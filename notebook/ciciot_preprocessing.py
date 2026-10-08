"""Helpers embedded in the processing notebook and exported with its artifacts."""
from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler, StandardScaler

CLASS_NAMES = [
    "Normal", "BruteForce", "DDoS", "DoS", "Mirai", "Recon", "Spoofing", "Web-Based"
]
CLASS_TO_ID = {name: i for i, name in enumerate(CLASS_NAMES)}
RAW_FEATURES = [
    "flow_duration", "Header_Length", "Protocol Type", "Duration", "Rate", "Srate",
    "Drate", "fin_flag_number", "syn_flag_number", "rst_flag_number", "psh_flag_number",
    "ack_flag_number", "ece_flag_number", "cwr_flag_number", "ack_count", "syn_count",
    "fin_count", "urg_count", "rst_count", "HTTP", "HTTPS", "DNS", "Telnet", "SMTP",
    "SSH", "IRC", "TCP", "UDP", "DHCP", "ARP", "ICMP", "IPv", "LLC", "Tot sum",
    "Min", "Max", "AVG", "Std", "Tot size", "IAT", "Number", "Magnitue", "Radius",
    "Covariance", "Variance", "Weight",
]
LABEL_GROUPS = {
    "Normal": ["BenignTraffic"],
    "BruteForce": ["DictionaryBruteForce"],
    "DDoS": [
        "DDoS-ICMP_Flood", "DDoS-UDP_Flood", "DDoS-TCP_Flood", "DDoS-PSHACK_Flood",
        "DDoS-SYN_Flood", "DDoS-RSTFINFlood", "DDoS-SynonymousIP_Flood",
        "DDoS-ICMP_Fragmentation", "DDoS-UDP_Fragmentation", "DDoS-ACK_Fragmentation",
        "DDoS-HTTP_Flood", "DDoS-SlowLoris",
    ],
    "DoS": ["DoS-UDP_Flood", "DoS-TCP_Flood", "DoS-SYN_Flood", "DoS-HTTP_Flood"],
    "Mirai": ["Mirai-greeth_flood", "Mirai-udpplain", "Mirai-greip_flood"],
    "Recon": [
        "Recon-HostDiscovery", "Recon-OSScan", "Recon-PortScan", "Recon-PingSweep",
        "VulnerabilityScan",
    ],
    "Spoofing": ["MITM-ArpSpoofing", "DNS_Spoofing"],
    "Web-Based": [
        "BrowserHijacking", "CommandInjection", "SqlInjection", "XSS",
        "Backdoor_Malware", "Uploading_Attack",
    ],
}
RAW_TO_CLASS = {label: group for group, labels in LABEL_GROUPS.items() for label in labels}
# Continuous metrics only: do not select protocol codes/TTL/flags by skewness alone.
LOG_CANDIDATES = [
    "flow_duration", "Header_Length", "Rate", "Srate", "Drate", "Tot sum", "Min",
    "Max", "AVG", "Std", "Tot size", "IAT", "Number", "Magnitue", "Radius",
    "Covariance", "Variance", "Weight",
]


def write_json(path, value):
    Path(path).write_text(
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8"
    )


def encode_labels(labels):
    labels = pd.Series(labels).astype("string").str.strip()
    if labels.isna().any() or labels.eq("").any():
        raise ValueError("Missing/empty target label; do not impute target labels.")
    categories = labels.map(RAW_TO_CLASS)
    if categories.isna().any():
        unknown = labels[categories.isna()].value_counts().to_dict()
        raise ValueError(f"Unknown CICIoT2023 labels: {unknown}")
    return categories.map(CLASS_TO_ID).to_numpy(dtype=np.int8)


def class_support(y):
    counts = np.bincount(np.asarray(y, dtype=np.int64), minlength=8)
    return {name: int(counts[i]) for i, name in enumerate(CLASS_NAMES)}


