import io
import time
import zipfile
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from BE.main import create_app
from conftest import FakeGeminiClient, upload, wait_case, wait_run


def test_auth_and_swagger(client):
    assert client.get("/health").json()["status"] == "ready"
    assert client.get("/api/runs", auth=("tester", "wrong-password")).status_code == 401
    assert client.get("/docs").status_code == 200
    schema = client.get("/openapi.json").json()
    assert schema["components"]["securitySchemes"]["HTTPBasic"]["scheme"] == "basic"
    for path in ["/api/runs", "/api/runs/{run_id}/control", "/api/runs/{run_id}/explanations"]:
        assert "post" in schema["paths"][path]
    assert schema["paths"]["/api/runs"]["post"]["requestBody"]["content"].get("multipart/form-data")
    assert client.get("/api/schema").json()["class_names"] == client.app.state.manager.runtime.class_names
    assert len(pd.read_csv(io.StringIO(client.get("/api/input-template").text)).columns) == 46
    assert client.get("/api/model").json()["model_load_count"] == 1


def test_batch_matches_50_saved_predictions(client, settings):
    content = (settings.integration_dir / "input_features.csv").read_bytes()
    run_id = upload(client, content)
    run = wait_run(client, run_id)
    assert run["processed_rows"] == 50
    response = client.get(f"/api/runs/{run_id}/predictions?limit=1000").json()
    expected = pd.read_csv(settings.integration_dir / "predictions.csv")
    actual = np.asarray([list(row["probabilities"].values()) for row in response["items"]])
    columns = [f"prob_{name}" for name in client.app.state.manager.runtime.class_names]
    np.testing.assert_allclose(actual, expected[columns].to_numpy(), rtol=1e-6, atol=1e-7)
    assert [row["predicted_class"] for row in response["items"]] == expected["predicted_class"].tolist()
    assert len(client.get(f"/api/runs/{run_id}/predictions?offset=10&limit=3").json()["items"]) == 3
    exported = pd.read_csv(io.StringIO(client.get(f"/api/runs/{run_id}/export").text))
    assert len(exported) == 50
    zipped = client.get(f"/api/runs/{run_id}/export?format=zip")
    assert zipped.status_code == 200
    with zipfile.ZipFile(io.BytesIO(zipped.content)) as archive:
        assert {"predictions.csv", "run_status.json", "protocol.json"} <= set(archive.namelist())
        assert not any(".env" in name for name in archive.namelist())
    assert client.get("/api/runs").json()["total"] == 1
    assert client.get("/api/model").json()["model_load_count"] == 1


def test_input_validation_and_optional_label(client, settings):
    data = pd.read_csv(settings.shap_dir / "selected_input.csv").head(2)
    data["label"] = ["Khong dua nhan nay vao prompt", "Other"]
    run_id = upload(client, data.to_csv(index=False).encode())
    assert wait_run(client, run_id)["processed_rows"] == 2
    missing = data.drop(columns=["IAT"]).to_csv(index=False).encode()
    duplicate = data.to_csv(index=False).replace("flow_duration,", "IAT,", 1).encode()
    invalid = data.copy()
    invalid["IAT"] = invalid["IAT"].astype(object)
    invalid.loc[0, "IAT"] = "not-a-number"
    for content in [b"", b"a,b\n1,2\n", missing, duplicate, invalid.to_csv(index=False).encode()]:
        response = client.post("/api/runs", files={"file": ("bad.csv", content)})
        assert response.status_code == 422, response.text
    too_many = pd.concat([data] * 501, ignore_index=True).to_csv(index=False).encode()
    assert client.post("/api/runs", files={"file": ("big.csv", too_many)}).status_code == 422
    assert client.post("/api/runs", files={"file": ("bad.exe", b"data")}).status_code == 422
    assert client.get("/api/runs/" + "0" * 32).status_code == 404
    assert client.get("/api/runs/invalid-id").status_code == 422
    assert client.get("/api/runs").json()["total"] == 1


def test_upload_body_limit(settings, model_runtime):
    small = replace(settings, max_upload_bytes=128)
    with TestClient(create_app(small, model_runtime)) as client:
        client.auth = ("tester", "test-password")
        response = client.post("/api/runs", files={"file": ("big.csv", b"a" * 70000)})
        assert response.status_code == 413
        assert client.get("/api/runs").json()["total"] == 0


