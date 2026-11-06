import sqlite3
import threading
import time

import pandas as pd
import pytest

from BE.jobs import RequestConflict
from conftest import upload, wait_case, wait_run


def sample_csv(settings):
    return pd.read_csv(settings.shap_dir / "selected_input.csv").head(4).to_csv(index=False).encode()


def wait_idle(manager):
    deadline = time.monotonic() + 10
    while manager.active_run is not None or manager.pending_cases:
        assert time.monotonic() < deadline
        time.sleep(0.02)


def test_delete_removes_children_files_and_keeps_other_runs(client, settings):
    manager = client.app.state.manager
    run_id = upload(client, sample_csv(settings))
    wait_run(client, run_id)
    wait_idle(manager)
    other_id = upload(client, sample_csv(settings))
    wait_run(client, other_id)
    wait_idle(manager)
    other_predictions = client.get(f"/api/runs/{other_id}/predictions").json()
    for audience in ["technical", "basic"]:
        manager.store.queue_explanation(run_id, 0, False, audience)
        manager.store.update_explanation(run_id, 0, "completed", "gemini_disabled", audience_level=audience)
        directory = manager.explanation_dir(run_id, 0, audience)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "report_vi.md").write_text("Báo cáo fixture cho kiểm thử xóa.")
        manager.store.save_human_review(run_id, 0, audience, {"notes": "Đánh giá fixture"})
    assert manager.store.alert_page(run_id=run_id)["total"] > 0
    path = f"/api/runs/{run_id}"
    assert client.delete(path, auth=None).status_code == 401
    assert client.delete(path, headers={"Origin": "https://other.invalid"}).status_code == 403
    assert manager.run_dir(run_id).exists()
    assert "delete" in client.get("/openapi.json").json()["paths"]["/api/runs/{run_id}"]
    response = client.delete(path)
    assert response.status_code == 200, response.text
    assert response.json()["files_deleted"] is True
    assert client.get(path).status_code == client.delete(path).status_code == 404
    assert client.get(path + "/export").status_code == 404
    with pytest.raises(RequestConflict):
        manager.control(run_id, "resume")
    assert not manager.run_dir(run_id).exists()
    assert not list(manager.runs_dir.glob(".deleted-*"))
    with manager.store.connect() as connection:
        for table in ["runs", "predictions", "explanations", "alerts", "human_reviews"]:
            column = "id" if table == "runs" else "run_id"
            assert connection.execute(f"SELECT COUNT(*) FROM {table} WHERE {column}=?", (run_id,)).fetchone()[0] == 0
        assert not connection.execute("PRAGMA foreign_key_check").fetchall()
        assert not connection.execute("SELECT * FROM alert_events WHERE alert_id NOT IN (SELECT id FROM alerts)").fetchall()
    assert client.get(f"/api/runs/{other_id}/predictions").json() == other_predictions
    assert manager.run_dir(other_id).exists()
    assert client.get("/api/runs").json()["total"] == 1
    assert manager.runtime.load_count == 1
    assert client.delete("/api/runs/invalid-id").status_code == 422


def test_delete_rejects_prediction_even_after_stop_until_worker_finishes(client, settings, monkeypatch):
    manager = client.app.state.manager
    entered, release = threading.Event(), threading.Event()
    original = manager.runtime.predict

    def slow_predict(values):
        entered.set()
        assert release.wait(10)
        return original(values)

    monkeypatch.setattr(manager.runtime, "predict", slow_predict)
    run_id = upload(client, sample_csv(settings), mode="replay", interval=5)
    try:
        assert entered.wait(5)
        assert client.delete(f"/api/runs/{run_id}").status_code == 409
        assert client.post(f"/api/runs/{run_id}/control", json={"action": "pause"}).status_code == 200
        assert client.delete(f"/api/runs/{run_id}").status_code == 409
        assert client.post(f"/api/runs/{run_id}/control", json={"action": "stop"}).status_code == 200
        assert client.delete(f"/api/runs/{run_id}").status_code == 409
        assert manager.run_dir(run_id).exists()
    finally:
        release.set()
    wait_idle(manager)
    assert client.delete(f"/api/runs/{run_id}").status_code == 200


def test_delete_rejects_running_shap(client, settings, monkeypatch):
    manager = client.app.state.manager
    run_id = upload(client, sample_csv(settings))
    wait_run(client, run_id)
    wait_idle(manager)
    entered, release = threading.Event(), threading.Event()
    from BE.jobs import explain_sample

    def slow_explain(*args):
        entered.set()
        assert release.wait(10)
        return explain_sample(*args)

    monkeypatch.setattr("BE.jobs.explain_sample", slow_explain)
    try:
        assert client.post(f"/api/runs/{run_id}/explanations", json={"row_indices": [0], "use_gemini": False}).status_code == 202
        assert entered.wait(5)
        assert client.delete(f"/api/runs/{run_id}").status_code == 409
        assert manager.run_dir(run_id).exists()
    finally:
        release.set()
    wait_case(client, run_id, 0)
    wait_idle(manager)
    assert client.delete(f"/api/runs/{run_id}").status_code == 200


def test_delete_database_failure_restores_files_and_transaction(client, settings):
    manager = client.app.state.manager
    run_id = upload(client, sample_csv(settings))
    wait_run(client, run_id)
    wait_idle(manager)
    before = client.get(f"/api/runs/{run_id}/predictions").json()
    with manager.store.connect() as connection:
        connection.execute("CREATE TRIGGER reject_run_delete BEFORE DELETE ON runs BEGIN SELECT RAISE(ABORT, 'fixture'); END;")
    with pytest.raises(sqlite3.IntegrityError):
        manager.delete_run(run_id)
    assert manager.run_dir(run_id).is_dir()
    assert not list(manager.runs_dir.glob(".deleted-*"))
    assert client.get(f"/api/runs/{run_id}/predictions").json() == before
    assert manager.store.alert_page(run_id=run_id)["total"] > 0


def test_delete_reports_cleanup_failure_without_claiming_files_removed(client, settings, monkeypatch):
    manager = client.app.state.manager
    run_id = upload(client, sample_csv(settings))
    wait_run(client, run_id)
    wait_idle(manager)

    def reject_cleanup(path):
        raise PermissionError("fixture")

    monkeypatch.setattr("BE.jobs.shutil.rmtree", reject_cleanup)
    response = client.delete(f"/api/runs/{run_id}")
    assert response.status_code == 200 and response.json()["files_deleted"] is False
    assert "chưa được dọn" in response.json()["message"]
    assert client.get(f"/api/runs/{run_id}").status_code == 404
    assert len(list(manager.runs_dir.glob(".deleted-*"))) == 1
