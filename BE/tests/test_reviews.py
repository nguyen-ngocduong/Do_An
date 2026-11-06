import json

import pandas as pd

from BE.storage import Store
from conftest import upload, wait_run


def prepare_review(client, settings):
    content = pd.read_csv(settings.shap_dir / "selected_input.csv").head(1).to_csv(index=False).encode()
    run_id = upload(client, content)
    wait_run(client, run_id)
    path = f"/api/runs/{run_id}/human-reviews/0"
    current = client.get(path).json()
    return run_id, path, {
        "reviewer_name": "Người kiểm tra", "prediction_assessment": "uncertain",
        "explanation_clarity": 3, "notes": "Cần đối chiếu thêm bằng chứng <script>chỉ là văn bản</script>",
        "evidence_signature": current["context"]["evidence_signature"],
    }


def test_review_persists_exports_and_does_not_change_prediction(client, settings):
    run_id, path, body = prepare_review(client, settings)
    before = client.get(f"/api/runs/{run_id}/predictions").json()
    assert client.get(path).json()["review"] is None
    assert client.get(path + "/export").status_code == 404
    saved = client.put(path, json=body)
    assert saved.status_code == 200, saved.text
    review = saved.json()["review"]
    assert review["reviewer_username"] == "tester" and review["explanation_clarity"] == 3
    assert client.get(path).json()["review"] == review
    reopened = Store(settings.runtime_dir / "app.sqlite3")
    assert reopened.human_review(run_id, 0, "technical") == review
    assert client.get(f"/api/runs/{run_id}/predictions").json() == before
    assert client.get(path + "?audience_level=basic").json()["review"] is None
    response = client.get(path + "/export")
    assert response.status_code == 200 and response.json()["review"] == review
    assert "attachment" in response.headers["content-disposition"]
    assert client.get(path, auth=None).status_code == 401
    assert client.put(path, json=body, auth=None).status_code == 401
    assert client.get(path + "/export", auth=None).status_code == 401


def test_review_rejects_invalid_scores_names_labels_and_spoofed_author(client, settings):
    _, path, body = prepare_review(client, settings)
    for changes in [
        {"explanation_clarity": 0}, {"evidence_faithfulness": 6}, {"actionability": True},
        {"reviewer_name": "   "}, {"reviewer_username": "pretend-expert"},
        {"notes": "x" * 4001}, {"proposed_label": "Unknown"},
        {"proposed_label": "DDoS", "prediction_assessment": "agree"},
    ]:
        assert client.put(path, json={**body, **changes}).status_code == 422
    assert client.put(path, json=body, headers={"Origin": "https://other.invalid"}).status_code == 403
    assert client.get(path.rsplit("/", 1)[0] + "/99").status_code == 404


def test_review_evidence_change_keeps_old_review_and_rejects_stale_save(client, settings):
    run_id, path, body = prepare_review(client, settings)
    assert client.put(path, json=body).status_code == 200
    directory = client.app.state.manager.case_dir(run_id, 0)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "explanation.json").write_text(json.dumps({"new": "bằng chứng mới"}))
    response = client.get(path).json()
    assert response["stale"] is True
    assert response["review"]["evidence_signature"] == body["evidence_signature"]
    assert client.put(path, json=body).status_code == 409
    body["evidence_signature"] = response["context"]["evidence_signature"]
    assert client.put(path, json=body).status_code == 200
    assert client.get(path).json()["stale"] is False
