"""Execute notebook helpers against synthetic data; never process/train the dataset locally.

Run: .venv/bin/python -m unittest discover -s notebook/tests -p 'test_test_upload_csv.py' -v
"""

import ast
import copy
import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / "notebook/ciciot2023-do-an-test-upload-csv.ipynb"
FROZEN_HELPER = ROOT / "output/integration_runs/integration_20261022_075217_0b67d48f/predict_csv.py"


def notebook_namespace():
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    namespace = {}
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            compile(source, cell["id"], "exec")
            if "export-library" in cell.get("metadata", {}).get("tags", []):
                exec(compile(source, cell["id"], "exec"), namespace)
    return namespace


class TestTestUploadCSV(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.output = self.root / "exports"
        self.ns = notebook_namespace()

    def make_source(self, rows=2001):
        rng = np.random.default_rng(42)
        self.values = rng.normal(size=(rows, 46)).astype(np.float32)
        # Include extreme values, subnormal values, missing cells, and source order.
        self.values[:, 0] = np.arange(rows, dtype=np.float32)
        self.values[0, 1:6] = [np.nan, np.finfo(np.float32).max, 1e-40, -0.0, -1e30]
        self.labels = (np.arange(rows) % 8).astype(np.uint8)
        np.save(self.source / "X_test_unprocessed.npy", self.values)
        np.save(self.source / "y_test.npy", self.labels)
        mapping = self.ns["CLASS_TO_ID"]
        schema = {
            "protocol": self.ns["PROTOCOL"], "preprocessing_fitted": False,
            "class_names": self.ns["CLASS_NAMES"], "class_to_id": mapping,
            "input_features": self.ns["FEATURE_NAMES"],
            "output_features": self.ns["FEATURE_NAMES"], "label_input_to_estimator": False,
        }
        config = {
            "protocol": self.ns["PROTOCOL"], "run_id": self.ns["EXPECTED_DATA_RUN_ID"],
            "preprocessing_fitted": False, "class_names": self.ns["CLASS_NAMES"],
            "class_to_id": mapping, "features": self.ns["FEATURE_NAMES"],
            "artifacts": {"test": {
                "input_file": "X_test_unprocessed.npy", "target_file": "y_test.npy",
                "shape": list(self.values.shape),
            }},
        }
        self.ns["write_json"](self.source / "feature_schema.json", schema)
        self.ns["write_json"](self.source / "preprocessing_config.json", config)
        self.ns["write_json"](self.source / "run_status.json", {
            "protocol": self.ns["PROTOCOL"], "run_id": self.ns["EXPECTED_DATA_RUN_ID"],
            "status": "complete",
        })
        (self.source / "feature_names.txt").write_text(
            "\n".join(self.ns["FEATURE_NAMES"]) + "\n", encoding="utf-8",
        )
        self.refresh_fixture_checksums()

    def refresh_fixture_checksums(self):
        manifest = {}
        for path in self.source.iterdir():
            if path.name not in {"checksums.json", "run_status.json"}:
                manifest[path.name] = self.ns["sha256_file"](path)
        self.ns["write_json"](self.source / "checksums.json", manifest)
        # Tests trust their synthetic fixture only, never change the notebook's pinned hash.
        self.ns["EXPECTED_MANIFEST_SHA256"] = self.ns["sha256_file"](self.source / "checksums.json")

    def export(self, **options):
        return self.ns["export_test_uploads"](self.source, self.output, **options)

    def test_notebook_clean_and_pins_match_frozen_source(self):
        notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
        self.assertEqual(notebook["nbformat_minor"], 5)
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                self.assertIsNone(cell["execution_count"])
                self.assertEqual(cell["outputs"], [])
        reference = json.loads((FROZEN_HELPER.parent / "input_schema.json").read_text())
        self.assertEqual(self.ns["FEATURE_NAMES"], reference["feature_names"])
        self.assertEqual(self.ns["CLASS_NAMES"], reference["class_names"])
        sources = json.loads((ROOT / "output/stacking_meta_runs/xgb_meta_20261021_092334_9024562d/source_artifacts.json").read_text())
        source = next(item for item in sources if item["category"] == "processing checksum manifest")
        self.assertEqual(self.ns["EXPECTED_MANIFEST_SHA256"], source["sha256"])

    def test_row_limits_remainder_and_backend_reader(self):
        # Execute the actual frozen helper's CSV reader without importing model loading code
        # or creating __pycache__ in the read-only artifact directories.
        tree = ast.parse(FROZEN_HELPER.read_text())
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "read_csv_features")
        backend_ns = {"Path": Path, "csv": csv, "pd": pd, "np": np}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(FROZEN_HELPER), "exec"), backend_ns)
        for count, expected_sizes in [(1, [1]), (1000, [1000]), (1001, [1000, 1]), (2001, [1000, 1000, 1])]:
            with self.subTest(count=count):
                self.make_source(count)
                directory, archive, manifest = self.export()
                self.assertEqual(manifest["rows"].tolist(), expected_sizes)
                for record in manifest.to_dict("records"):
                    path = directory / record["file"]
                    actual = backend_ns["read_csv_features"](path, self.ns["FEATURE_NAMES"])
                    np.testing.assert_array_equal(actual, self.values[record["test_start_row"]:record["test_stop_row_exclusive"]])
                    self.assertEqual(path.stat().st_size, record["bytes"])
                    self.assertEqual(self.ns["sha256_file"](path), record["sha256"])
                    self.assertLessEqual(path.stat().st_size, 10 * 1024 * 1024)
                with zipfile.ZipFile(archive) as bundle:
                    self.assertIsNone(bundle.testzip())
                    self.assertEqual(json.loads(bundle.read("run_status.json"))["status"], "complete")
                    self.assertEqual(len([name for name in bundle.namelist() if name.startswith("uploads/")]), len(expected_sizes))

    def test_without_labels_does_not_require_y_test(self):
        self.make_source(7)
        (self.source / "y_test.npy").unlink()
        directory, archive, manifest = self.export(include_label=False, create_zip=False)
        self.assertIsNone(archive)
        data = pd.read_csv(directory / manifest.iloc[0]["file"])
        self.assertEqual(data.columns.tolist(), self.ns["FEATURE_NAMES"])
        protocol = self.ns["read_json"](directory / "export_protocol.json")
        self.assertIsNone(protocol["source_label_counts"])
        self.assertNotIn("y_test.npy", protocol["source"]["verified_checksums"])

    def test_selected_range_retains_order_and_labels(self):
        self.make_source(25)
        directory, _, manifest = self.export(start_row=3, max_total_rows=11, rows_per_file=4)
        self.assertEqual(manifest["rows"].tolist(), [4, 4, 3])
        self.assertEqual(manifest["test_start_row"].tolist(), [3, 7, 11])
        self.assertEqual(manifest["test_stop_row_exclusive"].tolist(), [7, 11, 14])
        frames = [pd.read_csv(directory / name) for name in manifest["file"]]
        data = pd.concat(frames, ignore_index=True)
        self.assertEqual(data["flow_duration"].tolist(), list(range(3, 14)))
        self.assertEqual(data["label"].tolist(), [self.ns["CLASS_NAMES"][int(value)] for value in self.labels[3:14]])
        self.assertEqual(sum(self.ns["read_json"](directory / "export_protocol.json")["source_label_counts"].values()), 11)
        _, _, tail = self.export(start_row=23, max_total_rows=100)
        self.assertEqual(tail["rows"].tolist(), [2])

    def test_byte_boundary_counts_header_and_utf8(self):
        self.make_source(20)
        header_size = len(self.ns["csv_line"](self.ns["FEATURE_NAMES"] + ["label"]))
        row_sizes = []
        for index, row in enumerate(self.values):
            fields = ["" if np.isnan(value) else format(float(value), ".17g") for value in row]
            fields.append(self.ns["CLASS_NAMES"][int(self.labels[index])])
            row_sizes.append(len(self.ns["csv_line"](fields)))
        limit = header_size + max(row_sizes)
        directory, _, manifest = self.export(max_file_bytes=limit)
        self.assertEqual(manifest["bytes"].max(), limit)
        self.assertTrue((manifest["bytes"] <= limit).all())
        self.assertEqual(manifest["rows"].sum(), 20)
        self.assertGreater(len(manifest), 1)
        for name in manifest["file"]:
            self.assertLessEqual((directory / name).stat().st_size, limit)

    def test_failure_no_success_archive_or_complete_status(self):
        self.make_source(1002)
        # Invalid row beyond the first emitted part exercises failure after partial output.
        self.values[1001, 0] = np.inf
        np.save(self.source / "X_test_unprocessed.npy", self.values)
        self.refresh_fixture_checksums()
        with self.assertRaisesRegex(ValueError, "Inf"):
            self.export(rows_per_file=2)
        runs = list(self.output.glob("test_upload_*"))
        self.assertEqual(len(runs), 1)
        self.assertEqual(self.ns["read_json"](runs[0] / "run_status.json")["status"], "failed")
        self.assertTrue(list((runs[0] / "uploads").glob("*.csv")))
        self.assertFalse(list(self.output.glob("*.zip*")))

    def test_single_row_cannot_fit(self):
        self.make_source(1)
        with self.assertRaisesRegex(ValueError, "Một dòng"):
            self.export(max_file_bytes=10)
        self.assertFalse(list(self.output.glob("*.zip*")))

    def test_zip_failure_does_not_mark_complete(self):
        self.make_source(2)
        with patch.object(self.ns["zipfile"], "ZipFile", side_effect=OSError("archive disk full")):
            with self.assertRaisesRegex(OSError, "disk full"):
                self.export()
        run = next(self.output.glob("test_upload_*"))
        self.assertEqual(self.ns["read_json"](run / "run_status.json")["status"], "failed")
        self.assertFalse(list(self.output.glob("*.zip*")))

    def test_invalid_feature_shape_and_dtype(self):
        self.make_source(2)
        for values in [self.values.astype(np.float64), self.values[:, :-1], self.values.reshape(-1)]:
            np.save(self.source / "X_test_unprocessed.npy", values)
            self.refresh_fixture_checksums()
            with self.subTest(shape=values.shape, dtype=values.dtype), self.assertRaisesRegex(ValueError, "Shape/dtype"):
                self.export()
        self.assertFalse(self.output.exists())

    def test_bad_options(self):
        self.make_source(2)
        invalid = [
            {"rows_per_file": 1001}, {"rows_per_file": 0}, {"rows_per_file": True},
            {"max_file_bytes": 10 * 1024 * 1024 + 1}, {"max_file_bytes": 0},
            {"start_row": -1}, {"start_row": 2}, {"max_total_rows": 0},
            {"max_total_rows": 1.2}, {"include_label": "yes"}, {"create_zip": 1},
        ]
        for options in invalid:
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.export(**options)
        self.assertFalse(self.output.exists())

    def test_wrong_manifest_and_corrupt_data_rejected(self):
        self.make_source(2)
        original_pin = self.ns["EXPECTED_MANIFEST_SHA256"]
        self.ns["EXPECTED_MANIFEST_SHA256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "manifest"):
            self.export()
        self.ns["EXPECTED_MANIFEST_SHA256"] = original_pin
        with (self.source / "X_test_unprocessed.npy").open("ab") as stream:
            stream.write(b"corrupted")
        with self.assertRaisesRegex(ValueError, "Checksum"):
            self.export()
        self.assertFalse(self.output.exists())

    def test_wrong_source_contracts(self):
        self.make_source(2)
        config_path = self.source / "preprocessing_config.json"
        original = self.ns["read_json"](config_path)
        mutations = [
            ("run_id", "other"), ("protocol", "other"), ("preprocessing_fitted", True),
            ("features", list(reversed(self.ns["FEATURE_NAMES"]))),
            ("class_names", list(reversed(self.ns["CLASS_NAMES"]))),
        ]
        for key, value in mutations:
            changed = copy.deepcopy(original)
            changed[key] = value
            self.ns["write_json"](config_path, changed)
            self.refresh_fixture_checksums()
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.export()
        changed = copy.deepcopy(original)
        changed["artifacts"]["test"]["input_file"] = "X_train_unprocessed.npy"
        self.ns["write_json"](config_path, changed)
        self.refresh_fixture_checksums()
        with self.assertRaisesRegex(ValueError, "Chỉ cho phép"):
            self.export()
        self.ns["write_json"](config_path, original)
        self.refresh_fixture_checksums()
        status = self.ns["read_json"](self.source / "run_status.json")
        status["status"] = "in_progress"
        self.ns["write_json"](self.source / "run_status.json", status)
        with self.assertRaisesRegex(ValueError, "complete"):
            self.export()

    def test_label_shape_and_class_ids(self):
        self.make_source(4)
        np.save(self.source / "y_test.npy", self.labels[:2])
        self.refresh_fixture_checksums()
        with self.assertRaisesRegex(ValueError, "cùng số dòng"):
            self.export()
        self.labels[0] = 8
        np.save(self.source / "y_test.npy", self.labels)
        self.refresh_fixture_checksums()
        with self.assertRaisesRegex(ValueError, "0–7"):
            self.export()
        self.assertFalse(list(self.output.glob("*.zip*")))

    def test_discovery_refuses_other_or_ambiguous_run(self):
        self.make_source(1)
        self.assertEqual(self.ns["find_data_dir"](None, self.root), self.source)
        other = self.root / "duplicate"
        other.mkdir()
        (other / "preprocessing_config.json").write_bytes((self.source / "preprocessing_config.json").read_bytes())
        with self.assertRaisesRegex(ValueError, "đúng một"):
            self.ns["find_data_dir"](None, self.root)
        self.assertEqual(self.ns["find_data_dir"](self.source, self.root), self.source)
        (other / "preprocessing_config.json").unlink()
        config = self.ns["read_json"](self.source / "preprocessing_config.json")
        config["run_id"] = "wrong"
        self.ns["write_json"](self.source / "preprocessing_config.json", config)
        with self.assertRaisesRegex(ValueError, "đúng một"):
            self.ns["find_data_dir"](None, self.root)


if __name__ == "__main__":
    unittest.main()
