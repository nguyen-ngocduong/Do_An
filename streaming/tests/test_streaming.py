import json
from pathlib import Path

import httpx
import pytest

from streaming.client import BackendBusy, NidrClient
from streaming.consumer import CsvConsumer
from streaming.events import encode, read_csv_events, validate_event
from streaming.producer import publish_file
from streaming import producer as producer_module
from streaming.state import Staging


@pytest.fixture
def events(tmp_path):
    path = tmp_path / "nidr_test_00001.csv"
    path.write_text("A,B,label\n1.2345678901234567,,Normal\n-2,3,DDoS\n")
    return read_csv_events(path, ["A", "B"])


def test_csv_roundtrip_retains_values_and_excludes_labels(tmp_path, events):
    assert "label" not in encode(events[0]).decode()
    assert events[0]["features"]["A"] == "1.2345678901234567"
    store = Staging(tmp_path / "state.sqlite3", ["A", "B"], "topic")
    store.accept(events[1])
    assert store.pending() is None
    source_id = store.accept(events[0])
    assert store.csv_bytes(source_id).decode() == "A,B\n1.2345678901234567,\n-2,3\n"
    # Event trùng không tạo thêm dòng; restart đọc lại đúng staging.
    store.accept(events[0])
    store = Staging(store.path, ["A", "B"], "topic")
    assert store.pending()["row_count"] == 2
    store.submitted(source_id, "run-1")
    store.complete(source_id)
    store.accept(events[1])
    assert store.pending() is None
    with store.connect() as db:
        assert db.execute("SELECT COUNT(*) FROM rows").fetchone()[0] == 0


@pytest.mark.parametrize("change", [
    {"version": 2}, {"row_index": -1}, {"row_count": 1001}, {"filename": "../a.csv"},
    {"file_sha256": "bad"}, {"row_index": True}, {"features": {"A": "1", "label": "Normal"}},
    {"features": {"A": "inf", "B": ""}}, {"features": {"A": "word", "B": ""}},
])
def test_rejects_invalid_events(events, change):
    with pytest.raises(ValueError):
        validate_event({**events[0], **change}, ["A", "B"])


def test_conflicting_row_rolls_back_and_incomplete_csv_is_not_submitted(tmp_path, events):
    store = Staging(tmp_path / "state.sqlite3", ["A", "B"], "topic")
    source_id = store.accept(events[0])
    with pytest.raises(ValueError):
        store.accept({**events[0], "features": {"A": "9", "B": ""}})
    with pytest.raises(ValueError):
        store.csv_bytes(source_id)
    assert store.pending() is None


@pytest.mark.parametrize("content", ["A,A\n1,2\n", "A,B,C\n1,2,3\n", "A,B\n", "A,B\n1\n"])
def test_rejects_bad_csv(tmp_path, content):
    path = tmp_path / "bad.csv"
    path.write_text(content)
    with pytest.raises(ValueError):
        read_csv_events(path, ["A", "B"])


def test_producer_requires_delivery_ack(events):
    class Producer:
        def __init__(self, fail=False):
            self.fail = fail
            self.messages = []

        def produce(self, topic, **kwargs):
            self.messages.append(kwargs)

        def poll(self, timeout):
            pass

        def flush(self, timeout):
            return 1 if self.fail else 0

    producer = Producer()
    publish_file(producer, "topic", events, 0)
    assert len(producer.messages) == 2
    assert all(m["partition"] == 0 for m in producer.messages)
    with pytest.raises(RuntimeError):
        publish_file(Producer(fail=True), "topic", events, 0)


def test_producer_works_without_backend_credentials_and_keeps_checkpoint(tmp_path, monkeypatch):
    source = Path(__file__).resolve().parents[2] / "output/integration_runs/integration_20261022_075217_0b67d48f/input_features.csv"
    (tmp_path / "nidr_test_00001.csv").write_bytes(source.read_bytes())
    messages = []

    class Kafka:
        def __init__(self, config):
            pass

        def produce(self, topic, **kwargs):
            messages.append(kwargs)

        def poll(self, timeout):
            pass

        def flush(self, timeout):
            return 0

    monkeypatch.setattr(producer_module, "Producer", Kafka)
    monkeypatch.setenv("CSV_SOURCE_DIR", str(tmp_path))
    monkeypatch.setenv("STREAM_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("NIDR_API_URL", "http://127.0.0.1:1")
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    monkeypatch.setattr("sys.argv", ["producer", "--rate", "0"])
    producer_module.main()
    producer_module.main()
    assert len(messages) == 50
    monkeypatch.setattr("sys.argv", ["producer", "--rate", "0", "--republish"])
    producer_module.main()
    assert len(messages) == 100


def test_consumer_commits_only_after_staging_and_completes_once(tmp_path, events):
    class Message:
        def __init__(self, event):
            self.event = event

        def error(self):
            return None

        def value(self):
            return encode(self.event)

    class Kafka:
        def __init__(self):
            self.commits = 0

        def commit(self, **kwargs):
            self.commits += 1
            assert store.pending() is not None or self.commits == 1

    class Client:
        def __init__(self):
            self.submits = 0

        def submit(self, content, filename, source_id, mode, interval):
            self.submits += 1
            assert content.startswith(b"A,B\n") and source_id.startswith("kafka:topic:")
            return {"id": "run-1"}

        def run(self, run_id):
            return {"status": "completed", "processed_rows": 2}

    store = Staging(tmp_path / "state.sqlite3", ["A", "B"], "topic")
    kafka, client = Kafka(), Client()
    worker = CsvConsumer(kafka, client, store, tmp_path)
    worker.receive(Message(events[0]))
    assert not worker.process_pending()
    worker.receive(Message(events[1]))
    assert worker.process_pending()
    assert not worker.process_pending() and client.submits == 1
    bad = {**events[0], "row_index": -1}
    with pytest.raises(ValueError):
        worker.receive(Message(bad))
    assert kafka.commits == 2


def test_client_uses_idempotency_key_and_rejects_old_be():
    def handle(request):
        if request.url.path == "/api/observability":
            return httpx.Response(200, json={"ingestion_idempotency": True})
        if request.url.path == "/api/schema":
            return httpx.Response(200, json={"feature_names": ["A", "B"]})
        assert request.headers["Idempotency-Key"] == "kafka:topic:sha"
        assert b"label" not in request.content
        return httpx.Response(202, json={"id": "run-1"})

    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(handle)) as http:
        client = NidrClient(http)
        assert client.feature_names() == ["A", "B"]
        assert client.submit(b"A,B\n1,2\n", "file.csv", "kafka:topic:sha")["id"] == "run-1"
    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(lambda r: httpx.Response(404))) as old:
        with pytest.raises(RuntimeError, match="1.8.0"):
            NidrClient(old).feature_names()


def test_busy_api_is_retryable_but_conflict_and_auth_are_not():
    def run(status, message):
        http = httpx.Client(base_url="http://test", transport=httpx.MockTransport(
            lambda r: httpx.Response(status, json={"detail": message})))
        return NidrClient(http)

    with pytest.raises(BackendBusy):
        run(409, "Đang có lần chạy dự đoán/phát lại.").submit(b"csv", "f.csv", "key")
    for status in [401, 409, 422]:
        with pytest.raises(RuntimeError):
            run(status, "Không hợp lệ").submit(b"csv", "f.csv", "key")
