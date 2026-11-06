"""Phát CSV theo dòng. Mặc định một file, 50 dòng/giây, không tự chạy Gemini."""

import argparse
import fcntl
import logging
import json
import os
from pathlib import Path
import sqlite3
import time

from confluent_kafka import Producer

from streaming.events import encode, read_csv_events, validate_event


logger = logging.getLogger(__name__)


def publish_file(producer, topic, events, rate):
    failed = []

    def delivered(error, message):
        if error is not None and not failed:
            failed.append(error.code())

    for event in events:
        while True:
            try:
                producer.produce(topic, partition=0, key=event["file_sha256"].encode(),
                                 value=encode(event), on_delivery=delivered)
                break
            except BufferError:
                producer.poll(0.1)
        producer.poll(0)
        if failed:
            raise RuntimeError("Kafka từ chối sự kiện; chưa đánh dấu file đã phát.")
        if rate:
            time.sleep(1 / rate)
    remaining = producer.flush(30)
    if failed or remaining:
        raise RuntimeError("Chưa nhận đủ ACK Kafka; chạy lại sẽ phát lại file an toàn.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-files", type=int, default=1)
    parser.add_argument("--file", help="Tên file nidr_test_*.csv trong thư mục upload")
    parser.add_argument("--rate", type=float, default=float(os.getenv("CSV_ROWS_PER_SECOND", "50")))
    parser.add_argument("--republish", action="store_true", help="Phát lại kể cả khi checkpoint đã có ACK; BE vẫn chống tạo trùng")
    args = parser.parse_args()
    if not 1 <= args.max_files <= 729 or args.rate < 0 or args.rate > 1000:
        parser.error("max-files: 1..729; rate: 0..1000 (0 là không giới hạn nhịp).")
    source = Path(os.getenv("CSV_SOURCE_DIR", "/input")).resolve()
    state_dir = Path(os.getenv("STREAM_STATE_DIR", "/state"))
    state_dir.mkdir(parents=True, exist_ok=True)
    topic = os.getenv("KAFKA_TOPIC", "nidr.csv.rows.v1")
    # Schema được COPY từ artifact tích hợp đã chốt; producer không cần BE online/tài khoản.
    schema_path = Path(__file__).with_name("input_schema.json")
    if not schema_path.exists():
        schema_path = Path(__file__).resolve().parents[1] / "output/integration_runs/integration_20261022_075217_0b67d48f/input_schema.json"
    names = json.loads(schema_path.read_text())["feature_names"]
    if len(names) != 46 or len(set(names)) != 46:
        raise ValueError("Schema producer không phải 46 đặc trưng đã chốt.")
    producer = Producer({"bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
                         "enable.idempotence": True, "acks": "all", "compression.type": "gzip",
                         "queue.buffering.max.kbytes": 1024, "queue.buffering.max.messages": 1000,
                         "delivery.timeout.ms": 30000, "client.id": "nidr-csv-producer"})
    with (state_dir / "producer.lock").open("a") as lock, sqlite3.connect(state_dir / "producer.sqlite3") as db:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        db.execute("CREATE TABLE IF NOT EXISTS published(topic TEXT,sha TEXT,PRIMARY KEY(topic,sha))")
        files = sorted(source.rglob("nidr_test_*.csv"))
        if not files:
            raise ValueError("Không có CSV nidr_test_*.csv đọc được; kiểm tra mount và quyền thư mục upload.")
        if args.file:
            files = [p for p in files if p.name == args.file]
            if len(files) != 1:
                raise ValueError("Không tìm thấy duy nhất file yêu cầu trong thư mục upload.")
        count = 0
        for path in files:
            if not path.resolve().is_relative_to(source):
                raise ValueError("Không đọc symlink ra ngoài thư mục upload.")
            events = read_csv_events(path, names)
            for event in events:
                validate_event(event, names)
            digest = events[0]["file_sha256"]
            previous = db.execute("SELECT 1 FROM published WHERE topic=? AND sha=?", (topic, digest)).fetchone()
            if previous and not args.republish:
                continue
            publish_file(producer, topic, events, args.rate)
            db.execute("INSERT OR IGNORE INTO published VALUES(?,?)", (topic, digest))
            db.commit()
            logger.info("Kafka đã ACK %s (%d dòng).", path.name, len(events))
            count += 1
            if count >= args.max_files:
                break
        logger.info("Hoàn tất phát %d file. Không phát manifest.csv hoặc label.", count)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        main()
    except Exception as error:
        # Không in exception HTTP có thể chứa URL/tài khoản.
        logger.error("Producer dừng (%s); checkpoint đã ACK vẫn được giữ.", type(error).__name__)
        raise SystemExit(1) from None
