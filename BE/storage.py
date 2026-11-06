"""SQLite lưu tiến độ và kết quả; mỗi thao tác mở connection riêng."""

import json
import sqlite3
from contextlib import contextmanager

from BE.config import CLASS_NAMES
from BE.utils import utc_now


class AlertConflict(Exception):
    """Chuyển trạng thái cảnh báo không đúng thứ tự."""


class Store:
    def __init__(self, path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY, filename TEXT NOT NULL, mode TEXT NOT NULL,
                    interval_seconds REAL NOT NULL, status TEXT NOT NULL,
                    total_rows INTEGER NOT NULL, processed_rows INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    signature TEXT NOT NULL, message TEXT NOT NULL DEFAULT ''
                );
                -- Giữ receipt kể cả khi run bị xóa: đọc lại Kafka không tự hồi sinh dữ liệu đã xóa.
                CREATE TABLE IF NOT EXISTS ingestion_receipts (
                    source_id TEXT PRIMARY KEY, request_hash TEXT NOT NULL,
                    run_id TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS predictions (
                    run_id TEXT NOT NULL REFERENCES runs(id), row_index INTEGER NOT NULL,
                    predicted_class TEXT NOT NULL, predicted_probability REAL NOT NULL,
                    probabilities TEXT NOT NULL, predict_seconds REAL NOT NULL,
                    created_at TEXT NOT NULL, PRIMARY KEY (run_id, row_index)
                );
                CREATE TABLE IF NOT EXISTS explanations (
                    run_id TEXT NOT NULL REFERENCES runs(id), row_index INTEGER NOT NULL,
                    audience_level TEXT NOT NULL DEFAULT 'technical',
                    status TEXT NOT NULL, use_gemini INTEGER NOT NULL,
                    gemini_status TEXT NOT NULL DEFAULT 'pending',
                    message TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL,
                    PRIMARY KEY (run_id, row_index, audience_level)
                );
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL, row_index INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'new' CHECK(status IN ('new','acknowledged','closed')),
                    note TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    UNIQUE(run_id, row_index),
                    FOREIGN KEY(run_id,row_index) REFERENCES predictions(run_id,row_index)
                );
                CREATE TABLE IF NOT EXISTS alert_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id INTEGER NOT NULL REFERENCES alerts(id), previous_status TEXT,
                    status TEXT NOT NULL, note TEXT NOT NULL,
                    actor TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS human_reviews (
                    run_id TEXT NOT NULL, row_index INTEGER NOT NULL,
                    audience_level TEXT NOT NULL, payload TEXT NOT NULL,
                    PRIMARY KEY(run_id,row_index,audience_level),
                    FOREIGN KEY(run_id,row_index) REFERENCES predictions(run_id,row_index)
                );
            """)
            # DDL và sao chép dữ liệu cũ phải cùng transaction để có thể rollback.
            connection.execute("BEGIN IMMEDIATE")
            self.migrate_explanations(connection)
            # Bổ sung cảnh báo cho dữ liệu cũ; không thay đổi dự đoán hoặc gọi Gemini.
            connection.execute(
                "INSERT OR IGNORE INTO alerts(run_id,row_index,created_at,updated_at) "
                "SELECT run_id,row_index,created_at,created_at FROM predictions "
                "WHERE predicted_class!='Normal' ORDER BY created_at,run_id,row_index"
            )
            connection.execute(
                "INSERT INTO alert_events(alert_id,previous_status,status,note,actor,created_at) "
                "SELECT id,NULL,status,'Cảnh báo theo model; chưa xác nhận tấn công thực tế.',"
                "'system',created_at FROM alerts WHERE NOT EXISTS "
                "(SELECT 1 FROM alert_events WHERE alert_id=alerts.id)"
            )
            # Không tự gọi lại API khi server khởi động sau một lần gián đoạn.
            connection.execute(
                "UPDATE runs SET status='interrupted', message=?, updated_at=? "
                "WHERE status IN ('queued','running','paused')",
                ("Server đã khởi động lại; có thể chủ động tiếp tục lần chạy.", utc_now()),
            )
            connection.execute(
                "UPDATE explanations SET status='interrupted', message=?, updated_at=? "
                "WHERE status IN ('queued','shap_running','gemini_running')",
                ("Tác vụ bị gián đoạn; gửi lại yêu cầu để dùng cache và tiếp tục.", utc_now()),
            )

    def migrate_explanations(self, connection):
        columns = [row['name'] for row in connection.execute("PRAGMA table_info(explanations)")]
        if "audience_level" in columns:
            return
        connection.execute("ALTER TABLE explanations RENAME TO explanations_legacy")
        connection.execute("""
            CREATE TABLE explanations (
                run_id TEXT NOT NULL REFERENCES runs(id), row_index INTEGER NOT NULL,
                audience_level TEXT NOT NULL DEFAULT 'technical', status TEXT NOT NULL,
                use_gemini INTEGER NOT NULL, gemini_status TEXT NOT NULL DEFAULT 'pending',
                message TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL,
                PRIMARY KEY(run_id,row_index,audience_level)
            )
        """)
        connection.execute(
            "INSERT INTO explanations(run_id,row_index,audience_level,status,use_gemini,gemini_status,message,updated_at) "
            "SELECT run_id,row_index,'technical',status,use_gemini,gemini_status,message,updated_at FROM explanations_legacy"
        )
        connection.execute("DROP TABLE explanations_legacy")

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=15)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def human_review(self, run_id, row_index, audience_level):
        with self.connect() as connection:
            row = connection.execute(
                "SELECT payload FROM human_reviews WHERE run_id=? AND row_index=? AND audience_level=?",
                (run_id, row_index, audience_level),
            ).fetchone()
        return json.loads(row["payload"]) if row else None

    def save_human_review(self, run_id, row_index, audience_level, review):
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO human_reviews VALUES(?,?,?,?) "
                "ON CONFLICT(run_id,row_index,audience_level) DO UPDATE SET payload=excluded.payload",
                (run_id, row_index, audience_level, json.dumps(review, ensure_ascii=False, allow_nan=False)),
            )

    def human_reviews(self, run_id):
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM human_reviews WHERE run_id=? ORDER BY row_index,audience_level", (run_id,),
            ).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def create_run(self, run_id, filename, mode, interval, total_rows, signature,
                   source_id=None, request_hash=None):
        now = utc_now()
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO runs(id,filename,mode,interval_seconds,status,total_rows,"
                "created_at,updated_at,signature) VALUES(?,?,?,?,?,?,?,?,?)",
                (run_id, filename, mode, interval, "queued", total_rows, now, now, signature),
            )
            if source_id is not None:
                connection.execute(
                    "INSERT INTO ingestion_receipts(source_id,request_hash,run_id,created_at) VALUES(?,?,?,?)",
                    (source_id, request_hash, run_id, now),
                )

    def ingestion_receipt(self, source_id):
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM ingestion_receipts WHERE source_id=?", (source_id,)).fetchone()
        return dict(row) if row else None

    def get_run(self, run_id):
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
            if row is None:
                return None
            result = dict(row)
            counts = connection.execute(
                "SELECT status, COUNT(*) AS count FROM explanations WHERE run_id=? "
                "AND audience_level='technical' GROUP BY status",
                (run_id,),
            ).fetchall()
            result["explanation_counts"] = {row["status"]: row["count"] for row in counts}
            return result

    def list_runs(self, offset=0, limit=50):
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM runs ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset)
            ).fetchall()
            total = connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        return {"items": [dict(row) for row in rows], "total": total}

    def set_run_status(self, run_id, status, message=""):
        with self.connect() as connection:
            connection.execute(
                "UPDATE runs SET status=?, message=?, updated_at=? WHERE id=?",
                (status, message, utc_now(), run_id),
            )

    def delete_run(self, run_id):
        """Xóa cùng transaction, từ bảng con tới bảng cha để giữ khóa ngoại."""
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "DELETE FROM alert_events WHERE alert_id IN (SELECT id FROM alerts WHERE run_id=?)",
                (run_id,),
            )
            for table in ["alerts", "human_reviews", "explanations", "predictions"]:
                # Tên bảng chỉ lấy từ danh sách cố định; run_id luôn là tham số SQL.
                connection.execute(f"DELETE FROM {table} WHERE run_id=?", (run_id,))
            connection.execute("DELETE FROM runs WHERE id=?", (run_id,))

    def save_prediction(self, run_id, row_index, probabilities, class_names, seconds):
        predicted = int(probabilities.argmax())
        values = {name: float(probabilities[index]) for index, name in enumerate(class_names)}
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO predictions VALUES(?,?,?,?,?,?,?)",
                (run_id, row_index, class_names[predicted], float(probabilities[predicted]),
                 json.dumps(values), seconds, utc_now()),
            )
            connection.execute(
                "UPDATE runs SET processed_rows=processed_rows+1, updated_at=? WHERE id=?",
                (utc_now(), run_id),
            )
            if class_names[predicted] != "Normal":
                now = utc_now()
                cursor = connection.execute(
                    "INSERT INTO alerts(run_id,row_index,created_at,updated_at) VALUES(?,?,?,?)",
                    (run_id, row_index, now, now),
                )
                connection.execute(
                    "INSERT INTO alert_events(alert_id,previous_status,status,note,actor,created_at) "
                    "VALUES(?,NULL,'new',?,'system',?)",
                    (cursor.lastrowid, "Cảnh báo theo model; chưa xác nhận tấn công thực tế.", now),
                )

    def predictions(self, run_id, offset=0, limit=1000):
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM predictions WHERE run_id=? ORDER BY row_index LIMIT ? OFFSET ?",
                (run_id, limit, offset),
            ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["probabilities"] = json.loads(item["probabilities"])
            result.append(item)
        return result

    def prediction(self, run_id, row_index):
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM predictions WHERE run_id=? AND row_index=?", (run_id, row_index)
            ).fetchone()
        if row is None:
            return None
        result = dict(row)
        result["probabilities"] = json.loads(result["probabilities"])
        return result

    def queue_explanation(self, run_id, row_index, use_gemini, audience_level="technical"):
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO explanations(run_id,row_index,audience_level,status,use_gemini,updated_at) "
                "VALUES(?,?,?,'queued',?,?) ON CONFLICT(run_id,row_index,audience_level) DO UPDATE SET "
                "status='queued',use_gemini=excluded.use_gemini,gemini_status='pending',"
                "message='',updated_at=excluded.updated_at",
                (run_id, row_index, audience_level, int(use_gemini), utc_now()),
            )

    def update_explanation(self, run_id, row_index, status, gemini_status="pending", message="", audience_level="technical"):
        with self.connect() as connection:
            connection.execute(
                "UPDATE explanations SET status=?,gemini_status=?,message=?,updated_at=? "
                "WHERE run_id=? AND row_index=? AND audience_level=?",
                (status, gemini_status, message, utc_now(), run_id, row_index, audience_level),
            )

    def explanation(self, run_id, row_index, audience_level="technical"):
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM explanations WHERE run_id=? AND row_index=? AND audience_level=?",
                (run_id, row_index, audience_level),
            ).fetchone()
        return dict(row) if row else None

    def explanations(self, run_id, audience_level=None):
        with self.connect() as connection:
            condition = "run_id=?"
            parameters = [run_id]
            if audience_level is not None:
                condition += " AND audience_level=?"
                parameters.append(audience_level)
            rows = connection.execute(
                f"SELECT * FROM explanations WHERE {condition} ORDER BY row_index,audience_level", parameters,
            ).fetchall()
        return [dict(row) for row in rows]

    def prediction_page(self, run_id, offset=0, limit=100, predicted_class=None,
                        explanation_status=None, audience_level="technical"):
        condition = "p.run_id=?"
        parameters = [audience_level, run_id]
        if predicted_class is not None:
            condition += " AND p.predicted_class=?"
            parameters.append(predicted_class)
        if explanation_status is not None:
            condition += " AND COALESCE(e.status,'not_requested')=?"
            parameters.append(explanation_status)
        joined = (
            " FROM predictions p LEFT JOIN explanations e ON p.run_id=e.run_id "
            "AND p.row_index=e.row_index AND e.audience_level=? "
            "LEFT JOIN alerts a ON p.run_id=a.run_id AND p.row_index=a.row_index "
            f"WHERE {condition}"
        )
        with self.connect() as connection:
            connection.execute("BEGIN")
            total = connection.execute("SELECT COUNT(*)" + joined, parameters).fetchone()[0]
            total_predicted = connection.execute(
                "SELECT COUNT(*) FROM predictions WHERE run_id=?", (run_id,),
            ).fetchone()[0]
            rows = connection.execute(
                "SELECT p.*,COALESCE(e.status,'not_requested') AS explanation_status,"
                "COALESCE(e.gemini_status,'not_requested') AS gemini_status,"
                "a.id AS alert_id,a.status AS alert_status" + joined + " ORDER BY p.row_index LIMIT ? OFFSET ?",
                parameters + [limit, offset],
            ).fetchall()
        items = []
        for row in rows:
            item = dict(row)
            item["probabilities"] = json.loads(item["probabilities"])
            items.append(item)
        return {"items": items, "total": total, "total_predicted": total_predicted,
                "offset": offset, "limit": limit, "audience_level": audience_level}

    def explanation_page(self, run_id, offset=0, limit=100, status=None, audience_level="technical"):
        condition = "run_id=? AND audience_level=?"
        parameters = [run_id, audience_level]
        if status is not None:
            condition += " AND status=?"
            parameters.append(status)
        with self.connect() as connection:
            connection.execute("BEGIN")
            total = connection.execute(f"SELECT COUNT(*) FROM explanations WHERE {condition}", parameters).fetchone()[0]
            rows = connection.execute(
                f"SELECT * FROM explanations WHERE {condition} ORDER BY row_index LIMIT ? OFFSET ?",
                parameters + [limit, offset],
            ).fetchall()
        return {"run_id": run_id, "items": [dict(row) for row in rows], "total": total,
                "offset": offset, "limit": limit, "audience_level": audience_level}

    def summary(self, run_id, audience_level="technical"):
        with self.connect() as connection:
            connection.execute("BEGIN")
            run = connection.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
            if run is None:
                return None
            class_counts = dict.fromkeys(CLASS_NAMES, 0)
            for row in connection.execute(
                "SELECT predicted_class,COUNT(*) AS count FROM predictions WHERE run_id=? GROUP BY predicted_class",
                (run_id,),
            ):
                class_counts[row["predicted_class"]] = row["count"]
            explanation_counts = dict.fromkeys(
                ["queued", "shap_running", "gemini_running", "completed", "partial", "failed", "interrupted"], 0,
            )
            for row in connection.execute(
                "SELECT status,COUNT(*) AS count FROM explanations WHERE run_id=? AND audience_level=? GROUP BY status",
                (run_id, audience_level),
            ):
                explanation_counts[row["status"]] = row["count"]
            processed = sum(class_counts.values())
            not_requested = processed - sum(explanation_counts.values())
            explanation_counts["not_requested"] = not_requested
            gemini_counts = {"not_requested": not_requested}
            for row in connection.execute(
                "SELECT gemini_status,COUNT(*) AS count FROM explanations "
                "WHERE run_id=? AND audience_level=? GROUP BY gemini_status", (run_id, audience_level),
            ):
                gemini_counts[row["gemini_status"]] = row["count"]
            alert_counts = dict.fromkeys(["new", "acknowledged", "closed"], 0)
            for row in connection.execute(
                "SELECT status,COUNT(*) AS count FROM alerts WHERE run_id=? GROUP BY status", (run_id,),
            ):
                alert_counts[row["status"]] = row["count"]
        return {
            "run_id": run_id, "prediction_status": run["status"], "total_rows": run["total_rows"],
            "processed_rows": processed, "pending_rows": run["total_rows"] - processed,
            "class_counts": class_counts, "normal_rows": class_counts["Normal"],
            "suspected_attack_rows": processed - class_counts["Normal"],
            "explanation_counts": explanation_counts, "gemini_counts": gemini_counts,
            "alert_counts": alert_counts, "audience_level": audience_level,
            "human_semantic_review": "user_review_available",
        }

    def alert_page(self, offset=0, limit=100, status=None, predicted_class=None,
                   run_id=None, audience_level="technical"):
        condition = "1=1"
        parameters = [audience_level]
        for column, value in [("a.status", status), ("p.predicted_class", predicted_class), ("a.run_id", run_id)]:
            if value is not None:
                condition += f" AND {column}=?"
                parameters.append(value)
        joined = (
            " FROM alerts a JOIN predictions p ON a.run_id=p.run_id AND a.row_index=p.row_index "
            "LEFT JOIN explanations e ON a.run_id=e.run_id AND a.row_index=e.row_index AND e.audience_level=? "
            f"WHERE {condition}"
        )
        with self.connect() as connection:
            connection.execute("BEGIN")
            total = connection.execute("SELECT COUNT(*)" + joined, parameters).fetchone()[0]
            rows = connection.execute(
                "SELECT a.*,p.predicted_class,p.predicted_probability,"
                "COALESCE(e.status,'not_requested') AS explanation_status,"
                "COALESCE(e.gemini_status,'not_requested') AS gemini_status" + joined
                + " ORDER BY a.id DESC LIMIT ? OFFSET ?", parameters + [limit, offset],
            ).fetchall()
        return {"items": [dict(row) for row in rows], "total": total,
                "offset": offset, "limit": limit, "audience_level": audience_level}

    def alert(self, alert_id, audience_level="technical"):
        with self.connect() as connection:
            connection.execute("BEGIN")
            row = connection.execute(
                "SELECT a.*,p.predicted_class,p.predicted_probability,"
                "COALESCE(e.status,'not_requested') AS explanation_status,"
                "COALESCE(e.gemini_status,'not_requested') AS gemini_status FROM alerts a "
                "JOIN predictions p ON a.run_id=p.run_id AND a.row_index=p.row_index "
                "LEFT JOIN explanations e ON a.run_id=e.run_id AND a.row_index=e.row_index AND e.audience_level=? "
                "WHERE a.id=?", (audience_level, alert_id),
            ).fetchone()
            if row is None:
                return None
            result = dict(row)
            result["history"] = [dict(event) for event in connection.execute(
                "SELECT * FROM alert_events WHERE alert_id=? ORDER BY id", (alert_id,),
            )]
        return result

    def update_alert(self, alert_id, status, note, actor):
        transitions = {"new": ["acknowledged"], "acknowledged": ["closed"], "closed": ["acknowledged"]}
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM alerts WHERE id=?", (alert_id,)).fetchone()
            if row is None:
                return False
            if status != row["status"] and status not in transitions[row["status"]]:
                raise AlertConflict("Chuyển trạng thái không hợp lệ: new → acknowledged → closed; mở lại bằng acknowledged.")
            next_note = row["note"] if note is None else note.strip()
            if status == row["status"] and next_note == row["note"]:
                return True
            now = utc_now()
            connection.execute(
                "UPDATE alerts SET status=?,note=?,updated_at=? WHERE id=?", (status, next_note, now, alert_id),
            )
            connection.execute(
                "INSERT INTO alert_events(alert_id,previous_status,status,note,actor,created_at) VALUES(?,?,?,?,?,?)",
                (alert_id, row["status"], status, next_note, actor, now),
            )
        return True