def test_replay_pause_stop_resume_matches_batch(client, settings):
    data = pd.read_csv(settings.shap_dir / "selected_input.csv").head(6)
    content = data.to_csv(index=False).encode()
    run_id = upload(client, content, mode="replay", interval=0.15)
    deadline = time.monotonic() + 5
    while client.get(f"/api/runs/{run_id}").json()["processed_rows"] == 0:
        assert time.monotonic() < deadline
        time.sleep(0.01)
    assert client.post(f"/api/runs/{run_id}/control", json={"action": "pause"}).status_code == 200
    time.sleep(0.2)  # Cho phép dòng đang suy luận hoàn tất.
    paused_count = client.get(f"/api/runs/{run_id}").json()["processed_rows"]
    time.sleep(0.25)
    assert client.get(f"/api/runs/{run_id}").json()["processed_rows"] == paused_count
    assert client.post("/api/runs", files={"file": ("other.csv", content)}).status_code == 409
    assert client.post(f"/api/runs/{run_id}/control", json={"action": "stop"}).status_code == 200
    deadline = time.monotonic() + 5
    while client.app.state.manager.active_run is not None:
        assert time.monotonic() < deadline
        time.sleep(0.02)
    assert client.post(f"/api/runs/{run_id}/control", json={"action": "resume"}).status_code == 200
    assert wait_run(client, run_id)["processed_rows"] == 6
    replay = client.get(f"/api/runs/{run_id}/predictions").json()["items"]
    assert [row["row_index"] for row in replay] == list(range(6))
    batch_id = upload(client, content)
    wait_run(client, batch_id)
    batch = client.get(f"/api/runs/{batch_id}/predictions").json()["items"]
    np.testing.assert_allclose(
        [list(row["probabilities"].values()) for row in replay],
        [list(row["probabilities"].values()) for row in batch], rtol=1e-6, atol=1e-7,
    )


def test_restart_preserves_and_resumes(settings, model_runtime):
    content = pd.read_csv(settings.shap_dir / "selected_input.csv").head(2).to_csv(index=False).encode()
    with TestClient(create_app(settings, model_runtime)) as first:
        first.auth = ("tester", "test-password")
        run_id = upload(first, content, mode="replay", interval=5)
        deadline = time.monotonic() + 5
        while first.get(f"/api/runs/{run_id}").json()["processed_rows"] < 1:
            assert time.monotonic() < deadline
            time.sleep(0.02)
    with TestClient(create_app(settings, model_runtime)) as second:
        second.auth = ("tester", "test-password")
        state = second.get(f"/api/runs/{run_id}").json()
        assert state["status"] == "interrupted" and state["processed_rows"] == 1
        assert second.post(f"/api/runs/{run_id}/control", json={"action": "resume"}).status_code == 200
        wait_run(second, run_id)
        rows = second.get(f"/api/runs/{run_id}/predictions").json()["items"]
        assert [row["row_index"] for row in rows] == [0, 1]


def test_real_shap_and_missing_gemini_keep_report(client, settings):
    run_id = upload(client, (settings.integration_dir / "input_features.csv").read_bytes())
    wait_run(client, run_id)
    response = client.post(f"/api/runs/{run_id}/explanations", json={"row_indices": [0]})
    assert response.status_code == 202
    result = wait_case(client, run_id, 0)
    assert result["status"] == "partial"
    assert result["gemini_status"] == "not_configured"
    assert result["explanation"]["max_additivity_error_all_classes"] <= 1e-5
    path = client.app.state.manager.case_dir(run_id, 0)
    with np.load(path / "shap_values.npz", allow_pickle=False) as actual:
        assert actual["values"].shape == (46, 8)
        source = settings.integration_dir / "cases/mau_001/shap_values.npz"
        with np.load(source, allow_pickle=False) as expected:
            np.testing.assert_allclose(actual["values"], expected["values"], rtol=1e-6, atol=1e-7)
    assert "report_vi.md" in result["files"]
    assert client.get(result["files"]["waterfall.png"]).status_code == 200
    assert client.get(result["files"]["report_vi.md"]).status_code == 200
    assert client.get(f"/api/runs/{run_id}/explanations/0/files/.env").status_code == 404
    initial_timestamp = (path / "shap_values.npz").stat().st_mtime_ns
    client.post(f"/api/runs/{run_id}/explanations", json={"row_indices": [0], "use_gemini": False})
    wait_case(client, run_id, 0)
    assert (path / "shap_values.npz").stat().st_mtime_ns == initial_timestamp


