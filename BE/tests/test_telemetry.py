"""Tracing tắt/hỏng không đổi kết quả; SDK thật export vào bộ nhớ trong test."""

from dataclasses import replace
from contextlib import contextmanager
import json
from types import SimpleNamespace

from langfuse import Langfuse
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
import pytest

from BE.telemetry import Telemetry
from BE.gemini_service import GeminiService


def test_disabled_missing_keys_and_bad_url_do_not_connect(settings):
    monitor = Telemetry(settings)
    assert monitor.status()["active"] is False
    with monitor.span("disabled") as span:
        span.update(output={"ok": True})
        assert span.trace_id is None
    missing = Telemetry(replace(settings, langfuse_enabled=True))
    assert missing.status()["problem"] == "missing_keys"
    invalid = Telemetry(replace(settings, langfuse_enabled=True, langfuse_public_key="pk-test",
                                langfuse_secret_key="sk-test", langfuse_base_url="http://evil.example"))
    assert invalid.status()["problem"] == "invalid_cloud_url"


def test_real_sdk_records_nested_generation_and_masks_secrets(settings):
    exporter = InMemorySpanExporter()
    client = Langfuse(public_key="pk-lf-unit-test", secret_key="sk-lf-unit-test",
                      tracer_provider=TracerProvider(), span_exporter=exporter,
                      media_upload_thread_count=1)
    monitor = Telemetry(settings, client=client)
    try:
        with monitor.span("explanation", metadata={"run_id": "test"}) as root:
            root.update(input={"row_index": 0})
            with monitor.span("gemini", generation=True, model="test-model") as child:
                child.update(input="prompt " + settings.admin_password,
                             output={"answer": "Diễn giải tiếng Việt"},
                             usage_details={"input": 10, "output": 2, "total": 12})
                assert child.trace_id == root.trace_id
        client.flush()
        spans = exporter.get_finished_spans()
        assert len(spans) == 2
        generation = next(s for s in spans if s.name == "gemini")
        parent = next(s for s in spans if s.name == "explanation")
        assert generation.parent.span_id == parent.context.span_id
        encoded = json.dumps([dict(s.attributes) for s in spans], ensure_ascii=False)
        assert settings.admin_password not in encoded
        assert "REDACTED" in encoded and "test-model" in encoded
        assert json.loads(generation.attributes["langfuse.observation.output"])["answer"] == "Diễn giải tiếng Việt"
        assert generation.attributes["langfuse.observation.type"] == "generation"
    finally:
        monitor.close()


def test_broken_export_does_not_hide_application_errors(settings):
    class Broken:
        def start_as_current_observation(self, **kwargs):
            raise RuntimeError("must not leak secrets")

        def shutdown(self):
            raise RuntimeError("must not leak secrets")

    monitor = Telemetry(settings, client=Broken())
    with monitor.span("still-works"):
        result = 42
    assert result == 42
    with pytest.raises(ValueError, match="application-error"):
        with monitor.span("failing-app"):
            raise ValueError("application-error")
    monitor.close()


def test_observability_endpoint_requires_auth_and_never_returns_keys(client):
    response = client.get("/api/observability")
    assert response.status_code == 200
    assert response.json()["ingestion_idempotency"] is True
    assert response.json()["active"] is False
    assert "test-password" not in response.text
    assert client.get("/api/observability", auth=("tester", "bad")).status_code == 401


@pytest.mark.parametrize("api_error", [False, True])
def test_generation_records_actual_usage_errors_and_skips_cache(settings, tmp_path, api_error):
    observations = []

    class Capture:
        @contextmanager
        def start_as_current_observation(self, **fields):
            data = dict(fields)
            observations.append(data)
            yield SimpleNamespace(update=lambda **values: data.update(values))

    class Gemini:
        def __init__(self):
            self.models = self
            self.calls = 0

        def generate_content(self, **kwargs):
            self.calls += 1
            if api_error:
                from google.genai.errors import ClientError
                raise ClientError(429, {"error": {"message": settings.admin_password}})
            return SimpleNamespace(text="Báo cáo", model_dump=lambda **kwargs: {
                "model_version": "gemini-test-version", "usage_metadata": {
                    "prompt_token_count": 10, "candidates_token_count": 3,
                    "thoughts_token_count": 2, "total_token_count": 15,
                },
            })

    runtime = SimpleNamespace(generation_config={"response_json_schema": {}}, check_guide={})
    gemini = Gemini()
    service = GeminiService(runtime, settings, client=gemini)
    service.telemetry = Telemetry(settings, client=Capture())
    result = service.call(tmp_path, 1, "Prompt " + settings.admin_password)
    assert service.call(tmp_path, 1, "Prompt " + settings.admin_password) == result
    assert gemini.calls == len(observations) == 1
    observation = observations[0]
    assert settings.admin_password not in json.dumps(observation)
    if api_error:
        assert result["api_status"] == "api_error" and result["http_code"] == 429
        assert observation["level"] == "ERROR"
    else:
        assert observation["usage_details"] == {"input": 10, "output": 5, "total": 15}
        assert observation["metadata"]["response_model"] == "gemini-test-version"
        assert observation["output"] == "Báo cáo"
