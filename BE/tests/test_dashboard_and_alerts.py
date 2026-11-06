import io
import json
import sqlite3
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from BE.config import CLASS_NAMES
from BE.main import create_app
from BE.storage import Store
from conftest import FakeGeminiClient, upload, wait_case, wait_run


def test_summary_filters_and_explanation_pages(client, settings):
    run_id = upload(client, (settings.integration_dir / "input_features.csv").read_bytes())
    wait_run(client, run_id)
    summary = client.get(f"/api/runs/{run_id}/summary").json()
    assert summary["prediction_status"] == "completed"
    assert summary["processed_rows"] == 50 and summary["pending_rows"] == 0
    assert list(summary["class_counts"]) == CLASS_NAMES
    assert sum(summary["class_counts"].values()) == 50
    assert summary["explanation_counts"]["not_requested"] == 50
    assert summary["gemini_counts"]["not_requested"] == 50
    assert summary["alert_counts"]["new"] == summary["suspected_attack_rows"]
    assert summary["normal_rows"] + summary["suspected_attack_rows"] == 50

    store = client.app.state.manager.store
    store.queue_explanation(run_id, 0, False)
    store.update_explanation(run_id, 0, "completed", "gemini_disabled")
    store.queue_explanation(run_id, 1, True)
    store.update_explanation(run_id, 1, "partial", "api_error")
    page = client.get(f"/api/runs/{run_id}/predictions", params={"explanation_status": "completed"}).json()
    assert page["total"] == 1 and page["total_predicted"] == 50
    assert page["items"][0]["row_index"] == 0
    assert page["items"][0]["gemini_status"] == "gemini_disabled"
    assert client.get(f"/api/runs/{run_id}/predictions?explanation_status=not_requested").json()["total"] == 48

    chosen = page["items"][0]["predicted_class"]
    filtered = client.get(f"/api/runs/{run_id}/predictions", params={"predicted_class": chosen, "limit": 1}).json()
    assert filtered["total"] == summary["class_counts"][chosen]
    assert filtered["total_predicted"] == 50 and len(filtered["items"]) == 1
    assert client.get(f"/api/runs/{run_id}/predictions?predicted_class=Unknown").status_code == 422

    page = client.get(f"/api/runs/{run_id}/explanations?offset=1&limit=1").json()
    assert page["total"] == 2 and len(page["items"]) == 1
    assert page["items"][0]["row_index"] == 1
    assert client.get(f"/api/runs/{run_id}/explanations?status=partial").json()["total"] == 1
    summary = client.get(f"/api/runs/{run_id}/summary").json()
    assert summary["prediction_status"] == "completed"
    assert summary["explanation_counts"]["partial"] == 1
    assert summary["explanation_counts"]["not_requested"] == 48
    assert summary["gemini_counts"]["api_error"] == 1
    assert client.get(f"/api/runs/{run_id}/summary?audience_level=basic").json()["explanation_counts"]["not_requested"] == 50
    assert client.get(f"/api/runs/{run_id}/explanations?audience_level=basic").json()["total"] == 0


def test_summary_during_paused_replay_and_resume(client, settings):
    content = pd.read_csv(settings.shap_dir / "selected_input.csv").head(3).to_csv(index=False).encode()
    run_id = upload(client, content, mode="replay", interval=60)
    deadline = time.monotonic() + 5
    while client.get(f"/api/runs/{run_id}").json()["processed_rows"] == 0:
        assert time.monotonic() < deadline
        time.sleep(0.01)
    client.post(f"/api/runs/{run_id}/control", json={"action": "pause"})
    summary = client.get(f"/api/runs/{run_id}/summary").json()
    assert summary["prediction_status"] == "paused"
    assert summary["processed_rows"] == 1 and summary["pending_rows"] == 2
    assert sum(summary["class_counts"].values()) == 1
    client.post(f"/api/runs/{run_id}/control", json={"action": "stop"})
    deadline = time.monotonic() + 3
    while client.app.state.manager.active_run is not None:
        assert time.monotonic() < deadline
        time.sleep(0.01)
    # Đổi nhịp trong fixture để không chờ 120 giây cho hai dòng còn lại.
    with client.app.state.manager.store.connect() as connection:
        connection.execute("UPDATE runs SET interval_seconds=0.05 WHERE id=?", (run_id,))
    client.post(f"/api/runs/{run_id}/control", json={"action": "resume"})
    wait_run(client, run_id)
    final = client.get(f"/api/runs/{run_id}/summary").json()
    assert final["processed_rows"] == 3
    alerts = client.get("/api/alerts", params={"run_id": run_id}).json()
    assert alerts["total"] == final["suspected_attack_rows"]
    pairs = [(row["run_id"], row["row_index"]) for row in alerts["items"]]
    assert len(pairs) == len(set(pairs))