def load_split(path, features=RAW_FEATURES):
    """Keep float64 through raw audit/dedup; cast only when exporting model input."""
    path = Path(path)
    columns = pd.read_csv(path, nrows=0).columns.tolist()
    expected = set(features) | {"label"}
    if len(columns) != len(expected) or set(columns) != expected:
        raise ValueError(
            f"Schema mismatch in {path}: missing={expected-set(columns)}, "
            f"extra={set(columns)-expected}, columns={columns}"
        )
    frame = pd.read_csv(path, dtype={**{f: "float64" for f in features}, "label": "string"})
    if frame.empty:
        raise ValueError(f"Empty split: {path}")
    # Stable source-row identity, even after removing rows.
    frame.insert(0, "source_row", np.arange(len(frame), dtype=np.int64))
    y = encode_labels(frame["label"])
    frame["y_encoded"] = y
    frame["label"] = frame["label"].str.strip().astype("category")
    missing = {}; infinite = {}
    for col in features:
        values = frame[col].to_numpy()
        missing[col] = int(np.isnan(values).sum())
        mask = np.isinf(values)
        infinite[col] = int(mask.sum())
        if mask.any():
            frame.loc[mask, col] = np.nan
        # Canonicalize signed zero for consistent duplicate fingerprints.
        frame.loc[frame[col].eq(0), col] = 0.0
    quality = {
        "rows_loaded": len(frame), "nan_before": missing, "inf_before": infinite,
        "support_before": class_support(y), "source_bytes": path.stat().st_size,
    }
    return frame, quality


def row_fingerprints(matrix, feature_names):
    """64-bit fingerprints of actual tree model input; collisions remain a limitation."""
    if matrix.ndim != 2 or matrix.shape[1] != len(feature_names):
        raise ValueError("Fingerprint matrix/schema mismatch")
    return pd.util.hash_pandas_object(
        pd.DataFrame(matrix, columns=feature_names), index=False
    ).to_numpy(dtype=np.uint64)


def conflict_summary(hashes, y):
    """Do not choose labels by majority vote or use held-out labels to edit train."""
    pairs = pd.DataFrame({"hash": hashes, "class_id": np.asarray(y)})
    unique_pairs = pairs.drop_duplicates()
    counts = unique_pairs.groupby("hash", sort=False).size()
    conflicting = counts[counts > 1].index.to_numpy(dtype=np.uint64)
    return {
        "feature_groups_with_multiple_8class_labels": len(conflicting),
        "rows_in_conflicting_groups": int(np.isin(hashes, conflicting).sum()),
        "policy": "retain_and_report_ambiguous_training_samples",
    }


def overlap_mask(hashes, earlier_hashes):
    return np.isin(hashes, earlier_hashes, assume_unique=False)


