"""Staging bền vững: commit Kafka offset chỉ sau khi sự kiện đã nằm trên volume."""

from contextlib import contextmanager
import csv
import io
import json
import sqlite3

from streaming.events import MAX_BYTES, encode, validate_event


class Staging:
    def __init__(self, path, feature_names, topic):
        self.path = path
        self.names = feature_names
        self.topic = topic
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS files (
                    source_id TEXT PRIMARY KEY, filename TEXT NOT NULL,
                    row_count INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'collecting', run_id TEXT
                );
                CREATE TABLE IF NOT EXISTS rows (
                    source_id TEXT NOT NULL, row_index INTEGER NOT NULL, payload TEXT NOT NULL,
                    PRIMARY KEY(source_id,row_index)
                );
            """)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def accept(self, event):
        validate_event(event, self.names)
        source_id = f"kafka:{self.topic}:{event['file_sha256']}"
        payload = encode(event).decode()
        with self.connect() as db:
            existing = db.execute("SELECT * FROM files WHERE source_id=?", (source_id,)).fetchone()
            if existing and (existing["row_count"] != event["row_count"] or existing["filename"] != event["filename"]):
                raise ValueError("Metadata của cùng nguồn Kafka bị thay đổi.")
            if existing and existing["status"] in ["submitted", "completed"]:
                return source_id
            db.execute("INSERT OR IGNORE INTO files(source_id,filename,row_count) VALUES(?,?,?)",
                       (source_id, event["filename"], event["row_count"]))
            previous = db.execute("SELECT payload FROM rows WHERE source_id=? AND row_index=?",
                                  (source_id, event["row_index"])).fetchone()
            if previous and previous["payload"] != payload:
                raise ValueError("Một dòng Kafka được phát lại với nội dung khác.")
            db.execute("INSERT OR IGNORE INTO rows VALUES(?,?,?)", (source_id, event["row_index"], payload))
            count = db.execute("SELECT COUNT(*) FROM rows WHERE source_id=?", (source_id,)).fetchone()[0]
            if count == event["row_count"]:
                db.execute("UPDATE files SET status='ready' WHERE source_id=?", (source_id,))
        return source_id

    def pending(self):
        with self.connect() as db:
            row = db.execute("SELECT * FROM files WHERE status IN ('ready','submitted') ORDER BY rowid LIMIT 1").fetchone()
        return dict(row) if row else None

    def csv_bytes(self, source_id):
        with self.connect() as db:
            file = db.execute("SELECT * FROM files WHERE source_id=?", (source_id,)).fetchone()
            rows = db.execute("SELECT payload FROM rows WHERE source_id=? ORDER BY row_index", (source_id,)).fetchall()
        if file is None or len(rows) != file["row_count"]:
            raise ValueError("Chưa nhận đủ dòng của CSV.")
        output = io.StringIO(newline="")
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(self.names)
        for row in rows:
            values = json.loads(row["payload"])["features"]
            writer.writerow([values[name] for name in self.names])
        content = output.getvalue().encode()
        if len(content) > MAX_BYTES:
            raise ValueError("CSV khôi phục vượt 10 MiB.")
        return content

    def submitted(self, source_id, run_id):
        with self.connect() as db:
            db.execute("UPDATE files SET status='submitted',run_id=? WHERE source_id=?", (run_id, source_id))

    def complete(self, source_id):
        with self.connect() as db:
            db.execute("UPDATE files SET status='completed' WHERE source_id=?", (source_id,))
            # Giữ receipt nhỏ; giải phóng bản sao các dòng đã nằm trong BE và Kafka.
            db.execute("DELETE FROM rows WHERE source_id=?", (source_id,))
