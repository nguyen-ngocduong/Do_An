"""Langfuse Cloud là tùy chọn; lỗi quan sát không làm hỏng suy luận."""

from contextlib import contextmanager
import logging
import os


logger = logging.getLogger(__name__)
CLOUD_URLS = {"https://cloud.langfuse.com", "https://us.cloud.langfuse.com"}


class Observation:
    def __init__(self, span, settings):
        self.span = span
        self.settings = settings
        self.trace_id = getattr(span, "trace_id", None)

    def clean(self, value):
        if isinstance(value, str):
            # Không để khóa lọt qua prompt/output, kể cả khi một thư viện trả lại chúng.
            for secret in [self.settings.admin_password, self.settings.gemini_api_key,
                           self.settings.langfuse_secret_key, self.settings.langfuse_public_key]:
                if secret:
                    value = value.replace(secret, "[REDACTED]")
            return value[:32000]
        if isinstance(value, dict):
            return {key: self.clean(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [self.clean(item) for item in value[:100]]
        return value

    def update(self, **fields):
        if self.span is None:
            return
        try:
            self.span.update(**self.clean(fields))
        except Exception as error:
            logger.warning("Không cập nhật được trace (%s).", type(error).__name__)


class Telemetry:
    def __init__(self, settings, client=None):
        self.settings = settings
        self.client = client
        self.problem = None
        if client is not None or not settings.langfuse_enabled:
            return
        if not settings.langfuse_public_key or not settings.langfuse_secret_key:
            self.problem = "missing_keys"
            logger.warning("Chưa điền khóa Langfuse; NIDR tiếp tục chạy bình thường.")
            return
        if settings.langfuse_base_url not in CLOUD_URLS:
            self.problem = "invalid_cloud_url"
            logger.warning("LANGFUSE_BASE_URL phải là endpoint Cloud EU hoặc US.")
            return
        try:
            # SDK export nền. Queue đầy sẽ bỏ telemetry, không chặn worker model.
            os.environ.setdefault("OTEL_BSP_MAX_QUEUE_SIZE", "128")
            from langfuse import Langfuse
            from langfuse.span_filter import is_langfuse_span
            from opentelemetry.sdk.trace import TracerProvider

            self.client = Langfuse(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                base_url=settings.langfuse_base_url,
                timeout=3, flush_at=16, flush_interval=5,
                media_upload_thread_count=1, environment=settings.langfuse_environment, release="nidr-1.8.0",
                tracer_provider=TracerProvider(), should_export_span=is_langfuse_span,
            )
        except Exception as error:
            self.problem = "initialization_failed"
            logger.warning("Không khởi tạo được Langfuse (%s).", type(error).__name__)

    def status(self):
        return {"enabled": self.settings.langfuse_enabled,
                "active": self.client is not None,
                "capture_content": self.settings.langfuse_capture_content,
                "problem": self.problem,
                "note": "active là SDK đã khởi tạo, không khẳng định Cloud đã nhận trace."}

    @contextmanager
    def span(self, name, metadata=None, generation=False, model=None):
        context = None
        span = None
        if self.client is not None:
            try:
                context = self.client.start_as_current_observation(
                    name=name, as_type="generation" if generation else "span",
                    metadata=metadata, model=model,
                )
                span = context.__enter__()
            except Exception as error:
                context = None
                logger.warning("Không mở được trace (%s).", type(error).__name__)
        observation = Observation(span, self.settings)
        try:
            yield observation
        except Exception as error:
            observation.update(level="ERROR", status_message=type(error).__name__)
            raise
        finally:
            if context is not None:
                try:
                    # Không đưa nguyên exception ứng dụng/HTTP có thể chứa bí mật vào SDK.
                    context.__exit__(None, None, None)
                except Exception as error:
                    logger.warning("Không đóng được trace (%s).", type(error).__name__)

    def close(self):
        if self.client is not None:
            try:
                self.client.shutdown()
            except Exception as error:
                logger.warning("Không flush được trace khi dừng (%s).", type(error).__name__)