def test_selected_rare_classes_and_mock_gemini(settings, model_runtime):
    fake = FakeGeminiClient(behavior="ascii_first")
    with TestClient(create_app(settings, model_runtime, fake)) as client:
        client.auth = ("tester", "test-password")
        run_id = upload(client, (settings.shap_dir / "selected_input.csv").read_bytes())
        wait_run(client, run_id)
        response = client.post(f"/api/runs/{run_id}/explanations", json={"row_indices": [0, 2, 14]})
        assert response.status_code == 202
        results = [wait_case(client, run_id, index) for index in [0, 2, 14]]
        assert [row["explanation"]["predicted_class"] for row in results] == ["Normal", "BruteForce", "Web-Based"]
        assert all(row["gemini_status"] == "accepted" for row in results)
        assert len(fake.calls) == 4  # Ca đầu sửa văn bản một lần, hai ca sau một lần gọi.
        assert all("nhan_that" not in prompt and '"label"' not in prompt for prompt in fake.calls)
        response = client.post(f"/api/runs/{run_id}/explanations", json={"row_indices": [0, 2, 14]})
        assert response.status_code == 202 and len(fake.calls) == 4
        cache = client.app.state.manager.case_dir(run_id, 2) / "shap_values.npz"
        cached_time = cache.stat().st_mtime_ns
        response = client.post(
            f"/api/runs/{run_id}/explanations",
            json={"row_indices": [2], "retry_gemini": True},
        )
        assert response.status_code == 202
        assert wait_case(client, run_id, 2)["gemini_status"] == "accepted"
        assert len(fake.calls) == 5 and cache.stat().st_mtime_ns == cached_time
        assert list((cache.parent / "previous_gemini").iterdir())
        assert client.get("/api/model").json()["model_load_count"] == 1


def test_explanation_validation_and_capacity(client, settings, monkeypatch):
    import threading
    manager = client.app.state.manager
    release = threading.Event()

    def hold_task(*args):
        while not release.is_set() and not manager.shutdown_event.is_set():
            release.wait(0.02)

    monkeypatch.setattr(manager, "process_explanation", hold_task)
    data = pd.read_csv(settings.shap_dir / "selected_input.csv")
    run_id = upload(client, pd.concat([data] * 4, ignore_index=True).to_csv(index=False).encode())
    wait_run(client, run_id)
    for indices in [[], [-1], [True], [0, 0], list(range(51))]:
        assert client.post(f"/api/runs/{run_id}/explanations", json={"row_indices": indices}).status_code == 422
    assert client.post(f"/api/runs/{run_id}/explanations", json={"row_indices": [999]}).status_code == 409
    response = client.post(f"/api/runs/{run_id}/explanations", json={"row_indices": list(range(50))})
    assert response.status_code == 202
    assert client.post(f"/api/runs/{run_id}/explanations", json={"row_indices": [0]}).status_code == 202
    assert client.post(f"/api/runs/{run_id}/explanations", json={"row_indices": [50]}).status_code == 429
    release.set()


def test_missing_value_uses_frozen_preprocessor(client, settings):
    data = pd.read_csv(settings.shap_dir / "selected_input.csv").head(1)
    data.loc[0, "flow_duration"] = np.nan
    run_id = upload(client, data.to_csv(index=False).encode())
    wait_run(client, run_id)
    response = client.post(f"/api/runs/{run_id}/explanations", json={"row_indices": [0], "use_gemini": False})
    assert response.status_code == 202
    result = wait_case(client, run_id, 0)
    assert result["status"] == "completed"
    assert result["explanation"]["max_additivity_error_all_classes"] <= 1e-5


def test_stop_interrupts_long_replay_wait(client, settings):
    content = pd.read_csv(settings.shap_dir / "selected_input.csv").head(3).to_csv(index=False).encode()
    run_id = upload(client, content, mode="replay", interval=60)
    deadline = time.monotonic() + 5
    while client.get(f"/api/runs/{run_id}").json()["processed_rows"] < 1:
        assert time.monotonic() < deadline
        time.sleep(0.01)
    assert client.post(f"/api/runs/{run_id}/control", json={"action": "stop"}).status_code == 200
    deadline = time.monotonic() + 2
    while client.app.state.manager.active_run is not None:
        assert time.monotonic() < deadline, "Worker không nên đợi hết nhịp 60 giây sau yêu cầu stop."
        time.sleep(0.01)
    assert client.get(f"/api/runs/{run_id}").json()["processed_rows"] == 1


def test_same_runtime_rejects_second_server(client, settings, model_runtime):
    with pytest.raises(RuntimeError, match="Runtime đã có server"):
        with TestClient(create_app(settings, model_runtime)):
            pass
    assert client.get("/health").status_code == 200
