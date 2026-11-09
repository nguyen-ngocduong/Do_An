"""BE trả Swagger; API input giữ đúng dữ liệu và không suy luận lại."""

import io

import numpy as np
import pandas as pd

from conftest import upload, wait_run


def test_backend_root_redirects_to_swagger_and_private_files_stay_private(client):
    assert client.get("/", auth=("tester", "wrong")).status_code == 401
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307 and response.headers["location"] == "/docs"
    for path in ["/assets/app.js", "/assets/styles.css", "/FE/PLAN.md", "/BE/.env", "/output/README.md"]:
        assert client.get(path).status_code == 404
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").json()["info"]["version"] == "1.8.0"


def test_input_row_order_missing_values_and_no_label(client, settings):
    frame = pd.read_csv(settings.shap_dir / "selected_input.csv").head(2)
    frame.loc[0, "IAT"] = np.nan
    frame["label"] = "Không gửi nhãn thật vào UI đầu vào"
    run_id = upload(client, frame.to_csv(index=False).encode())
    wait_run(client, run_id)
    url = f"/api/runs/{run_id}/inputs/0"
    before = client.get(f"/api/runs/{run_id}/summary").json()
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["row_index"] == 0 and data["run_id"] == run_id
    assert list(data["features"]) == client.app.state.manager.runtime.feature_names
    assert len(data["features"]) == 46 and "label" not in data["features"]
    assert data["features"]["IAT"] is None
    expected = pd.read_csv(io.StringIO(frame.to_csv(index=False))).iloc[0]
    for name, value in data["features"].items():
        if value is not None:
            assert value == float(np.float32(expected[name]))
    assert client.get(f"/api/runs/{run_id}/summary").json() == before
    assert client.get("/api/model").json()["model_load_count"] == 1
    assert client.get(url, auth=("tester", "wrong")).status_code == 401
    assert client.get(f"/api/runs/{run_id}/inputs/2").status_code == 404
    assert client.get(f"/api/runs/{run_id}/inputs/-1").status_code == 422
    assert client.get(f"/api/runs/{'a' * 32}/inputs/0").status_code == 404


def test_input_row_rejects_tampered_saved_array(client, settings):
    frame = pd.read_csv(settings.shap_dir / "selected_input.csv").head(1)
    run_id = upload(client, frame.to_csv(index=False).encode())
    wait_run(client, run_id)
    saved = settings.runtime_dir / "runs" / run_id / "input_values.npy"
    saved.write_bytes(b"altered")
    response = client.get(f"/api/runs/{run_id}/inputs/0")
    assert response.status_code == 422
    assert "Checksum" in response.json()["detail"]
