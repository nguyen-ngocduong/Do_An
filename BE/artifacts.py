"""Nạp model/background một lần và kiểm chứng với kết quả Kaggle."""

import importlib.metadata
import importlib.util
import platform
import shutil
import threading

import numpy as np
import pandas as pd

from BE.config import BASE_NAMES, CLASS_NAMES, MODEL_ID, SHAP_RUN_ID, XGB_RUN_ID
from BE.utils import json_hash, read_json, sha256_file, write_json


def verify_file(root, manifest, name):
    path = root / name
    expected = manifest.get(name)
    if not isinstance(expected, str) or not path.is_file():
        raise ValueError(f"Thiếu artifact hoặc checksum: {name}")
    if sha256_file(path) != expected:
        raise ValueError(f"Checksum artifact không khớp: {name}")
    return path


class ModelRuntime:
    def __init__(self, settings):
        self.settings = settings
        self.lock = threading.Lock()
        self.load_count = 0
        self.ready = False
        settings.runtime_dir.mkdir(parents=True, exist_ok=True)

        xgb_manifest = read_json(settings.xgb_dir / "output_checksums.json")
        shap_manifest = read_json(settings.shap_dir / "output_checksums.json")
        integration_manifest = read_json(settings.integration_dir / "output_checksums.json")
        verify_file(settings.xgb_dir, xgb_manifest, "protocol.json")
        verify_file(settings.xgb_dir, xgb_manifest, "frozen_candidates.json")
        verify_file(settings.shap_dir, shap_manifest, "protocol.json")
        verify_file(settings.integration_dir, integration_manifest, "protocol.json")
        source = read_json(settings.xgb_dir / "protocol.json")
        self.shap_protocol = read_json(settings.shap_dir / "protocol.json")
        integration = read_json(settings.integration_dir / "protocol.json")
        freeze = read_json(settings.xgb_dir / "frozen_candidates.json")
        source_status = read_json(settings.xgb_dir / "run_status.json")
        shap_status = read_json(settings.shap_dir / "run_status.json")
        if source.get("protocol") != "stacking_xgb_meta_v1" or source.get("run_id") != XGB_RUN_ID:
            raise ValueError("Không đúng run XGBoost đã chốt.")
        if self.shap_protocol.get("protocol") != "stacking_shap_local_v1":
            raise ValueError("Protocol SHAP không được hỗ trợ.")
        if source_status.get("status") != "complete" or source_status.get("run_id") != XGB_RUN_ID:
            raise ValueError("Run XGBoost chưa hoàn tất hoặc sai run ID.")
        if shap_status.get("status") != "complete" or shap_status.get("run_id") != SHAP_RUN_ID:
            raise ValueError("Run SHAP chưa hoàn tất hoặc sai run ID.")
        if integration["source_xgb_run_id"] != XGB_RUN_ID or integration["source_shap_run_id"] != SHAP_RUN_ID:
            raise ValueError("Run tích hợp không cùng nguồn model/SHAP.")
        if self.shap_protocol["source_xgb_run_id"] != XGB_RUN_ID:
            raise ValueError("Background không thuộc model được chọn.")
        if self.shap_protocol["data_run_id"] != source["data_run_id"]:
            raise ValueError("Model và SHAP khác data run.")
        if freeze["primary_candidate_id"] != MODEL_ID:
            raise ValueError("Model được freeze khác cấu hình BE.")
        if integration["source_protocol_sha256"] != sha256_file(settings.xgb_dir / "protocol.json"):
            raise ValueError("Protocol nguồn khác run tích hợp.")

        # Kiểm tra phiên bản trước khi giải tuần tự hóa sklearn objects.
        self.versions = {"python": platform.python_version()}
        package_names = {
            "numpy": "numpy", "pandas": "pandas", "sklearn": "scikit-learn",
            "joblib": "joblib", "xgboost": "xgboost", "shap": "shap",
            "matplotlib": "matplotlib", "google-genai": "google-genai",
        }
        for key, package in package_names.items():
            actual = importlib.metadata.version(package)
            self.versions[key] = actual
            if actual != integration["versions"][key]:
                raise ValueError(f"Cần {package}=={integration['versions'][key]}; hiện tại {actual}.")
        if platform.python_version().split(".")[:2] != source["versions"]["python"].split(".")[:2]:
            raise ValueError("Dùng cùng phiên bản Python major/minor với run nguồn.")

        record = next(row for row in freeze["candidates"] if row["candidate_id"] == MODEL_ID)
        bundle_path = verify_file(settings.xgb_dir, xgb_manifest, record["bundle_file"])
        if record["sha256"] != xgb_manifest[record["bundle_file"]]:
            raise ValueError("Checksum bundle khác frozen selection.")
        if record["sha256"] != integration["bundle_sha256"]:
            raise ValueError("Bundle khác run tích hợp.")
        self.bundle_sha256 = record["sha256"]
        helper_path = verify_file(settings.xgb_dir, xgb_manifest, "predict_csv.py")
        # Import bản sao trong runtime, tránh tạo __pycache__ ở output nguồn.
        local_helper = settings.runtime_dir / "source_predict_csv.py"
        shutil.copyfile(helper_path, local_helper)
        spec = importlib.util.spec_from_file_location("datn_source_prediction", local_helper)
        self.helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.helper)
        self.bundle = self.helper.load_bundle(bundle_path)
        self.load_count += 1
        self.bundle["threads"] = settings.threads
        if self.bundle["candidate_id"] != MODEL_ID or self.bundle["kind"] != "stacking":
            raise ValueError("Bundle không đúng stacking được chọn.")
        if self.bundle["base_names"] != BASE_NAMES or self.bundle["class_names"] != CLASS_NAMES:
            raise ValueError("Thứ tự base models/lớp không khớp.")
        if self.bundle["meta_model"].__class__.__name__ != "XGBClassifier":
            raise ValueError("Meta-model không phải XGBClassifier.")
        self.feature_names = list(self.bundle["feature_names"])
        self.class_names = list(CLASS_NAMES)
        if len(self.feature_names) != 46 or len(set(self.feature_names)) != 46:
            raise ValueError("Bundle phải có 46 đặc trưng gốc không lặp.")
        if self.feature_names != self.shap_protocol["features"]:
            raise ValueError("Thứ tự đặc trưng của bundle và SHAP khác nhau.")
        if self.shap_protocol["class_names"] != CLASS_NAMES:
            raise ValueError("Thứ tự lớp SHAP không khớp.")

        for name in ["background.npy", "background_probabilities.csv", "model_reference.json",
                     "selected_input.csv", "golden_predictions.csv"]:
            verify_file(settings.shap_dir, shap_manifest, name)
        reference = read_json(settings.shap_dir / "model_reference.json")
        if reference["bundle_sha256"] != self.bundle_sha256:
            raise ValueError("SHAP tham chiếu bundle khác.")
        self.background = np.load(settings.shap_dir / "background.npy", allow_pickle=False)
        expected_shape = (self.shap_protocol["background_size"], len(self.feature_names))
        if self.background.dtype != np.float32 or self.background.shape != expected_shape:
            raise ValueError("Background sai dtype hoặc kích thước.")
        if np.isinf(self.background).any():
            raise ValueError("Background chứa Inf.")

        for name in ["input_schema.json", "system_prompt.txt", "generation_config.json", "check_guide.json"]:
            verify_file(settings.integration_dir, integration_manifest, name)
        self.input_schema = read_json(settings.integration_dir / "input_schema.json")
        if self.input_schema["feature_names"] != self.feature_names:
            raise ValueError("Schema đầu vào không khớp bundle.")
        if self.input_schema["class_names"] != CLASS_NAMES:
            raise ValueError("Schema đầu vào khác thứ tự lớp.")
        self.generation_config = read_json(settings.integration_dir / "generation_config.json")
        self.check_guide = read_json(settings.integration_dir / "check_guide.json")
        system_prompt = (settings.integration_dir / "system_prompt.txt").read_text(encoding="utf-8")
        if system_prompt != self.generation_config["system_instruction"]:
            raise ValueError("System prompt và cấu hình Gemini không khớp.")

        golden_values = self.read_csv(settings.shap_dir / "selected_input.csv")
        expected = pd.read_csv(settings.shap_dir / "golden_predictions.csv")
        actual = self.predict(golden_values)
        columns = [f"prob_{name}" for name in CLASS_NAMES]
        np.testing.assert_allclose(actual, expected[columns].to_numpy(), rtol=1e-6, atol=1e-7)
        np.testing.assert_array_equal(actual.argmax(axis=1), expected["class_id"].to_numpy())
        self.background_probabilities = self.predict(self.background).astype(np.float64).mean(axis=0)
        background_expected = pd.read_csv(settings.shap_dir / "background_probabilities.csv")
        if background_expected["Class"].tolist() != CLASS_NAMES:
            raise ValueError("Xác suất nền khác thứ tự lớp.")
        np.testing.assert_allclose(
            self.background_probabilities, background_expected["Base probability"].to_numpy(),
            rtol=0, atol=self.shap_protocol["additivity_tolerance"],
        )
        self.signature = json_hash({
            "bundle": self.bundle_sha256, "background": shap_manifest["background.npy"],
            "shap_protocol": shap_manifest["protocol.json"],
            "generation_config": integration_manifest["generation_config.json"],
            "check_guide": integration_manifest["check_guide.json"],
            "gemini_model": settings.gemini_model,
        })
        self.checks = {
            "bundle_sha256": self.bundle_sha256, "golden_rows": len(golden_values),
            "golden_prediction_match": True, "background_probability_match": True,
            "versions": self.versions, "signature": self.signature,
        }
        write_json(settings.runtime_dir / "startup_checks.json", self.checks)
        self.ready = True

    def read_csv(self, path):
        try:
            preview = pd.read_csv(path, nrows=self.settings.max_input_rows + 1)
            if not 1 <= len(preview) <= self.settings.max_input_rows:
                raise ValueError(f"CSV phải có 1–{self.settings.max_input_rows} dòng.")
            return self.helper.read_csv_features(path, self.feature_names)
        except (ValueError, TypeError, UnicodeError, StopIteration) as error:
            raise ValueError(f"CSV không hợp lệ: {error}") from None

    def predict(self, values):
        # Cả worker dự đoán và SHAP gọi cùng hàm, không nạp lại model.
        with self.lock:
            return self.helper.predict_bundle(self.bundle, values, self.settings.prediction_batch_size)
