

import argparse
import csv
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from threadpoolctl import threadpool_limits


def load_bundle(path):
    bundle = joblib.load(path)
    current_versions = {
        "numpy": np.__version__, "pandas": pd.__version__,
        "sklearn": sklearn.__version__, "joblib": joblib.__version__,
    }
    if "xgboost" in bundle["versions"]:
        import xgboost
        current_versions["xgboost"] = xgboost.__version__
    for package, version in current_versions.items():
        if bundle["versions"][package] != version:
            raise RuntimeError(f"Use recorded {package} version: {bundle['versions'][package]}")
    return bundle


def read_csv_features(path, feature_names):
    with Path(path).open(newline="", encoding="utf-8-sig") as file:
        header = next(csv.reader(file))
    if len(header) != len(set(header)):
        raise ValueError("CSV has duplicate column names.")
    data = pd.read_csv(path)
    missing = sorted(set(feature_names) - set(data.columns))
    extra = sorted(set(data.columns) - set(feature_names) - {"label"})
    if missing or extra or len(data.columns) != len(set(data.columns)):
        raise ValueError(f"CSV schema mismatch: missing={missing}, extra={extra}")
    features = data.loc[:, feature_names].astype(np.float64)
    features = features.replace([np.inf, -np.inf], np.nan)
    with np.errstate(over="ignore", invalid="ignore"):
        values = features.to_numpy(dtype=np.float32)
    if np.isinf(values).any():
        raise ValueError("Float32 conversion overflowed.")
    return values


def predict_bundle(bundle, values, batch_size=25000):
    if values.ndim != 2 or values.shape[1] != len(bundle["feature_names"]):
        raise ValueError("Unexpected input feature count/order.")
    expected_classes = np.arange(len(bundle["class_names"]))
    result = np.empty((len(values), len(expected_classes)), dtype=np.float32)
    with threadpool_limits(limits=bundle["threads"]):
        for start in range(0, len(values), batch_size):
            stop = min(start + batch_size, len(values))
            with np.errstate(over="ignore", invalid="ignore"):
                batch = np.asarray(values[start:stop], dtype=np.float32)
            if np.isinf(batch).any():
                raise ValueError("Input has Inf or float32 overflow.")
            transformed = bundle["preprocessor"].transform(batch).astype(np.float32, copy=False)
            if not np.isfinite(transformed).all():
                raise ValueError("Preprocessing produced NaN/Inf.")
            blocks = []
            for name in bundle["base_names"]:
                model = bundle["base_models"][name]
                if not np.array_equal(model.classes_, expected_classes):
                    raise ValueError("Unexpected base class order.")
                probabilities = model.predict_proba(transformed).astype(np.float32)
                blocks.append(probabilities)
            if bundle["kind"] == "base":
                probabilities = blocks[0]
            else:
                meta_input = np.concatenate(blocks, axis=1)
                model = bundle["meta_model"]
                if not np.array_equal(model.classes_, expected_classes):
                    raise ValueError("Unexpected meta class order.")
                probabilities = model.predict_proba(meta_input).astype(np.float32)
            if not np.isfinite(probabilities).all():
                raise ValueError("Non-finite probabilities.")
            if np.any(probabilities < 0) or np.any(probabilities > 1):
                raise ValueError("Probabilities outside [0, 1].")
            if not np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-5):
                raise ValueError("Probabilities do not sum to one.")
            result[start:stop] = probabilities
    return result


def predict_csv(bundle_path, input_path, output_path):
    bundle = load_bundle(bundle_path)
    values = read_csv_features(input_path, bundle["feature_names"])
    probabilities = predict_bundle(bundle, values)
    predicted = probabilities.argmax(axis=1)
    output = pd.DataFrame({"class_id": predicted})
    output["class_name"] = np.asarray(bundle["class_names"])[predicted]
    for class_id, class_name in enumerate(bundle["class_names"]):
        output[f"prob_{class_name}"] = probabilities[:, class_id]
    output.to_csv(output_path, index=False)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    predict_csv(args.bundle, args.input, args.output)