def test_alert_lifecycle_history_and_export(client, settings):
    run_id = upload(client, (settings.shap_dir / "selected_input.csv").read_bytes())
    wait_run(client, run_id)
    alerts = client.get("/api/alerts", params={"run_id": run_id, "limit": 1}).json()
    assert alerts["total"] > 1 and len(alerts["items"]) == 1
    alert_id = alerts["items"][0]["id"]
    url = f"/api/alerts/{alert_id}"
    before = client.get(url).json()
    assert before["predicted_class"] != "Normal"
    assert before["history"][0]["actor"] == "system"
    assert before["playbook"]["class_name"] == before["predicted_class"]
    assert before["human_semantic_review"] == "user_review_available"
    assert client.get("/api/alerts?predicted_class=Normal").json()["total"] == 0
    assert client.patch(url, json={"status": "closed"}).status_code == 409
    assert client.patch(url, json={"status": "acknowledged"}, auth=("tester", "wrong")).status_code == 401
    acknowledged = client.patch(url, json={"status": "acknowledged", "note": "Đã tiếp nhận để kiểm tra."}).json()
    assert acknowledged["status"] == "acknowledged" and len(acknowledged["history"]) == 2
    assert acknowledged["history"][-1]["actor"] == "tester"
    assert client.patch(url, json={"status": "acknowledged"}).json()["history"] == acknowledged["history"]
    assert client.get("/api/alerts", params={"run_id": run_id, "status": "acknowledged"}).json()["total"] == 1
    assert client.patch(url, json={"status": "new"}).status_code == 409
    closed = client.patch(url, json={"status": "closed", "note": "Đã ghi nhận kết quả kiểm tra."}).json()
    assert closed["prediction"]["probabilities"] == before["prediction"]["probabilities"]
    assert closed["prediction"]["predicted_class"] == before["prediction"]["predicted_class"]
    assert closed["prediction"]["alert_status"] == "closed"
    assert closed["human_semantic_review"] == "user_review_available"
    reopened = client.patch(url, json={"status": "acknowledged"}).json()
    assert len(reopened["history"]) == 4 and reopened["status"] == "acknowledged"
    assert client.patch(url, json={"status": "closed", "note": "x" * 2001}).status_code == 422
    assert client.get("/api/alerts/999999").status_code == 404
    zipped = client.get(f"/api/runs/{run_id}/export?format=zip")
    with zipfile.ZipFile(io.BytesIO(zipped.content)) as archive:
        history = json.loads(archive.read("alert_history.json"))
        assert len(history[str(alert_id)]) == 4


def test_duplicate_concurrent_acknowledgements_do_not_duplicate_events(client, settings):
    run_id = upload(client, (settings.integration_dir / "input_features.csv").read_bytes())
    wait_run(client, run_id)
    store = client.app.state.manager.store
    alert_id = store.alert_page(run_id=run_id)["items"][0]["id"]
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(lambda _: store.update_alert(alert_id, "acknowledged", "Đã nhận.", "tester"), range(3)))
    assert all(results)
    assert len(store.alert(alert_id)["history"]) == 2


