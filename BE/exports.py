"""Xuất snapshot kết quả đã hoàn thành, không lấy file bí mật của server."""

import io
import json
import tempfile
import zipfile
from pathlib import Path

import pandas as pd


SHAP_FILES = {"waterfall.png", "explanation.json", "shap_values.npz", "top5_features.csv"}
CASE_FILES = SHAP_FILES | {
    "report_vi.md", "playbook.json", "llm_input.json", "explanation_vi.json",
    "explanation_vi_draft.json", "gemini_status.json", "execution.json",
}


def case_file(manager, run_id, row_index, filename, audience_level="technical"):
    if filename in SHAP_FILES:
        return manager.case_dir(run_id, row_index) / filename
    return manager.explanation_dir(run_id, row_index, audience_level) / filename


def prediction_csv(manager, run_id):
    records = manager.store.predictions(run_id)
    rows = []
    for record in records:
        row = {
            "row_index": record["row_index"], "predicted_class": record["predicted_class"],
            "predicted_probability": record["predicted_probability"],
            "predict_seconds": record["predict_seconds"], "created_at": record["created_at"],
        }
        for name in manager.runtime.class_names:
            row[f"prob_{name}"] = record["probabilities"][name]
        rows.append(row)
    columns = ["row_index", "predicted_class", "predicted_probability", "predict_seconds", "created_at"]
    columns.extend(f"prob_{name}" for name in manager.runtime.class_names)
    stream = io.StringIO()
    pd.DataFrame(rows, columns=columns).to_csv(stream, index=False)
    return stream.getvalue()


def report_zip(manager, run_id):
    directory = manager.settings.runtime_dir / "exports"
    directory.mkdir(exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=directory, suffix=".zip", delete=False) as stream:
        output_path = Path(stream.name)
    try:
        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("predictions.csv", prediction_csv(manager, run_id))
            archive.writestr(
                "run_status.json", json.dumps(manager.store.get_run(run_id), ensure_ascii=False, indent=2)
            )
            for name in ["protocol.json", "input_features.csv"]:
                archive.write(manager.run_dir(run_id) / name, arcname=name)
            states = manager.store.explanations(run_id)
            archive.writestr("explanations.json", json.dumps(states, ensure_ascii=False, indent=2))
            alerts = manager.store.alert_page(run_id=run_id, limit=manager.settings.max_input_rows)["items"]
            archive.writestr("alerts.json", json.dumps(alerts, ensure_ascii=False, indent=2))
            history = {str(alert["id"]): manager.store.alert(alert["id"])["history"] for alert in alerts}
            archive.writestr("alert_history.json", json.dumps(history, ensure_ascii=False, indent=2))
            reviews = manager.store.human_reviews(run_id)
            archive.writestr("human_reviews.json", json.dumps(reviews, ensure_ascii=False, indent=2))
            for state in states:
                if state["status"] not in ["completed", "partial"]:
                    continue
                case_dir = manager.explanation_dir(run_id, state["row_index"], state["audience_level"])
                relative_dir = case_dir.relative_to(manager.run_dir(run_id))
                for name in sorted(CASE_FILES):
                    path = case_file(manager, run_id, state["row_index"], name, state["audience_level"])
                    if path.is_file():
                        archive.write(path, arcname=f"{relative_dir}/{name}")
        return output_path
    except Exception:
        output_path.unlink(missing_ok=True)
        raise
