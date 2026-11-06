"""Tổng quan từ SQLite và bằng chứng đã lưu; không chạy suy luận hoặc gọi LLM."""

import json
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from BE.config import CLASS_NAMES
from BE.utils import utc_now


LOCAL_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")


def dashboard_summary(manager, period="7d", run_id=None, now=None):
    now = now or datetime.now(timezone.utc)
    today = now.astimezone(LOCAL_TIMEZONE).date()
    days = {"today": 1, "7d": 7, "30d": 30, "all": None}[period]
    start_date = today - timedelta(days=days - 1) if days else None
    end_utc = datetime.combine(today + timedelta(days=1), time.min, LOCAL_TIMEZONE).astimezone(timezone.utc)
    start_utc = datetime.combine(start_date, time.min, LOCAL_TIMEZONE).astimezone(timezone.utc) if start_date else None
    # Toàn bộ lịch sử dùng biểu đồ 30 ngày gần nhất, ghi rõ phạm vi trên API/UI.
    trend_start = start_date or today - timedelta(days=29)
    parameters = [end_utc.isoformat()]
    conditions = ["p.created_at < ?"]
    if start_utc:
        conditions.append("p.created_at >= ?")
        parameters.append(start_utc.isoformat())
    if run_id:
        conditions.append("p.run_id = ?")
        parameters.append(run_id)
    prediction_where = " AND ".join(conditions)

    with manager.store.connect() as connection:
        # Các truy vấn SQL đọc cùng snapshot, tránh đếm trùng khi worker đang ghi.
        connection.execute("BEGIN")
        connection.execute("CREATE TEMP TABLE dashboard_samples AS SELECT p.run_id,p.row_index,p.predicted_class,p.predicted_probability,p.created_at FROM predictions p WHERE " + prediction_where, parameters)
        class_counts = dict.fromkeys(CLASS_NAMES, 0)
        for row in connection.execute("SELECT predicted_class, COUNT(*) AS count FROM dashboard_samples GROUP BY predicted_class"):
            class_counts[row["predicted_class"]] = row["count"]
        predicted_rows = sum(class_counts.values())
        normal_rows = class_counts["Normal"]
        suspected_rows = predicted_rows - normal_rows

        # Cả run mới chưa có mẫu và run cũ có mẫu xử lý trong khoảng chọn đều hiện.
        run_conditions = ["r.created_at < ?"]
        run_parameters = [end_utc.isoformat()]
        if start_utc:
            run_conditions.append("r.created_at >= ?")
            run_parameters.append(start_utc.isoformat())
        run_where = "(" + " AND ".join(run_conditions) + " OR EXISTS (SELECT 1 FROM dashboard_samples p WHERE p.run_id=r.id))"
        if run_id:
            run_where += " AND r.id=?"
            run_parameters.append(run_id)
        run_count = connection.execute("SELECT COUNT(*) FROM runs r WHERE " + run_where, run_parameters).fetchone()[0]
        recent_runs = [dict(row) for row in connection.execute(
            "SELECT r.* FROM runs r WHERE " + run_where + " ORDER BY r.updated_at DESC, r.id DESC LIMIT 5", run_parameters,
        )]
        run_options = [dict(row) for row in connection.execute(
            "SELECT id, filename, created_at FROM runs ORDER BY created_at DESC, id DESC LIMIT 100",
        )]
        available_run_count = connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        selected_run = None
        if run_id:
            row = connection.execute("SELECT id, filename, created_at FROM runs WHERE id=?", (run_id,)).fetchone()
            selected_run = dict(row) if row else None

        alert_counts = dict.fromkeys(["new", "acknowledged", "closed"], 0)
        for row in connection.execute(
            "SELECT a.status, COUNT(*) AS count FROM alerts a JOIN dashboard_samples p "
            "ON p.run_id=a.run_id AND p.row_index=a.row_index GROUP BY a.status",
        ):
            alert_counts[row["status"]] = row["count"]
        recent_alerts = [dict(row) for row in connection.execute(
            "SELECT a.id, a.run_id, a.row_index, a.status, a.created_at, p.predicted_class, "
            "p.predicted_probability, r.filename FROM alerts a JOIN dashboard_samples p "
            "ON p.run_id=a.run_id AND p.row_index=a.row_index JOIN runs r ON r.id=a.run_id "
            "ORDER BY a.created_at DESC, a.id DESC LIMIT 5",
        )]

        explanation_counts = dict.fromkeys([
            "not_requested", "queued", "shap_running", "gemini_running", "completed", "partial", "failed", "interrupted",
        ], 0)
        gemini_counts = {}
        for row in connection.execute(
            "SELECT e.status, e.gemini_status, COUNT(*) AS count FROM explanations e JOIN dashboard_samples p "
            "ON p.run_id=e.run_id AND p.row_index=e.row_index WHERE e.audience_level='technical' "
            "GROUP BY e.status,e.gemini_status",
        ):
            explanation_counts[row["status"]] += row["count"]
            gemini_counts[row["gemini_status"]] = gemini_counts.get(row["gemini_status"], 0) + row["count"]
        requested_rows = sum(explanation_counts.values())
        explanation_counts["not_requested"] = predicted_rows - requested_rows
        gemini_counts["not_requested"] = predicted_rows - requested_rows

        # Một mẫu có hai mức diễn giải vẫn chỉ có một bộ SHAP dùng chung.
        shap_candidates = connection.execute(
            "SELECT DISTINCT p.run_id,p.row_index FROM dashboard_samples p JOIN explanations e "
            "ON p.run_id=e.run_id AND p.row_index=e.row_index",
        ).fetchall()
        shap_rows = sum((manager.case_dir(row["run_id"], row["row_index"]) / "explanation.json").is_file() for row in shap_candidates)

        review_counts = dict.fromkeys(["not_reviewed", "agree", "disagree", "uncertain"], 0)
        saved_reviews = 0
        proposed_labels = 0
        for row in connection.execute(
            "SELECT h.payload FROM human_reviews h JOIN dashboard_samples p ON p.run_id=h.run_id "
            "AND p.row_index=h.row_index WHERE h.audience_level='technical'",
        ):
            review = json.loads(row["payload"])
            saved_reviews += 1
            assessment = review["prediction_assessment"]
            review_counts[assessment] += 1
            if review.get("proposed_label") is not None:
                proposed_labels += 1
        review_counts["not_reviewed"] += predicted_rows - saved_reviews

        activity = {}
        for row in connection.execute(
            "SELECT date(created_at,'+7 hours') AS day, predicted_class, COUNT(*) AS count "
            "FROM dashboard_samples GROUP BY day,predicted_class",
        ):
            day = activity.setdefault(row["day"], {"normal_rows": 0, "suspected_rows": 0})
            key = "normal_rows" if row["predicted_class"] == "Normal" else "suspected_rows"
            day[key] += row["count"]
        daily_activity = []
        date = trend_start
        while date <= today:
            counts = activity.get(date.isoformat(), {"normal_rows": 0, "suspected_rows": 0})
            daily_activity.append({"date": date.isoformat(), **counts, "total_rows": sum(counts.values())})
            date += timedelta(days=1)

    return {
        "generated_at": utc_now(), "period": period, "timezone": "Asia/Ho_Chi_Minh",
        "start_date": start_date.isoformat() if start_date else None, "end_date": today.isoformat(),
        "trend_start_date": trend_start.isoformat(), "trend_end_date": today.isoformat(),
        "audience_level": "technical", "selected_run": selected_run,
        "metrics": {"predicted_rows": predicted_rows, "normal_rows": normal_rows,
                    "suspected_rows": suspected_rows, "suspected_percentage": 100 * suspected_rows / predicted_rows if predicted_rows else None,
                    "pending_alerts": alert_counts["new"], "shap_rows": shap_rows, "run_count": run_count},
        "class_counts": class_counts, "daily_activity": daily_activity,
        "alert_counts": alert_counts, "explanation_counts": explanation_counts, "gemini_counts": gemini_counts,
        "review_counts": review_counts, "saved_reviews": saved_reviews, "proposed_labels": proposed_labels,
        "recent_runs": recent_runs, "recent_alerts": recent_alerts,
        "run_options": run_options, "available_run_count": available_run_count,
    }
