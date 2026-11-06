"""Số tổng toàn hệ thống: biên ngày Việt Nam, mẫu duy nhất, artifact và bộ lọc."""

from datetime import datetime, timedelta, timezone

import numpy as np

from BE.config import CLASS_NAMES
from BE.dashboard import dashboard_summary


NOW = datetime(2026, 11, 3, 12, tzinfo=timezone.utc)


def saved_run(manager, number, labels, created_at=None):
    run_id = f"{number:032x}"
    manager.store.create_run(run_id, f"samples_{number}.csv", "batch", 1, len(labels), manager.runtime.signature)
    for index, label in enumerate(labels):
        probabilities = np.zeros(len(CLASS_NAMES))
        probabilities[CLASS_NAMES.index(label)] = 1
        manager.store.save_prediction(run_id, index, probabilities, CLASS_NAMES, 0.01)
    manager.store.set_run_status(run_id, "completed")
    timestamp = (created_at or NOW).isoformat()
    with manager.store.connect() as connection:
        connection.execute("UPDATE runs SET created_at=?,updated_at=? WHERE id=?", (timestamp, timestamp, run_id))
        connection.execute("UPDATE predictions SET created_at=? WHERE run_id=?", (timestamp, run_id))
    return run_id


def test_dashboard_auth_empty_and_validation(client):
    assert client.get("/api/dashboard", auth=None).status_code == 401
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["metrics"]["predicted_rows"] == 0
    assert data["metrics"]["suspected_percentage"] is None
    assert list(data["class_counts"]) == CLASS_NAMES
    assert len(data["daily_activity"]) == 7
    assert all(day["total_rows"] == 0 for day in data["daily_activity"])
    assert data["recent_runs"] == data["recent_alerts"] == []
    assert data["timezone"] == "Asia/Ho_Chi_Minh"
    assert client.get("/api/dashboard?period=invalid").status_code == 422
    assert client.get("/api/dashboard?run_id=invalid").status_code == 422
    assert client.get("/api/dashboard?run_id=" + "a" * 32).status_code == 404
    assert "/api/dashboard" in client.get("/openapi.json").json()["paths"]


def test_overview_counts_all_rows_and_selected_run_without_inference(client, monkeypatch):
    manager = client.app.state.manager
    first = saved_run(manager, 1, ["Normal", "DDoS"] * 70)
    saved_run(manager, 2, ["BruteForce"] * 31)
    def unexpected_inference(*args):
        raise AssertionError("Dashboard không được suy luận")
    monkeypatch.setattr(manager.runtime, "predict", unexpected_inference)
    all_data = dashboard_summary(manager, "7d", now=NOW)
    assert all_data["metrics"]["predicted_rows"] == 171
    assert all_data["metrics"]["normal_rows"] == 70
    assert all_data["metrics"]["suspected_rows"] == 101
    assert sum(all_data["class_counts"].values()) == 171
    assert sum(all_data["alert_counts"].values()) == 101
    assert len(all_data["recent_alerts"]) == 5
    selected = dashboard_summary(manager, "7d", first, now=NOW)
    assert selected["metrics"]["predicted_rows"] == 140
    assert selected["class_counts"]["BruteForce"] == 0
    assert all(row["run_id"] == first for row in selected["recent_alerts"])
    assert selected["selected_run"]["id"] == first
    assert manager.runtime.load_count == 1


def test_vietnam_day_is_half_open_and_daily_gap_is_zero(client):
    manager = client.app.state.manager
    run_id = saved_run(manager, 1, ["Normal", "DDoS", "BruteForce", "Normal"])
    stamps = ["2026-11-02T16:59:59+00:00", "2026-11-02T17:00:00+00:00",
              "2026-11-03T16:59:59+00:00", "2026-11-03T17:00:00+00:00"]
    with manager.store.connect() as connection:
        for index, stamp in enumerate(stamps):
            connection.execute("UPDATE predictions SET created_at=? WHERE run_id=? AND row_index=?", (stamp, run_id, index))
    data = dashboard_summary(manager, "today", now=NOW)
    assert data["metrics"]["predicted_rows"] == 2
    assert data["daily_activity"] == [{"date": "2026-11-03", "normal_rows": 0, "suspected_rows": 2, "total_rows": 2}]
    data = dashboard_summary(manager, "7d", now=NOW)
    assert data["metrics"]["predicted_rows"] == 3
    assert data["daily_activity"][0]["total_rows"] == 0
    assert data["daily_activity"][-2]["normal_rows"] == 1


def test_actual_shap_artifact_and_technical_review_are_not_double_counted(client):
    manager = client.app.state.manager
    run_id = saved_run(manager, 1, ["Normal", "DDoS", "BruteForce"])
    for index in range(3):
        manager.store.queue_explanation(run_id, index, True)
        manager.store.update_explanation(run_id, index, "completed", "accepted")
    manager.store.queue_explanation(run_id, 0, True, audience_level="basic")
    manager.store.update_explanation(run_id, 0, "completed", "accepted", audience_level="basic")
    manager.store.update_explanation(run_id, 2, "failed", "not_completed")
    # Artifact fixture: dashboard chỉ kiểm tra sự tồn tại, không tự chạy SHAP.
    for index in [0, 2]:
        directory = manager.case_dir(run_id, index)
        directory.mkdir(parents=True)
        (directory / "explanation.json").write_text("{}")
    manager.store.save_human_review(run_id, 0, "technical", {"prediction_assessment": "disagree", "proposed_label": "Recon"})
    manager.store.save_human_review(run_id, 0, "basic", {"prediction_assessment": "agree", "proposed_label": None})
    manager.store.save_human_review(run_id, 1, "technical", {"prediction_assessment": "uncertain", "proposed_label": None})
    data = dashboard_summary(manager, "all", now=NOW)
    assert data["metrics"]["shap_rows"] == 2
    assert data["gemini_counts"]["accepted"] == 2
    assert data["explanation_counts"]["failed"] == 1
    assert data["saved_reviews"] == 2 and data["proposed_labels"] == 1
    assert data["review_counts"] == {"not_reviewed": 1, "agree": 0, "disagree": 1, "uncertain": 1}
    # Đóng cảnh báo không làm thay đổi nhãn hoặc phiếu đánh giá.
    alert_id = manager.store.alert_page(run_id=run_id)["items"][0]["id"]
    manager.store.update_alert(alert_id, "acknowledged", "Đã tiếp nhận", "tester")
    manager.store.update_alert(alert_id, "closed", "Đã kiểm tra", "tester")
    after = dashboard_summary(manager, "all", now=NOW)
    assert after["alert_counts"]["closed"] == 1
    assert after["metrics"]["suspected_rows"] == data["metrics"]["suspected_rows"]
    assert after["review_counts"] == data["review_counts"]


def test_all_history_trend_is_explicitly_bounded_and_delete_updates_totals(client):
    manager = client.app.state.manager
    old = saved_run(manager, 1, ["Web-Based"], NOW - timedelta(days=90))
    saved_run(manager, 2, ["Normal", "Mirai"])
    data = dashboard_summary(manager, "all", now=NOW)
    assert data["metrics"]["predicted_rows"] == 3
    assert len(data["daily_activity"]) == 30
    assert sum(day["total_rows"] for day in data["daily_activity"]) == 2
    assert data["start_date"] is None and data["trend_start_date"] == "2026-10-05"
    manager.store.delete_run(old)
    data = dashboard_summary(manager, "all", now=NOW)
    assert data["metrics"]["predicted_rows"] == 2
    assert data["class_counts"]["Web-Based"] == 0