def test_legacy_database_migration_is_repeatable(tmp_path):
    path = tmp_path / "legacy.sqlite3"
    store = Store(path)
    run_id = "1" * 32
    store.create_run(run_id, "legacy.csv", "batch", 1, 2, "signature")
    store.save_prediction(run_id, 0, np.asarray([0, 1, 0, 0, 0, 0, 0, 0]), CLASS_NAMES, 0.1)
    store.save_prediction(run_id, 1, np.asarray([1, 0, 0, 0, 0, 0, 0, 0]), CLASS_NAMES, 0.1)
    predictions = store.predictions(run_id)
    with sqlite3.connect(path) as connection:
        connection.execute("DROP TABLE explanations")
        connection.execute("""CREATE TABLE explanations (
            run_id TEXT NOT NULL, row_index INTEGER NOT NULL, status TEXT NOT NULL,
            use_gemini INTEGER NOT NULL, gemini_status TEXT NOT NULL,
            message TEXT NOT NULL, updated_at TEXT NOT NULL, PRIMARY KEY(run_id,row_index)
        )""")
        connection.execute("INSERT INTO explanations VALUES(?,0,'completed',1,'accepted','','2026-10-27')", (run_id,))
        connection.execute("DROP TABLE alert_events")
        connection.execute("DROP TABLE alerts")
    migrated = Store(path)
    assert migrated.predictions(run_id) == predictions
    assert migrated.explanation(run_id, 0)["gemini_status"] == "accepted"
    assert migrated.explanation(run_id, 0, "basic") is None
    alert = migrated.alert_page()["items"][0]
    assert migrated.alert_page()["total"] == 1
    migrated.update_alert(alert["id"], "acknowledged", "Giữ lịch sử.", "tester")
    migrated.queue_explanation(run_id, 0, False, "basic")
    migrated.update_explanation(run_id, 0, "completed", "gemini_disabled", audience_level="basic")
    restarted = Store(path)
    assert restarted.alert_page()["total"] == 1
    assert len(restarted.alert(alert["id"])["history"]) == 2
    assert restarted.alert(alert["id"])["status"] == "acknowledged"
    assert restarted.explanation(run_id, 0)["gemini_status"] == "accepted"
    assert restarted.explanation(run_id, 0, "basic")["gemini_status"] == "gemini_disabled"


def test_playbooks_available_without_gemini(client):
    for class_name in CLASS_NAMES:
        response = client.get(f"/api/playbooks/{class_name}")
        assert response.status_code == 200
        book = response.json()
        assert book["class_name"] == class_name and book["automatic_actions"] is False
        assert book["sources"] and book["checks"] and book["response_steps"]
        assert all(source["url"].startswith("https://") for source in book["sources"])
        assert "chưa xác nhận" in book["scope_note"].lower()
    assert client.get("/api/playbooks/Unknown").status_code == 422
    assert client.get("/api/playbooks/Normal", auth=("tester", "wrong")).status_code == 401


def test_failed_schema_migration_rolls_back_original_data(tmp_path, monkeypatch):
    path = tmp_path / "rollback.sqlite3"
    store = Store(path)
    run_id = "2" * 32
    store.create_run(run_id, "old.csv", "batch", 1, 1, "signature")
    with sqlite3.connect(path) as connection:
        connection.execute("DROP TABLE explanations")
        connection.execute("""CREATE TABLE explanations (
            run_id TEXT, row_index INTEGER, status TEXT, use_gemini INTEGER,
            gemini_status TEXT, message TEXT, updated_at TEXT, PRIMARY KEY(run_id,row_index)
        )""")
        connection.execute("INSERT INTO explanations VALUES(?,0,'completed',1,'accepted','','2026-10-27')", (run_id,))
    migrate = Store.migrate_explanations

    def fail_after_copy(self, connection):
        migrate(self, connection)
        raise ValueError("Mô phỏng lỗi sau khi sao chép dữ liệu.")

    monkeypatch.setattr(Store, "migrate_explanations", fail_after_copy)
    with pytest.raises(ValueError):
        Store(path)
    with sqlite3.connect(path) as connection:
        columns = [row[1] for row in connection.execute("PRAGMA table_info(explanations)")]
        assert "audience_level" not in columns
        assert connection.execute("SELECT gemini_status FROM explanations").fetchone()[0] == "accepted"
        assert connection.execute("SELECT name FROM sqlite_master WHERE name='explanations_legacy'").fetchone() is None


