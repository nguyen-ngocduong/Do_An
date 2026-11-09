"""Nhận dòng Kafka, staging trên volume, gửi CSV sang BE và chờ kết quả."""

import argparse
import fcntl
import json
import logging
import os
from pathlib import Path
import signal
import threading
import time

from confluent_kafka import Consumer
import httpx

from streaming.client import BackendBusy, NidrClient
from streaming.state import Staging


logger = logging.getLogger(__name__)


class CsvConsumer:
    def __init__(self, consumer, client, staging, state_dir, mode="batch", interval=0.05):
        self.consumer = consumer
        self.client = client
        self.staging = staging
        self.state_dir = state_dir
        self.mode = mode
        self.interval = interval
        self.stopping = threading.Event()

    def receive(self, message):
        if message is None:
            return
        if message.error():
            raise RuntimeError("Kafka không đọc được sự kiện; offset chưa được commit.")
        value = message.value()
        if value is None or len(value) > 16000:
            raise ValueError("Sự kiện Kafka trống hoặc quá lớn.")
        event = json.loads(value)
        self.staging.accept(event)
        # Không đảo thứ tự này: ACK chỉ sau SQLite staging commit thành công.
        self.consumer.commit(message=message, asynchronous=False)

    def heartbeat(self):
        (self.state_dir / "consumer.heartbeat").touch()

    def wait(self):
        self.heartbeat()
        assignments = self.consumer.assignment()
        if assignments:
            self.consumer.pause(assignments)
        # Poll giữ group membership khi đang chờ BE. Rebalance vẫn có thể giao một record;
        # nhận và staging record đó trước khi tiếp tục, không bỏ mất nó.
        self.receive(self.consumer.poll(0.2))
        self.stopping.wait(1)

    def process_pending(self):
        pending = self.staging.pending()
        if pending is None:
            return False
        source_id = pending["source_id"]
        while not self.stopping.is_set():
            try:
                if not pending["run_id"]:
                    run = self.client.submit(self.staging.csv_bytes(source_id), pending["filename"],
                                             source_id, self.mode, self.interval)
                    self.staging.submitted(source_id, run["id"])
                    pending["run_id"] = run["id"]
                    logger.info("Đã nhập %s vào lần chạy %s.", pending["filename"], run["id"])
                run = self.client.run(pending["run_id"])
            except (BackendBusy, httpx.TransportError):
                self.wait()
                continue
            if run["status"] == "completed":
                self.staging.complete(source_id)
                logger.info("Hoàn tất %s: %d dòng, model xử lý trong BE.", pending["filename"], run["processed_rows"])
                return True
            if run["status"] in ["failed", "interrupted", "stopped"]:
                raise RuntimeError("Lần chạy cần người vận hành xử lý/tiếp tục trong NIDR; không tự tạo bản sao.")
            self.wait()
        return False

    def run(self, max_files=0):
        completed = 0
        while not self.stopping.is_set():
            self.heartbeat()
            if self.process_pending():
                completed += 1
                if max_files and completed >= max_files:
                    return
            assigned = self.consumer.assignment()
            if assigned:
                self.consumer.resume(assigned)
            self.receive(self.consumer.poll(1))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-files", type=int, default=0, help="0: chạy liên tục; dùng 1 để kiểm thử một file")
    parser.add_argument("--health", action="store_true")
    args = parser.parse_args()
    state_dir = Path(os.getenv("STREAM_STATE_DIR", "/state"))
    if args.health:
        path = state_dir / "consumer.heartbeat"
        raise SystemExit(0 if path.exists() and time.time() - path.stat().st_mtime < 60 else 1)
    state_dir.mkdir(parents=True, exist_ok=True)
    topic = os.getenv("KAFKA_TOPIC", "nidr.csv.rows.v1")
    client = NidrClient()
    consumer = None
    try:
        names = client.feature_names()
        staging = Staging(state_dir / "consumer.sqlite3", names, topic)
        consumer = Consumer({"bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
                             "group.id": os.getenv("KAFKA_GROUP_ID", "nidr-predict-v1"),
                             "enable.auto.commit": False, "enable.auto.offset.store": False,
                             "auto.offset.reset": "earliest", "max.poll.interval.ms": 300000,
                             "queued.max.messages.kbytes": 1024, "fetch.message.max.bytes": 1048576,
                             "allow.auto.create.topics": False})
        consumer.subscribe([topic])
        worker = CsvConsumer(consumer, client, staging, state_dir,
                             os.getenv("KAFKA_RUN_MODE", "batch"), float(os.getenv("KAFKA_REPLAY_INTERVAL", "0.05")))
        for sig in [signal.SIGTERM, signal.SIGINT]:
            signal.signal(sig, lambda signum, frame: worker.stopping.set())
        with (state_dir / "consumer.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            worker.run(args.max_files)
    finally:
        if consumer is not None:
            consumer.close()
        client.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        main()
    except Exception as error:
        logger.error("Consumer dừng (%s); staging và offset đã lưu vẫn được giữ.", type(error).__name__)
        raise SystemExit(1) from None