class CICPreprocessor:
    """Train-fitted schema, medians, optional log and scaler, usable for inference.

    transform_tree keeps original units after imputation/constant-column removal.
    transform_linear optionally logs selected continuous columns, then scales.
    Both methods return float32 and reject overflow rather than exporting Inf.
    """

    def __init__(self, features=RAW_FEATURES, drop_constant=True, use_log=False,
                 scaling="standard", skew_threshold=2.0, batch_size=100_000):
        self.raw_features = list(features)
        self.drop_constant = drop_constant
        self.use_log = use_log
        self.scaling = scaling
        self.skew_threshold = skew_threshold
        self.batch_size = batch_size

    def _check_schema(self, frame):
        missing = set(self.raw_features) - set(frame.columns)
        if missing:
            raise ValueError(f"Missing raw features: {sorted(missing)}")
        non_numeric = [c for c in self.raw_features if not pd.api.types.is_numeric_dtype(frame[c])]
        if non_numeric:
            raise ValueError(f"Non-numeric features: {non_numeric}")

    def _imputed_array(self, frame, features):
        self._check_schema(frame)
        result = np.empty((len(frame), len(features)), dtype=np.float64)
        for i, col in enumerate(features):
            values = frame[col].to_numpy(dtype=np.float64, copy=True)
            values[~np.isfinite(values)] = self.medians_[col]
            values[values == 0] = 0.0
            result[:, i] = values
        return result

    def _log_array(self, values):
        for index in self.log_indices_:
            if (values[:, index] < 0).any():
                raise ValueError(
                    f"Negative values in log feature {self.feature_names_[index]}; "
                    "do not silently clip them to zero. Correct data or disable log and refit."
                )
            values[:, index] = np.log1p(values[:, index])
        return values

    def fit(self, train):
        if self.scaling not in {"standard", "robust", "none"}:
            raise ValueError("scaling must be standard, robust or none")
        if self.batch_size < 1 or len(train) == 0:
            raise ValueError("Training rows and batch_size must be positive")
        self._check_schema(train)
        self.medians_ = {}; self.constant_features_ = []; self.empty_features_ = []
        self.log_features_ = []; self.training_stats_ = []
        for col in self.raw_features:
            clean = train[col].replace([np.inf, -np.inf], np.nan)
            if clean.isna().all():
                self.empty_features_.append(col)
                median = 0.0  # Explicit fallback, recorded in metadata.
            else:
                median = float(clean.median())
            self.medians_[col] = median
            clean = clean.fillna(median)
            unique = int(clean.nunique())
            if unique <= 1:
                self.constant_features_.append(col)
            q1, q3 = clean.quantile([0.25, 0.75]).to_numpy()
            iqr = q3-q1
            skew = float(clean.skew())
            skew = skew if np.isfinite(skew) else None
            self.training_stats_.append({
                "feature": col, "median": median, "unique": unique,
                "skewness": skew, "iqr": float(iqr), "min": float(clean.min()),
                "max": float(clean.max()),
                "iqr_outside_pct": float(((clean < q1-1.5*iqr) | (clean > q3+1.5*iqr)).mean()*100),
            })
            if (self.use_log and col in LOG_CANDIDATES and unique > 2
                    and skew is not None and skew > self.skew_threshold and clean.min() >= 0):
                self.log_features_.append(col)
        self.feature_names_ = [
            c for c in self.raw_features
            if not self.drop_constant or c not in self.constant_features_
        ]
        if not self.feature_names_:
            raise ValueError("No features remain after constant-column removal")
        self.log_features_ = [c for c in self.log_features_ if c in self.feature_names_]
        self.log_indices_ = [self.feature_names_.index(c) for c in self.log_features_]
        self.scaler_ = None
        if self.scaling == "standard":
            self.scaler_ = StandardScaler()
            for start in range(0, len(train), self.batch_size):
                part = train.iloc[start:start+self.batch_size]
                self.scaler_.partial_fit(self._log_array(self._imputed_array(part, self.feature_names_)))
        elif self.scaling == "robust":
            warnings.warn("RobustScaler fit uses the entire training matrix and needs more RAM.")
            self.scaler_ = RobustScaler().fit(
                self._log_array(self._imputed_array(train, self.feature_names_))
            )
        return self

    @staticmethod
    def _float32_finite(values):
        with np.errstate(over="ignore", invalid="ignore"):
            result = values.astype(np.float32)
        if not np.isfinite(result).all():
            raise ValueError("Non-finite/float32 overflow in model input; inspect data before training.")
        return result

    def transform_tree(self, frame):
        return self._float32_finite(self._imputed_array(frame, self.feature_names_))

    def transform_linear(self, frame):
        values = self._log_array(self._imputed_array(frame, self.feature_names_))
        if self.scaler_ is not None:
            values = self.scaler_.transform(values)
        return self._float32_finite(values)

    def metadata(self):
        return {
            "raw_features": self.raw_features, "final_features": self.feature_names_,
            "drop_constant": self.drop_constant, "constant_features": self.constant_features_,
            "all_missing_train_features": self.empty_features_, "all_missing_fallback": 0.0,
            "imputer_medians": self.medians_, "linear_log_enabled": self.use_log,
            "linear_log_features": self.log_features_, "linear_scaling": self.scaling,
            "tree_scaling": "none", "output_dtype": "float32",
            "fit_split": "train_only", "batch_size": self.batch_size,
            "skew_threshold": self.skew_threshold,
        }
