"""Kafka thật + BE/model thật trên runtime tạm; không gọi Gemini hoặc sửa dữ liệu vận hành.

Chạy từ repo root sau khi build hai image và khởi động Kafka:
    .venv/bin/python deploy/observability/smoke_test.py
"""

import argparse
import base64
import csv
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import urllib.request
import uuid


ROOT = Path(__file__).resolve().parents[2]


def command(arguments, timeout=90):
    result = subprocess.run(arguments, text=True, capture_output=True, timeout=timeout)
    if result.returncode:
        # Các lệnh test chỉ dùng credentials giả; vẫn không xuất nguyên command/log ra chat.
        raise RuntimeError(f"Lệnh kiểm thử thất bại: {arguments[0]} (exit {result.returncode})")
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend-image", default="nidr-backend:kafka-observability")
    parser.add_argument("--streaming-image", default="nidr-streaming:1.0.0")
    parser.add_argument("--broker-container", default="nidr-kafka-1")
    parser.add_argument("--network", default="nidr_app")
    args = parser.parse_args()
    suffix = uuid.uuid4().hex[:10]
    topic = "nidr.smoke." + suffix
    backend = "nidr-smoke-backend-" + suffix
    consumer = "nidr-smoke-consumer-" + suffix
    state_volume = "nidr-smoke-state-" + suffix
    credentials = "smoke:temporary-test-password"
    source = ROOT / "output/integration_runs/integration_20261022_075217_0b67d48f"
    containers = []
    try:
        command(["docker", "exec", args.broker_container, "/opt/kafka/bin/kafka-topics.sh", "--bootstrap-server",
                 "localhost:9092", "--create", "--topic", topic, "--partitions", "1", "--replication-factor", "1"])
        command(["docker", "run", "-d", "--name", backend, "--network", args.network,
                 "-p", "127.0.0.1::8000", "-e", "ADMIN_USERNAME=smoke", "-e", "ADMIN_PASSWORD=temporary-test-password",
                 "-e", "RUNTIME_DIR=/tmp/nidr-smoke", "-e", "LANGFUSE_ENABLED=false", "-e", "GEMINI_API_KEY=",
                 args.backend_image])
        containers.append(backend)
        port = command(["docker", "port", backend, "8000/tcp"]).strip().rsplit(":", 1)[1]
        base = "http://127.0.0.1:" + port

        def get(path):
            request = urllib.request.Request(base + path)
            request.add_header("Authorization", "Basic " + base64.b64encode(credentials.encode()).decode())
            with urllib.request.urlopen(request, timeout=5) as response:
                return json.load(response)

        deadline = time.monotonic() + 120
        while True:
            try:
                if get("/health")["status"] == "ready":
                    break
            except (OSError, ValueError):
                pass
            if time.monotonic() > deadline:
                raise TimeoutError("BE kiểm thử không ready.")
            time.sleep(1)
        env = ["-e", "NIDR_API_URL=http://" + backend + ":8000", "-e", "ADMIN_USERNAME=smoke",
               "-e", "ADMIN_PASSWORD=temporary-test-password", "-e", "KAFKA_BOOTSTRAP_SERVERS=kafka:9092",
               "-e", "KAFKA_TOPIC=" + topic, "-e", "KAFKA_GROUP_ID=smoke-" + suffix]
        command(["docker", "run", "-d", "--name", consumer, "--network", args.network,
                 "-v", state_volume + ":/state", *env, args.streaming_image])
        containers.append(consumer)
        with tempfile.TemporaryDirectory(prefix="nidr-kafka-smoke-") as temporary:
            path = Path(temporary)
            path.chmod(0o755)  # UID 10001 trong adapter cần đọc thư mục bind mount.
            shutil.copyfile(source / "input_features.csv", path / "nidr_test_00001.csv")
            (path / "manifest.csv").write_text("file,rows\nfake,999\n")
            producer = ["docker", "run", "--rm", "--network", args.network, "-v", str(path) + ":/input:ro",
                        *env, args.streaming_image, "python", "-m", "streaming.producer", "--rate", "0"]
            command(producer)
            deadline = time.monotonic() + 90
            while True:
                runs = get("/api/runs")
                if runs["total"] == 1 and runs["items"][0]["status"] == "completed":
                    break
                if time.monotonic() > deadline:
                    raise TimeoutError("Consumer chưa hoàn tất file kiểm thử.")
                time.sleep(1)
            run = runs["items"][0]
            predictions = get(f"/api/runs/{run['id']}/predictions?limit=1000")["items"]
            expected = list(csv.DictReader(io.StringIO((source / "predictions.csv").read_text())))
            assert len(predictions) == len(expected) == 50
            for actual, golden in zip(predictions, expected):
                assert actual["predicted_class"] == golden["predicted_class"]
                for name, value in actual["probabilities"].items():
                    assert abs(value - float(golden["prob_" + name])) < 1e-6
            # Phát cùng dữ liệu lần hai và restart consumer: không tạo run thứ hai.
            command(producer)
            command(["docker", "restart", consumer])
            time.sleep(3)
            assert get("/api/runs")["total"] == 1
            assert get("/api/model")["model_load_count"] == 1
            result = {"kafka_rows": 100, "prediction_rows": 50, "runs_after_duplicate_and_restart": 1,
                      "golden_predictions_match": True, "model_load_count": 1, "real_gemini_calls": 0}
            print(json.dumps(result, indent=2))
    finally:
        for container in reversed(containers):
            subprocess.run(["docker", "rm", "-f", container], capture_output=True)
        subprocess.run(["docker", "volume", "rm", state_volume], capture_output=True)
        subprocess.run(["docker", "exec", args.broker_container, "/opt/kafka/bin/kafka-topics.sh",
                        "--bootstrap-server", "localhost:9092", "--delete", "--topic", topic], capture_output=True)


if __name__ == "__main__":
    main()
