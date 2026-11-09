"""Idempotency-Key bảo vệ nhập lại khi API response bị mất hoặc consumer restart."""

from fastapi.testclient import TestClient

from BE.main import create_app
from conftest import wait_run


def submit(client, content, key, **data):
    return client.post("/api/runs", files={"file": ("source.csv", content)},
                       headers={"Idempotency-Key": key}, data=data)


def test_duplicate_and_conflicting_content(client, settings):
    content = (settings.integration_dir / "input_features.csv").read_bytes()
    original = submit(client, content, "kafka:topic:source").json()
    repeated = submit(client, content, "kafka:topic:source")
    assert repeated.status_code == 202 and repeated.json()["id"] == original["id"]
    assert submit(client, content + b"\n", "kafka:topic:source").status_code == 409
    assert submit(client, content, "kafka:topic:source", mode="replay").status_code == 409
    assert client.get("/api/runs").json()["total"] == 1
    assert wait_run(client, original["id"])["processed_rows"] == 50
    assert client.get("/api/model").json()["model_load_count"] == 1


def test_receipt_survives_restart(settings, model_runtime):
    content = (settings.integration_dir / "input_features.csv").read_bytes()
    with TestClient(create_app(settings, model_runtime)) as first:
        first.auth = ("tester", "test-password")
        run = submit(first, content, "kafka:restart").json()
        wait_run(first, run["id"])
    with TestClient(create_app(settings, model_runtime)) as second:
        second.auth = ("tester", "test-password")
        repeated = submit(second, content, "kafka:restart")
        assert repeated.status_code == 202
        assert repeated.json()["id"] == run["id"]
        assert second.get("/api/runs").json()["total"] == 1
        assert second.delete(f"/api/runs/{run['id']}").status_code == 200
        assert submit(second, content, "kafka:restart").status_code == 409
        assert second.get("/api/runs").json()["total"] == 0


def test_invalid_upload_has_no_receipt_and_key_must_be_bounded(client, settings):
    assert submit(client, b"a,b\n1,2\n", "kafka:invalid").status_code == 422
    assert client.app.state.manager.store.ingestion_receipt("kafka:invalid") is None
    content = (settings.integration_dir / "input_features.csv").read_bytes()
    assert submit(client, content, "x" * 161).status_code == 422
    assert submit(client, content, "spaces not allowed").status_code == 422
    assert submit(client, content, "kafka:invalid").status_code == 202