def test_two_audiences_have_separate_cache_and_share_shap(settings, model_runtime):
    fake = FakeGeminiClient()
    with TestClient(create_app(settings, model_runtime, fake)) as client:
        client.auth = ("tester", "test-password")
        run_id = upload(client, (settings.shap_dir / "selected_input.csv").read_bytes())
        wait_run(client, run_id)
        url = f"/api/runs/{run_id}/explanations"
        assert client.post(url, json={"row_indices": [14]}).status_code == 202
        technical = wait_case(client, run_id, 14)
        manager = client.app.state.manager
        shared = manager.case_dir(run_id, 14)
        original_shap_time = (shared / "shap_values.npz").stat().st_mtime_ns
        original_gemini = (shared / "explanation_vi.json").read_bytes()
        request = {"row_indices": [14], "audience_level": "basic"}
        assert client.post(url, json=request).status_code == 202
        basic = wait_case(client, run_id, 14, audience_level="basic")
        assert technical["gemini_status"] == basic["gemini_status"] == "accepted"
        assert basic["audience_level"] == "basic"
        assert technical["explanation"] == basic["explanation"]
        assert len(fake.calls) == 2 and "DỄ HIỂU" in fake.calls[1] and "DỄ HIỂU" not in fake.calls[0]
        assert (shared / "shap_values.npz").stat().st_mtime_ns == original_shap_time
        assert (shared / "explanation_vi.json").read_bytes() == original_gemini
        basic_dir = manager.explanation_dir(run_id, 14, "basic")
        hashes = [json.loads((p / "gemini_response_01.json").read_text())["request_sha256"] for p in [shared, basic_dir]]
        assert hashes[0] != hashes[1]
        for name in ["report_vi.md", "waterfall.png", "playbook.json"]:
            assert client.get(basic["files"][name]).status_code == 200
        assert "Dễ hiểu" in client.get(basic["files"]["report_vi.md"]).text
        assert client.post(url, json=request).status_code == 202 and len(fake.calls) == 2
        request["retry_gemini"] = True
        assert client.post(url, json=request).status_code == 202
        assert wait_case(client, run_id, 14, audience_level="basic")["gemini_status"] == "accepted"
        assert len(fake.calls) == 3
        assert list((basic_dir / "previous_gemini").iterdir())
        assert not (shared / "previous_gemini").exists()
        assert (shared / "shap_values.npz").stat().st_mtime_ns == original_shap_time
        assert (shared / "explanation_vi.json").read_bytes() == original_gemini
        assert client.get(f"{url}?audience_level=basic").json()["total"] == 1
        assert client.post(url, json={"row_indices": [14], "audience_level": "../other"}).status_code == 422
        with zipfile.ZipFile(io.BytesIO(client.get(f"/api/runs/{run_id}/export?format=zip").content)) as archive:
            assert "cases/row_0014/report_vi.md" in archive.namelist()
            assert "cases/row_0014/audiences/basic/report_vi.md" in archive.namelist()
            assert "cases/row_0014/audiences/basic/waterfall.png" in archive.namelist()
        assert client.get("/api/model").json()["model_load_count"] == 1


def test_basic_only_does_not_replace_technical_state(client, settings):
    run_id = upload(client, (settings.integration_dir / "input_features.csv").read_bytes())
    wait_run(client, run_id)
    url = f"/api/runs/{run_id}/explanations"
    response = client.post(url, json={"row_indices": [0], "audience_level": "basic"})
    assert response.status_code == 202
    basic = wait_case(client, run_id, 0, audience_level="basic")
    assert basic["gemini_status"] == "not_configured" and basic["playbook"]
    assert client.get(f"{url}/0").status_code == 404
    summary = client.get(f"/api/runs/{run_id}/summary?audience_level=basic").json()
    assert summary["explanation_counts"]["partial"] == 1
    assert summary["explanation_counts"]["not_requested"] == 49
    assert client.get(f"/api/runs/{run_id}/summary").json()["explanation_counts"]["not_requested"] == 50
    report = client.get(basic["files"]["report_vi.md"]).text
    assert "Hướng dẫn tham khảo do chương trình" in report
