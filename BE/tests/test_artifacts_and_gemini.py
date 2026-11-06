import copy
import importlib.metadata
import json
import shutil
from dataclasses import replace
from types import SimpleNamespace

import joblib
import pytest

from BE.artifacts import ModelRuntime
from BE.gemini_service import GeminiService
from BE.gemini_validation import validate_evidence, validate_text
from BE.utils import read_json
from conftest import FakeGeminiClient


def test_corrupt_source_rejected_before_loading(settings, tmp_path, monkeypatch):
    damaged = tmp_path / "damaged"
    damaged.mkdir()
    shutil.copyfile(settings.xgb_dir / "output_checksums.json", damaged / "output_checksums.json")
    (damaged / "protocol.json").write_text('{}')
    monkeypatch.setattr(joblib, "load", lambda *args: pytest.fail("Không được nạp model chưa kiểm tra."))
    with pytest.raises(ValueError, match="Checksum"):
        ModelRuntime(replace(settings, xgb_dir=damaged))


def test_version_mismatch_rejected_before_loading(settings, monkeypatch):
    original = importlib.metadata.version
    monkeypatch.setattr(importlib.metadata, "version", lambda name: "0.0.0" if name == "pandas" else original(name))
    monkeypatch.setattr(joblib, "load", lambda *args: pytest.fail("Không được nạp sklearn objects khi lệch phiên bản."))
    with pytest.raises(ValueError, match="pandas=="):
        ModelRuntime(settings)


def test_all_50_saved_accepted_reports_pass_validation(settings):
    config = read_json(settings.integration_dir / "generation_config.json")
    guide = read_json(settings.integration_dir / "check_guide.json")
    directories = sorted((settings.integration_dir / "cases").iterdir())
    assert len(directories) == 50
    for directory in directories:
        item = read_json(directory / "explanation.json")
        result = read_json(directory / "explanation_vi.json")
        validate_evidence(result, item, config["response_json_schema"], guide)
        validate_text(result, item, guide)


@pytest.mark.parametrize("behavior,status,attempts", [
    ("valid", "accepted", 1), ("ascii_first", "accepted", 2),
    ("wrong_class", "invalid_evidence", 1), ("quota", "api_error", 1),
    ("timeout", "request_error", 1),
])
def test_gemini_errors_repair_and_response_cache(settings, tmp_path, behavior, status, attempts):
    runtime = SimpleNamespace(
        generation_config=read_json(settings.integration_dir / "generation_config.json"),
        check_guide=read_json(settings.integration_dir / "check_guide.json"),
    )
    item = read_json(settings.integration_dir / "cases/mau_001/explanation.json")
    client = FakeGeminiClient(behavior)
    service = GeminiService(runtime, settings, client)
    directory = tmp_path / "case"
    directory.mkdir()
    result = service.explain(item, directory)
    assert result["status"] == status
    assert len(client.calls) == attempts
    if status == "invalid_evidence":
        assert result["result"] is None and not (directory / "explanation_vi.json").exists()
    if behavior == "quota":
        assert read_json(directory / "gemini_response_01.json")["http_code"] == 429
    cached = service.explain(item, directory)
    assert cached["status"] == status and len(client.calls) == attempts
    assert not any("nhạy cảm" in path.read_text() for path in directory.glob('gemini_response_*.json'))
