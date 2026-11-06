"""Kiểm tra auth qua Next dev rewrites thật, không đi tắt bằng Nginx.

Chạy từ repo root: .venv/bin/python FE/tests/dev_proxy_check.py
BE dùng artifact thật và tài khoản/runtime tạm; không đọc BE/.env.
"""

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import httpx
import pandas as pd
import uvicorn

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from BE.config import Settings
from BE.main import create_app
from BE.tests.conftest import FakeGeminiClient
from FE.tests.browser_check import free_port


def main():
    with tempfile.TemporaryDirectory(prefix="iot-next-dev-proxy-") as temporary:
        directory = Path(temporary)
        settings = Settings(
            runtime_dir=directory / "runtime", admin_username="proxy-tester",
            admin_password="temporary-proxy-password", gemini_pause_seconds=0,
        )
        gemini = FakeGeminiClient()
        app = create_app(settings, gemini_client=gemini)
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        backend_port = listener.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(app, log_level="error"))
        worker = threading.Thread(target=lambda: server.run(sockets=[listener]), daemon=True)
        worker.start()
        next_server = None
        try:
            deadline = time.monotonic() + 45
            while not server.started:
                assert worker.is_alive() and time.monotonic() < deadline, "BE kiểm thử chưa sẵn sàng"
                time.sleep(0.1)
            # Project tối thiểu dùng đúng next.config.ts và node_modules của FE.
            # Build cache nằm trong thư mục tạm, không ảnh hưởng Next của người dùng.
            project = directory / "frontend"
            (project / "app").mkdir(parents=True)
            (project / "node_modules").symlink_to(ROOT / "FE/node_modules", target_is_directory=True)
            for name in ["next.config.ts", "package.json"]:
                shutil.copyfile(ROOT / "FE" / name, project / name)
            (project / "app/layout.tsx").write_text(
                'export default function Layout({children}: {children: React.ReactNode}) { return <html><body>{children}</body></html>; }'
            )
            (project / "app/page.tsx").write_text('export default function Page() { return <p>Proxy test</p>; }')
            node = Path.home() / ".nvm/versions/node/v22.23.4/bin/node"
            if not node.is_file():
                node = Path(shutil.which("node") or "node")
            next_port = free_port()
            with (directory / "next.log").open("w+") as log:
                next_server = subprocess.Popen(
                    [str(node), str(ROOT / "FE/node_modules/next/dist/bin/next"), "dev", "--webpack", "--hostname", "127.0.0.1", "--port", str(next_port)],
                    cwd=project,
                    env={**os.environ, "API_PROXY_TARGET": f"http://127.0.0.1:{backend_port}", "NEXT_TELEMETRY_DISABLED": "1"},
                    stdout=log, stderr=log,
                )
                base = f"http://127.0.0.1:{next_port}"
                with httpx.Client(base_url=base, timeout=30) as client:
                    deadline = time.monotonic() + 40
                    while True:
                        try:
                            if client.get("/health").status_code == 200:
                                break
                        except httpx.TransportError:
                            pass
                        assert next_server.poll() is None and time.monotonic() < deadline, "Next dev kiểm thử chưa sẵn sàng"
                        time.sleep(0.2)
                    headers = {"Origin": base, "Sec-Fetch-Site": "same-origin"}
                    credentials = {"username": settings.admin_username, "password": settings.admin_password}
                    response = client.post("/api/auth/login", json=credentials, headers=headers)
                    assert response.status_code == 200, f"Login qua Next: {response.status_code} {response.text}"
                    assert "HttpOnly" in response.headers["set-cookie"]
                    assert client.get("/api/auth/session").json()["username"] == settings.admin_username
                    source = pd.read_csv(settings.shap_dir / "selected_input.csv").head(1).to_csv(index=False).encode()
                    uploaded = client.post("/api/runs", files={"file": ("proxy.csv", source, "text/csv")}, headers=headers)
                    assert uploaded.status_code == 202, uploaded.text
                    rejected = client.post("/api/auth/logout", json={}, headers={**headers, "Origin": "https://external.invalid"})
                    assert rejected.status_code == 403
                    forged = client.post("/api/auth/logout", json={}, headers={**headers, "Origin": "https://external.invalid", "X-Forwarded-Host": "external.invalid"})
                    assert forged.status_code == 403
                    assert client.get("/api/auth/session").status_code == 200
                    assert client.post("/api/auth/logout", json={}, headers=headers).status_code == 200
                    assert client.get("/api/auth/session").status_code == 401
                    assert app.state.manager.runtime.load_count == 1
                    assert not gemini.calls
                    result = {
                        "passed": True, "transport": "Next dev rewrites -> loopback FastAPI",
                        "checks": ["login", "cookie session", "multipart upload", "cross-origin rejection", "spoofed forwarded-host rejection", "logout"],
                        "model_load_count": 1, "gemini_calls": 0,
                    }
                    output = ROOT / "FE/tests/results/dev_proxy_checks.json"
                    output.parent.mkdir(exist_ok=True)
                    output.write_text(json.dumps(result, indent=2))
                    print(json.dumps(result, indent=2), flush=True)
        finally:
            if next_server is not None:
                next_server.terminate()
                try:
                    next_server.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    next_server.kill()
                    next_server.wait()
            server.should_exit = True
            worker.join(timeout=20)


if __name__ == "__main__":
    main()
