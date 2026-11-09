"""Đường dẫn artifact và cấu hình đọc từ môi trường server."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


REPO_DIR = Path(__file__).resolve().parent.parent
CLASS_NAMES = ["Normal", "BruteForce", "DDoS", "DoS", "Mirai", "Recon", "Spoofing", "Web-Based"]
BASE_NAMES = ["DT", "RF", "HGB"]
MODEL_ID = "XGB_d4_n200"
XGB_RUN_ID = "xgb_meta_20261021_092334_9024562d"
SHAP_RUN_ID = "shap_20261022_021654_2555e479"
INTEGRATION_RUN_ID = "integration_20261022_075217_0b67d48f"


@dataclass
class Settings:
    xgb_dir: Path = REPO_DIR / "output/stacking_meta_runs" / XGB_RUN_ID
    shap_dir: Path = REPO_DIR / "output/xai_shap_runs" / SHAP_RUN_ID
    integration_dir: Path = REPO_DIR / "output/integration_runs" / INTEGRATION_RUN_ID
    runtime_dir: Path = REPO_DIR / "BE/runtime"
    admin_username: str = "admin"
    admin_password: str = field(default="", repr=False)
    gemini_api_key: str = field(default="", repr=False)
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_pause_seconds: float = 4.0
    host: str = "127.0.0.1"
    port: int = 8000
    ssl_certfile: str = ""
    ssl_keyfile: str = ""
    threads: int = 2
    max_input_rows: int = 1000
    max_upload_bytes: int = 10 * 1024 * 1024
    max_explain_rows: int = 50
    prediction_batch_size: int = 4096
    langfuse_enabled: bool = False
    langfuse_public_key: str = field(default="", repr=False)
    langfuse_secret_key: str = field(default="", repr=False)
    langfuse_base_url: str = "https://cloud.langfuse.com"
    langfuse_capture_content: bool = True
    langfuse_environment: str = "nidr-local"


def load_settings():
    load_dotenv(REPO_DIR / "BE/.env", override=False)
    load_dotenv(REPO_DIR / ".env.observability", override=False)
    settings = Settings()
    for name in ["xgb_dir", "shap_dir", "integration_dir", "runtime_dir"]:
        value = os.getenv(name.upper())
        if value:
            setattr(settings, name, Path(value).expanduser().resolve())
    settings.admin_username = os.getenv("ADMIN_USERNAME", "admin")
    settings.admin_password = os.getenv("ADMIN_PASSWORD", "")
    settings.gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    settings.gemini_model = os.getenv("GEMINI_MODEL", settings.gemini_model)
    settings.gemini_pause_seconds = float(os.getenv("GEMINI_PAUSE_SECONDS", "4"))
    settings.host = os.getenv("HOST", "127.0.0.1")
    settings.port = int(os.getenv("PORT", "8000"))
    settings.ssl_certfile = os.getenv("SSL_CERTFILE", "")
    settings.ssl_keyfile = os.getenv("SSL_KEYFILE", "")
    settings.langfuse_enabled = os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"
    settings.langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip()
    settings.langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY", "").strip()
    settings.langfuse_base_url = os.getenv("LANGFUSE_BASE_URL", settings.langfuse_base_url).rstrip("/")
    settings.langfuse_capture_content = os.getenv("LANGFUSE_CAPTURE_CONTENT", "true").lower() == "true"
    settings.langfuse_environment = os.getenv("LANGFUSE_ENVIRONMENT", "nidr-local")
    if not settings.admin_username or not settings.admin_password:
        raise ValueError("Đặt ADMIN_USERNAME và ADMIN_PASSWORD trong BE/.env hoặc biến môi trường.")
    if settings.gemini_pause_seconds < 0:
        raise ValueError("GEMINI_PAUSE_SECONDS không được âm.")
    return settings
