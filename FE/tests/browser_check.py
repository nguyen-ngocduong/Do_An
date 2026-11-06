"""Kiểm thử FE bằng Chrome thật, BE/model thật và Gemini giả lập.

Chạy từ repo root: .venv/bin/python FE/tests/browser_check.py
Server chỉ tồn tại trong lượt kiểm thử, dùng cổng và runtime tạm riêng.
"""

import base64
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import zipfile
from pathlib import Path

import httpx
import pandas as pd
import numpy as np
import uvicorn
from websockets.sync.client import connect

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from BE.config import Settings
from BE.main import create_app
from BE.tests.conftest import FakeGeminiClient


class Browser:
    """Các lệnh CDP nhỏ để kiểm tra DOM, upload và chụp viewport."""

    def __init__(self, connection):
        self.connection = connection
        self.next_id = 0
        self.errors = []

    def send_command(self, method, params):
        self.next_id += 1
        self.connection.send(json.dumps({"id": self.next_id, "method": method, "params": params}))
        return self.next_id

    def call(self, method, params=None):
        command_id = self.send_command(method, params or {})
        while True:
            result = json.loads(self.connection.recv(timeout=35))
            if result.get("method") == "Runtime.exceptionThrown":
                self.errors.append(result["params"]["exceptionDetails"])
            if result.get("method") == "Runtime.consoleAPICalled":
                console_event = result["params"]
                if console_event["type"] == "error":
                    self.errors.append({
                        "source": "console.error",
                        "messages": [argument.get("description", argument.get("value")) for argument in console_event["args"]],
                        "stackTrace": console_event.get("stackTrace"),
                    })
            if result.get("id") == command_id:
                if "error" in result:
                    raise AssertionError(result["error"])
                return result.get("result", {})

    def evaluate(self, expression):
        result = self.call("Runtime.evaluate", {"expression": expression, "returnByValue": True, "awaitPromise": True})
        if "exceptionDetails" in result:
            raise AssertionError(result["exceptionDetails"])
        return result.get("result", {}).get("value")

    def wait(self, expression, timeout=30):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.evaluate(expression):
                return
            time.sleep(0.1)
        raise AssertionError(f"Không đạt điều kiện: {expression}\nURL: {self.evaluate('location.href')}\nDOM: {self.evaluate('document.documentElement.outerHTML')[-3500:]}\nJS errors: {self.errors}")

    def click(self, selector):
        self.wait(f"Boolean(document.querySelector({json.dumps(selector)}))")
        self.evaluate(f"document.querySelector({json.dumps(selector)}).click()")

    def change(self, selector, value):
        self.evaluate(f"(()=>{{const node=document.querySelector({json.dumps(selector)});const proto=node.tagName==='SELECT'?HTMLSelectElement.prototype:node.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;Object.getOwnPropertyDescriptor(proto,'value').set.call(node,{json.dumps(value)});node.dispatchEvent(new Event(node.tagName==='SELECT'?'change':'input',{{bubbles:true}}));}})()")

    def upload(self, path):
        document = self.call("DOM.getDocument")
        node = self.call("DOM.querySelector", {"nodeId": document["root"]["nodeId"], "selector": "#csv-file"})
        self.call("DOM.setFileInputFiles", {"nodeId": node["nodeId"], "files": [str(path)]})

    def scroll_to(self, selector):
        self.wait(f"Boolean(document.querySelector({json.dumps(selector)}))")
        self.wait("!document.querySelector('.loading')")
        self.evaluate(f"""(() => {{
            const target = document.querySelector({json.dumps(selector)});
            const main = document.querySelector('#main-content');
            if (getComputedStyle(main).overflowY === 'auto') {{
                window.scrollTo(0, 0);
                main.scrollTop += target.getBoundingClientRect().top - main.getBoundingClientRect().top - 20;
            }} else {{
                target.scrollIntoView({{block: 'start'}});
                window.scrollBy(0, -16);
            }}
        }})()""")
        if selector == '.site-footer':
            # Đợi bố cục ổn định sau khi API tải xong, rồi cuộn hết vùng nội dung.
            time.sleep(0.3)
            self.evaluate("""(() => {
                const main = document.querySelector('#main-content');
                if (getComputedStyle(main).overflowY === 'auto') {
                    main.scrollTop = main.scrollHeight;
                    window.scrollTo(0, 0);
                }
            })()""")

    def screenshot(self, path, width=1280, height=720):
        self.call("Emulation.setDeviceMetricsOverride", {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False})
        time.sleep(0.15)
        assert self.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"Tràn ngang: {path.name}"
        small_text = self.evaluate("""[...document.querySelectorAll('body *')].filter(node => node.getClientRects().length && [...node.childNodes].some(child => child.nodeType === 3 && child.textContent.trim())).filter(node => parseFloat(getComputedStyle(node).fontSize) < 11.99).map(node => ({tag: node.tagName, size: getComputedStyle(node).fontSize, text: node.textContent.slice(0, 70)}))""")
        assert not small_text, f"Chữ nhỏ dưới 12 px trong {path.name}: {small_text}"
        image = self.call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
        path.write_bytes(base64.b64decode(image["data"]))


def free_port():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def main():
    chrome_path = shutil.which("google-chrome") or shutil.which("chromium")
    if not chrome_path:
        raise SystemExit("Cần Google Chrome hoặc Chromium để chạy kiểm thử này.")
    output = ROOT / "FE/tests/results"
    output.mkdir(exist_ok=True)
    checks = []

    def record(message):
        checks.append(message)
        print("PASS:", message, flush=True)
    gemini = FakeGeminiClient()
    with tempfile.TemporaryDirectory(prefix="iot-frontend-check-") as temporary:
        directory = Path(temporary)
        settings = Settings(runtime_dir=directory / "runtime", admin_username="browser-tester", admin_password="browser-test-password", gemini_pause_seconds=0)
        app = create_app(settings, gemini_client=gemini)
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
        worker = threading.Thread(target=lambda: server.run(sockets=[listener]), daemon=True)
        worker.start()
        chrome = None
        next_server = None
        gateway_name = f"iot-sentinel-e2e-{os.getpid()}"
        gateway_started = False
        next_log = (directory / "next.log").open("w+")
        try:
            deadline = time.monotonic() + 45
            while not server.started:
                if not worker.is_alive() or time.monotonic() > deadline:
                    raise AssertionError("Server kiểm thử không khởi động được.")
                time.sleep(0.1)
            # Bản production Next, Nginx TLS và BE đều trên máy này, cổng/runtime tạm.
            next_port = free_port()
            gateway_port = free_port()
            node = Path.home() / ".nvm/versions/node/v22.23.4/bin/node"
            if not node.is_file():
                node = Path(shutil.which("node") or "node")
            next_server = subprocess.Popen([str(node), ".next/standalone/server.js"], cwd=ROOT / "FE", env={**os.environ, "HOSTNAME": "127.0.0.1", "PORT": str(next_port)}, stdout=next_log, stderr=next_log)
            certificate = directory / "tls"
            certificate.mkdir()
            subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1", "-subj", "/CN=localhost", "-addext", "subjectAltName=IP:127.0.0.1,DNS:localhost", "-keyout", str(certificate / "server.key"), "-out", str(certificate / "server.crt")], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            config = (ROOT / "FE/deploy/nginx.conf").read_text().replace("listen 443 ssl", f"listen 127.0.0.1:{gateway_port} ssl").replace("127.0.0.1:8000", f"127.0.0.1:{port}").replace("127.0.0.1:3000", f"127.0.0.1:{next_port}")
            (directory / "nginx.conf").write_text(config)
            docker_args = ["docker", "run", "--rm", "--network", "host", "-v", f"{directory / 'nginx.conf'}:/etc/nginx/nginx.conf:ro", "-v", f"{certificate}:/etc/nginx/tls:ro"]
            subprocess.run(docker_args + ["nginx:1.28-alpine", "nginx", "-t"], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(docker_args + ["-d", "--name", gateway_name, "nginx:1.28-alpine"], check=True, stdout=subprocess.DEVNULL)
            gateway_started = True
            base = f"https://127.0.0.1:{gateway_port}"
            with httpx.Client(verify=str(certificate / "server.crt"), auth=(settings.admin_username, settings.admin_password)) as probe:
                deadline = time.monotonic() + 30
                while True:
                    try:
                        if probe.get(base + "/runs").status_code == 200:
                            break
                    except httpx.TransportError:
                        pass
                    assert time.monotonic() < deadline, "Next/Nginx chưa sẵn sàng"
                    time.sleep(0.2)
            record("Nginx -t, Next standalone, TLS và deep-link production hoạt động")
            profile = directory / "chrome"
            chrome = subprocess.Popen([chrome_path, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--no-first-run", "--ignore-certificate-errors", "--remote-debugging-port=0", f"--user-data-dir={profile}", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            deadline = time.monotonic() + 15
            while not (profile / "DevToolsActivePort").is_file():
                assert time.monotonic() < deadline
                time.sleep(0.1)
            debug_port = (profile / "DevToolsActivePort").read_text().splitlines()[0]
            with urllib.request.urlopen(f"http://127.0.0.1:{debug_port}/json") as response:
                targets = json.load(response)
                target = next(item for item in targets if item["type"] == "page" and item["url"] == "about:blank")
            with connect(target["webSocketDebuggerUrl"], max_size=20 * 1024 * 1024) as connection, httpx.Client(base_url=base, auth=(settings.admin_username, settings.admin_password), timeout=60, verify=str(certificate / "server.crt")) as http:
                browser = Browser(connection)
                browser.call("Runtime.enable")
                browser.call("Page.enable")
                downloads = directory / "downloads"
                downloads.mkdir()
                browser.call("Browser.setDownloadBehavior", {"behavior": "allow", "downloadPath": str(downloads)})
                for path in ["/", "/dashboard", "/runs", "/alerts"]:
                    denied = http.get(path, auth=None)
                    assert denied.status_code == 302 and "/login" in denied.headers["location"]
                for path in ["/api/schema", "/docs", "/openapi.json"]:
                    denied = http.get(path, auth=None)
                    assert denied.status_code == 401, (path, denied.status_code)
                    assert http.get(path, auth=("browser-tester", "wrong")).status_code == 401
                for path in ["/login", "/icon.svg"]:
                    assert http.get(path, auth=None).status_code == 200
                for path in ["/BE/.env", "/output/README.md", "/FE/PLAN.md", "/_be_auth", "/login/redirect"]:
                    assert http.get(path).status_code == 404, path
                assert http.get("/api/model").json()["checks"]["golden_prediction_match"]
                record("Cổng chung chuyển trang riêng tư tới đăng nhập, bảo vệ API/Swagger và xác minh golden model")
                for size, expected in [(10 * 1024 * 1024 - 1, 422), (10 * 1024 * 1024 + 1, 413), (11 * 1024 * 1024 + 1, 413)]:
                    response = http.post("/api/runs", files={"file": ("boundary.csv", b"x" * size, "text/csv")})
                    assert response.status_code == expected, (size, response.status_code, response.text[:150])
                header = ",".join(http.get("/api/schema").json()["feature_names"])
                too_many = header + "\n" + ((",".join(["0"] * 46) + "\n") * 1001)
                assert http.post("/api/runs", files={"file": ("too_many.csv", too_many, "text/csv")}).status_code == 422
                record("Upload sát 10 MiB qua Nginx, quá dung lượng và 1.001 dòng bị từ chối đúng")
                # Trình duyệt đăng nhập bằng form thật, không chèn Basic vào request.
                browser.call("Page.navigate", {"url": base + "/runs/new"})
                browser.wait("Boolean(document.querySelector('#login-username'))")
                assert browser.evaluate("document.querySelector('#login-username').placeholder") == "admin"
                assert browser.evaluate("Boolean(document.querySelector('#login-password').placeholder)")
                assert browser.evaluate("document.querySelector('#login-remember').checked") is False
                browser.screenshot(output / "login-wide.png", 1920, 1080)
                browser.screenshot(output / "login-desktop.png")
                browser.screenshot(output / "login-mobile.png", 390, 844)
                assert browser.evaluate("document.querySelectorAll('.site-footer').length") == 1
                browser.scroll_to('.site-footer')
                browser.screenshot(output / "site-footer-login-mobile.png", 390, 844)
                browser.evaluate("document.querySelector('.login-page').scrollTo(0, 0); window.scrollTo(0, 0)")
                browser.click("#theme-toggle")
                browser.screenshot(output / "login-dark.png", 1280, 900)
                browser.click("#theme-toggle")
                browser.screenshot(output / "login-desktop.png")
                login_button_top = browser.evaluate("document.querySelector('#login-submit').getBoundingClientRect().top")
                browser.click(".login-support-link")
                browser.wait("!document.querySelector('#login-support').hidden")
                browser.screenshot(output / "login-support.png")
                browser.click(".login-support-link")
                browser.click("#login-submit")
                browser.wait("document.querySelector('#login-error')?.innerText.includes('Vui lòng nhập')")
                assert browser.evaluate("document.activeElement.id") == "login-username"
                assert abs(browser.evaluate("document.querySelector('#login-submit').getBoundingClientRect().top") - login_button_top) < 1
                browser.change("#login-username", settings.admin_username)
                browser.change("#login-password", "wrong-password")
                browser.click('[aria-label="Hiện mật khẩu"]')
                assert browser.evaluate("document.querySelector('#login-password').type") == "text"
                browser.click('[aria-label="Ẩn mật khẩu"]')
                browser.call("Network.enable")
                browser.call("Network.emulateNetworkConditions", {"offline": False, "latency": 3000, "downloadThroughput": -1, "uploadThroughput": -1})
                browser.click("#login-submit")
                browser.wait("document.querySelector('#login-submit').disabled && Boolean(document.querySelector('.login-spinner'))")
                browser.screenshot(output / "login-submitting.png")
                browser.call("Network.emulateNetworkConditions", {"offline": False, "latency": 0, "downloadThroughput": -1, "uploadThroughput": -1})
                browser.wait("document.querySelector('#login-error')?.innerText.includes('không đúng')")
                assert abs(browser.evaluate("document.querySelector('#login-submit').getBoundingClientRect().top") - login_button_top) < 1
                browser.screenshot(output / "login-error.png")
                browser.change("#login-password", settings.admin_password)
                browser.click("#login-submit")
                browser.wait("location.pathname === '/runs/new' && Boolean(document.querySelector('#csv-file'))")
                cookie = next(item for item in browser.call("Network.getCookies")["cookies"] if item["name"] == "iot_session")
                assert cookie["httpOnly"] and cookie["secure"] and cookie["sameSite"] == "Strict"
                assert cookie["session"] is True
                assert "iot_session" not in browser.evaluate("document.cookie")
                assert settings.admin_password not in browser.evaluate("JSON.stringify(localStorage) + JSON.stringify(sessionStorage)")
                browser.call("Page.reload")
                browser.wait("Boolean(document.querySelector('#csv-file'))")
                record("Form đăng nhập: placeholder, trợ giúp, spinner, lỗi không nhảy nút, session cookie và quay về đúng trang")
                # Next giữ HTTP 200 nếu shell đã stream trước notFound(); kiểm tra boundary 404.
                for path in ["/runs/invalid/monitor", "/runs/" + "a" * 32 + "/rows/-1"]:
                    invalid = http.get(path)
                    assert invalid.status_code in [200, 404]
                    assert "Không tìm thấy trang" in invalid.text
                    assert invalid.status_code == 404 or "NEXT_HTTP_ERROR_FALLBACK;404" in invalid.text
                # Chỉ dùng tài khoản fixture; không đọc BE/.env hay đặt header cho CDN bên ngoài.
                browser.call("Page.navigate", {"url": base + "/runs/invalid/monitor"})
                browser.wait("document.body.innerText.includes('Không tìm thấy trang')")
                browser.call("Page.navigate", {"url": base + "/runs"})
                browser.wait("document.body.innerText.includes('Chưa có lần chạy')")
                assert not browser.evaluate("document.body.innerText.includes('Đã kết nối server')")
                record("HTTP Basic, lịch sử trống và không hiện trạng thái kết nối thành công")
                browser.screenshot(output / "history-empty-desktop.png")
                browser.click('#primary-navigation a[href="/dashboard"]')
                browser.wait("document.querySelectorAll('#dashboard-metrics dd').length === 4")
                assert browser.evaluate("Array.from(document.querySelectorAll('#dashboard-metrics dd')).every(node => node.textContent.trim() === '0')")
                assert browser.evaluate("document.body.innerText.includes('Chưa có mẫu trong khoảng đã chọn')")
                browser.screenshot(output / "dashboard-empty-desktop.png")
                browser.screenshot(output / "dashboard-empty-mobile.png", 390, 844)
                browser.screenshot(output / "dashboard-empty-desktop.png")
                browser.click('#primary-navigation a[href="/runs"]')
                browser.wait("location.pathname === '/runs' && document.body.innerText.includes('Chưa có lần chạy')")
                record("Dashboard trống hiện số 0, không dựng tỷ lệ giả, có hướng dẫn tải CSV và không lỗi chart")

                # Giống Page Agent: mở trang trong tab nền, vẫn phải tải phiên/dữ liệu lần đầu.
                browser.call("Page.bringToFront")
                background_id = browser.call("Target.createTarget", {"url": "about:blank", "background": True})["targetId"]
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{debug_port}/json") as response:
                        background_target = next(item for item in json.load(response) if item["id"] == background_id)
                    with connect(background_target["webSocketDebuggerUrl"], max_size=20 * 1024 * 1024) as background_connection:
                        background_browser = Browser(background_connection)
                        background_browser.call("Runtime.enable")
                        background_browser.call("Page.enable")
                        background_browser.call("Page.navigate", {"url": base + "/runs"})
                        browser.call("Page.bringToFront")
                        background_browser.wait("document.hidden && Boolean(document.querySelector('#sidebar-toggle')) && document.body.innerText.includes('Chưa có lần chạy')")
                        assert not background_browser.errors, background_browser.errors
                finally:
                    browser.call("Target.closeTarget", {"targetId": background_id})
                record("Tab nền giống Page Agent vẫn tải phiên/dữ liệu ban đầu và hiện sidebar")
                expanded_width = browser.evaluate("document.querySelector('main').getBoundingClientRect().width")
                browser.click("#sidebar-toggle")
                browser.wait("document.querySelector('#sidebar-toggle').getAttribute('aria-expanded') === 'false' && Math.abs(document.querySelector('.sidebar').getBoundingClientRect().width - 88) < 1")
                assert browser.evaluate("document.querySelector('main').getBoundingClientRect().width") > expanded_width + 130
                assert browser.evaluate("[...document.querySelectorAll('#primary-navigation a')].every(link => link.getAttribute('aria-label') && link.title && getComputedStyle(link.querySelector('.nav-short-label')).display !== 'none')")
                browser.screenshot(output / "sidebar-collapsed-desktop.png")
                browser.click('#primary-navigation a[href="/runs/new"]')
                browser.wait("Boolean(document.querySelector('#create-form'))")
                assert browser.evaluate("document.querySelector('.app-shell').dataset.sidebar === 'collapsed'")
                browser.call("Page.reload")
                browser.wait("Boolean(document.querySelector('#create-form')) && document.querySelector('.app-shell')?.dataset.sidebar === 'collapsed'")
                assert browser.evaluate("localStorage.getItem('nidr:sidebar') === 'collapsed'")
                browser.screenshot(output / "sidebar-collapsed-tablet.png", 768, 1024)
                browser.screenshot(output / "sidebar-collapsed-mobile.png", 390, 844)
                assert browser.evaluate("getComputedStyle(document.querySelector('#navigation-toggle')).display !== 'none' && getComputedStyle(document.querySelector('.sidebar-heading .brand')).display !== 'none'")
                browser.screenshot(output / "sidebar-collapsed-wide.png", 1920, 1080)
                browser.click("#theme-toggle")
                browser.screenshot(output / "sidebar-collapsed-dark.png")
                browser.click("#theme-toggle")
                browser.evaluate("document.querySelector('#sidebar-toggle').focus()")
                browser.call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13, "text": "\r"})
                browser.call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
                browser.wait("document.querySelector('#sidebar-toggle').getAttribute('aria-expanded') === 'true' && Math.abs(document.querySelector('.sidebar').getBoundingClientRect().width - 248) < 1")
                browser.screenshot(output / "sidebar-expanded-desktop.png")
                record("Sidebar desktop rộng/gọn bằng chuột và Enter, tăng diện tích nội dung, giữ lựa chọn qua chuyển trang/reload và độc lập Menu mobile")
                browser.click('a[href="/runs/new"]')
                browser.wait("Boolean(document.querySelector('#create-form'))")
                browser.screenshot(output / "upload-desktop.png")
                browser.screenshot(output / "upload-mobile.png", 390, 844)
                assert browser.evaluate("document.querySelector('#navigation-toggle').getAttribute('aria-expanded') === 'false' && getComputedStyle(document.querySelector('#primary-navigation')).display === 'none'")
                browser.click("#navigation-toggle")
                browser.wait("document.querySelector('#navigation-toggle').getAttribute('aria-expanded') === 'true'")
                browser.screenshot(output / "navigation-mobile-open.png", 390, 844)
                browser.evaluate("document.querySelector('#primary-navigation a').focus()")
                browser.call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Escape", "code": "Escape", "windowsVirtualKeyCode": 27})
                browser.wait("document.querySelector('#navigation-toggle').getAttribute('aria-expanded') === 'false'")
                assert browser.evaluate("document.activeElement.id === 'navigation-toggle'")
                browser.click("#navigation-toggle")
                browser.click('#primary-navigation a[href="/runs"]')
                browser.wait("location.pathname === '/runs'")
                assert browser.evaluate("document.querySelector('#navigation-toggle').getAttribute('aria-expanded') === 'false'")
                browser.click("#navigation-toggle")
                browser.click('#primary-navigation a[href="/runs/new"]')
                browser.wait("Boolean(document.querySelector('#create-form'))")
                record("Menu mobile mở/đóng, Escape trả focus và chọn trang đóng menu")
                browser.screenshot(output / "upload-tablet.png", 768, 1024)
                browser.screenshot(output / "upload-1440.png", 1440, 900)
                assert browser.evaluate("document.querySelector('.upload-contract h2').textContent") == "Đầu vào"
                assert browser.evaluate("getComputedStyle(document.querySelector('main')).borderTopWidth === '0px' && getComputedStyle(document.querySelector('main')).backgroundColor === getComputedStyle(document.body).backgroundColor")
                browser.screenshot(output / "upload-desktop.png")
                bad = directory / "bad.csv"
                bad.write_text("a,b\n1,2\n")
                browser.upload(bad)
                browser.click("#create-submit")
                browser.wait("!document.querySelector('#upload-error').hidden")
                assert http.get("/api/runs").json()["total"] == 0
                record("CSV sai bị từ chối, giữ form và không tạo run")
                source = pd.read_csv(settings.shap_dir / "selected_input.csv")
                samples = pd.concat([source, source, source, source.head(2)], ignore_index=True)
                sample_path = directory / "browser_50.csv"
                samples.to_csv(sample_path, index=False)
                browser.upload(sample_path)
                browser.wait("document.querySelector('.selected-file')?.innerText.includes('browser_50.csv')")
                browser.click('[aria-label="Bỏ file đã chọn"]')
                browser.wait("document.querySelector('.selected-file') === null")
                assert browser.evaluate("document.activeElement.id") == "choose-csv"
                browser.upload(sample_path)
                browser.wait("document.querySelector('.selected-file')?.innerText.includes('browser_50.csv')")
                browser.screenshot(output / "upload-selected-desktop.png")
                browser.click("#create-submit")
                browser.wait("location.pathname.includes('/monitor')")
                browser.wait("document.body.innerText.includes('50 / 50')")
                run_id = browser.evaluate("location.pathname.split('/')[2]")
                assert http.get(f"/api/runs/{run_id}").json()["processed_rows"] == 50
                assert http.get(f"/runs/{run_id}/predictions").status_code == 200
                expected = pd.read_csv(settings.shap_dir / "golden_predictions.csv")
                actual = http.get(f"/api/runs/{run_id}/predictions?limit=1000").json()["items"][:16]
                assert [item["predicted_class"] for item in actual] == expected["class_name"].tolist()
                for name in http.get("/api/schema").json()["class_names"]:
                    np.testing.assert_allclose([item["probabilities"][name] for item in actual], expected["prob_" + name], rtol=1e-6, atol=1e-7)
                record("Upload CSV 50 dòng và Batch hoàn tất; nhãn/tám xác suất khớp golden")
                browser.click('#primary-navigation a[href="/dashboard"]')
                browser.wait("Boolean(document.querySelector('#dashboard-metrics dd'))")
                dashboard = http.get("/api/dashboard").json()
                expected_metrics = [str(dashboard["metrics"][key]) for key in ["predicted_rows", "suspected_rows", "pending_alerts", "shap_rows"]]
                assert browser.evaluate("Array.from(document.querySelectorAll('#dashboard-metrics dd')).map(node => node.textContent.trim())") == expected_metrics
                assert dashboard["metrics"]["predicted_rows"] == 50
                assert len(dashboard["class_counts"]) == 8
                assert browser.evaluate("Boolean(document.querySelector('.latest-run-summary'))")
                assert browser.evaluate("Array.from(document.querySelectorAll('.latest-run-summary dd')).map(node => node.textContent)") == ["50", "50", "0", "Batch"]
                assert browser.evaluate("document.querySelectorAll('.class-pie-legend li').length") == 8
                assert browser.evaluate("Array.from(document.querySelectorAll('.class-pie-legend strong')).reduce((total, node) => total + Number(node.firstChild.textContent), 0)") == 50
                footer_text = browser.evaluate("document.querySelector('.site-footer').innerText")
                for value in ["Nguyễn Ngọc Dương", "B22DCVT112", "D22VTHI02", "Hà Minh Hải", "B22DCVT173", "D22VTMD03", "Tạ Trung Kiên", "B22DCVT265", "D22VTMD01", "Kỹ thuật Điện tử Viễn thông", "Chính quy", "Nhóm số 07"]:
                    assert value in footer_text
                # Fixture FE riêng để nhìn đủ đường KDE và tỷ lệ70%; không sửa dữ liệu BE.
                fixture = json.loads(json.dumps(dashboard))
                fixture["class_counts"] = {"Normal": 1, "BruteForce": 0, "DDoS": 35, "DoS": 10, "Mirai": 3, "Recon": 0, "Spoofing": 1, "Web-Based": 0}
                fixture["metrics"].update({"normal_rows": 1, "suspected_rows": 49, "suspected_percentage": 98, "shap_rows": 30})
                fixture["explanation_counts"] = {"not_requested": 20, "queued": 2, "shap_running": 1, "gemini_running": 0, "completed": 18, "partial": 7, "failed": 2, "interrupted": 0}
                fixture["gemini_counts"] = {"accepted": 18, "not_requested": 27, "api_error": 3, "needs_text_review": 2}
                fixture["saved_reviews"] = 11
                fixture["review_counts"] = {"not_reviewed": 40, "agree": 8, "disagree": 1, "uncertain": 1}
                fixture["proposed_labels"] = 1
                amounts = [0, 5, 8, 12, 15, 10, 0]
                for index, day in enumerate(fixture["daily_activity"]):
                    normal = 1 if index == 1 else 0
                    day.update({"total_rows": amounts[index], "normal_rows": normal, "suspected_rows": amounts[index] - normal})
                (output / 'light-dashboard-fixture.json').write_text(json.dumps(fixture, ensure_ascii=False, indent=2))
                browser.evaluate(f"window.__nidFixture = {json.dumps(fixture)}")
                browser.evaluate("""(() => {
                    window.__nidOriginalFetch = window.fetch;
                    window.fetch = async (input, init) => {
                        const response = await window.__nidOriginalFetch(input, init);
                        const url = typeof input === 'string' ? input : input.url;
                        if (url.includes('/api/dashboard') && response.ok) {
                            return new Response(JSON.stringify(window.__nidFixture), {status:200, headers:{'Content-Type':'application/json'}});
                        }
                        return response;
                    };
                })()""")
                browser.click('#dashboard-refresh')
                browser.wait("document.querySelectorAll('.class-pie path').length === 5 && document.querySelector('.class-pie-legend').textContent.includes('70%')")
                assert browser.evaluate("document.querySelectorAll('.class-pie text').length") == 0
                browser.wait("Boolean(document.querySelector('.chart-kde-path'))")
                assert not browser.evaluate("document.querySelector('.activity-chart').outerHTML.includes('NaN')")
                browser.scroll_to('.nid-dashboard')
                browser.screenshot(output / 'light-dashboard-fixture-wide.png', 1440, 900)
                browser.screenshot(output / 'light-dashboard-fixture-1280.png', 1280, 900)
                browser.scroll_to('.dashboard-pipeline')
                browser.screenshot(output / 'light-dashboard-pipeline.png', 1440, 900)
                browser.click('.dashboard-pipeline details > summary')
                assert browser.evaluate("document.querySelector('.dashboard-pipeline details').open")
                browser.screenshot(output / 'light-dashboard-pipeline-details.png', 1440, 900)
                browser.click('.dashboard-pipeline details > summary')
                browser.click('#theme-toggle')
                browser.scroll_to('.nid-dashboard')
                browser.screenshot(output / 'light-dashboard-fixture-dark.png', 1440, 900)
                browser.scroll_to('.dashboard-pipeline')
                browser.screenshot(output / 'light-dashboard-pipeline-dark.png', 1440, 900)
                browser.scroll_to('.site-footer')
                assert browser.evaluate("getComputedStyle(document.querySelector('.site-footer')).backgroundColor === getComputedStyle(document.querySelector('.dashboard-pipeline')).backgroundColor")
                browser.screenshot(output / 'light-dashboard-footer-dark.png', 1440, 900)
                browser.click('#theme-toggle')
                for width, height, label in [(768, 1024, 'tablet'), (390,844,'mobile'),(320,760,'small')]:
                    browser.call('Emulation.setDeviceMetricsOverride', {'width':width,'height':height,'deviceScaleFactor':1,'mobile':False})
                    browser.scroll_to('.dashboard-charts')
                    browser.wait("Math.abs(document.querySelector('.activity-chart').viewBox.baseVal.width - document.querySelector('.activity-chart').getBoundingClientRect().width) < 2")
                    browser.screenshot(output / f'light-dashboard-charts-{label}.png', width, height)
                    browser.scroll_to('.dashboard-pipeline')
                    browser.screenshot(output / f'light-dashboard-pipeline-{label}.png', width, height)
                browser.call('Emulation.setDeviceMetricsOverride', {'width':1440,'height':900,'deviceScaleFactor':1,'mobile':False})
                browser.scroll_to('.site-footer')
                assert browser.evaluate("getComputedStyle(document.querySelector('.site-footer')).backgroundColor") == 'rgb(255, 255, 255)'
                assert not browser.evaluate("document.querySelector('.sidebar').textContent.includes('XGBoost') || document.querySelector('.sidebar').textContent.includes('Model đã chốt')")
                browser.screenshot(output / 'light-dashboard-footer.png', 1440, 900)
                browser.evaluate("window.fetch = window.__nidOriginalFetch; delete window.__nidFixture; delete window.__nidOriginalFetch")
                browser.click('#dashboard-refresh')
                browser.wait("!document.querySelector('.chart-kde-path')")
                browser.scroll_to('.nid-dashboard')
                assert not gemini.calls
                record('Sidebar bỏ metadata model; footer theo theme; pie70% và cột/KDE trên fixtureFE đa-ngày; pipeline/details responsive, đọc không gọi Gemini')

                browser.screenshot(output / "dashboard-wide.png", 1440, 900)
                assert browser.evaluate("['dashboard-alerts-title','dashboard-runs-title'].every(id => document.getElementById(id).getBoundingClientRect().bottom <= innerHeight)"), "Dashboard 1440: tiêu đề hai bảng phải thấy trong viewport đầu"
                browser.screenshot(output / "dashboard-desktop.png", 1280, 900)
                assert browser.evaluate("['dashboard-alerts-title','dashboard-runs-title'].every(id => document.getElementById(id).getBoundingClientRect().bottom <= innerHeight)"), "Dashboard 1280: tiêu đề hai bảng phải thấy trong viewport đầu"
                browser.screenshot(output / "dashboard-user-1024.png", 1024, 768)
                assert browser.evaluate("new Set(Array.from(document.querySelectorAll('#dashboard-metrics > div')).map(node => Math.round(node.getBoundingClientRect().top))).size") == 1
                browser.screenshot(output / "dashboard-tablet.png", 768, 1024)
                assert browser.evaluate("document.querySelector('#dashboard-filters select[name=run_id]').getBoundingClientRect().width >= 320")
                browser.change('#dashboard-filters select[name="run_id"]', run_id)
                browser.screenshot(output / "dashboard-tablet-selected.png", 768, 1024)
                browser.change('#dashboard-filters select[name="run_id"]', "")
                browser.screenshot(output / "dashboard-mobile.png", 390, 844)
                browser.evaluate("document.querySelector('.dashboard-charts').scrollIntoView()")
                browser.screenshot(output / "dashboard-mobile-charts.png", 390, 844)
                browser.screenshot(output / "dashboard-mobile-small.png", 320, 760)
                browser.wait("Math.abs(document.querySelector('.activity-chart').viewBox.baseVal.width - document.querySelector('.activity-chart').getBoundingClientRect().width) < 2")

                browser.evaluate("document.querySelector('.dashboard-recent').scrollIntoView()")
                browser.screenshot(output / "dashboard-mobile-recent.png", 390, 844)
                browser.evaluate("document.querySelector('.dashboard-pipeline').scrollIntoView()")
                browser.screenshot(output / "dashboard-mobile-pipeline.png", 390, 844)
                browser.evaluate("window.scrollTo(0, 0)")

                browser.wait("Math.abs(document.querySelector('.activity-chart').viewBox.baseVal.width - document.querySelector('.activity-chart').getBoundingClientRect().width) < 2")
                browser.screenshot(output / "dashboard-wide.png", 1440, 900)
                browser.click("#theme-toggle")
                browser.screenshot(output / "dashboard-dark.png", 1440, 900)
                browser.scroll_to('.site-footer')
                browser.screenshot(output / "dashboard-footer-dark.png", 1440, 900)
                browser.click("#theme-toggle")
                browser.scroll_to('.dashboard-recent')
                browser.screenshot(output / "dashboard-lower-desktop.png", 1440, 900)
                browser.scroll_to('.site-footer')
                assert browser.evaluate("document.querySelector('.topbar').getBoundingClientRect().top >= 0")
                browser.screenshot(output / "dashboard-footer-desktop.png", 1440, 900)
                browser.call("Emulation.setDeviceMetricsOverride", {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": False})
                browser.scroll_to('.site-footer')
                browser.screenshot(output / "dashboard-footer-mobile-topic.png", 390, 844)
                browser.scroll_to('.site-footer-team')
                browser.screenshot(output / "dashboard-footer-mobile-team.png", 390, 844)
                browser.call("Emulation.setDeviceMetricsOverride", {"width": 320, "height": 760, "deviceScaleFactor": 1, "mobile": False})
                browser.scroll_to('.site-footer-team')
                browser.screenshot(output / "dashboard-footer-mobile-small.png", 320, 760)
                browser.call("Emulation.setDeviceMetricsOverride", {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False})
                browser.evaluate("document.querySelector('.nid-dashboard').scrollIntoView({block:'start'})")
                record("Dashboard: pie đủ tám lớp/tổng thật; footer theo theme đủ thông tin nhóm, mobile và theme tối")
                for route in ["/runs", "/runs/new", "/alerts", "/dashboard"]:
                    browser.click(f'.site-footer-links a[href="{route}"]')
                    browser.wait(f"location.pathname === {json.dumps(route)} && Boolean(document.querySelector('#primary-navigation'))")
                    assert browser.evaluate("document.querySelectorAll('.site-footer').length") == 1
                for suffix, image_name in [("monitor", "monitor"), ("predictions", "predictions"), ("rows/0", "sample"), ("export", "export")]:
                    browser.evaluate(f"location.href = {json.dumps(base + '/runs/' + run_id + '/' + suffix)}")
                    browser.wait(f"location.pathname.endsWith({json.dumps('/' + suffix)}) && Boolean(document.querySelector('#primary-navigation'))")
                    assert browser.evaluate("document.querySelectorAll('.site-footer').length") == 1
                    browser.scroll_to('.site-footer')
                    browser.screenshot(output / f"site-footer-{image_name}.png", 1440, 900)
                browser.evaluate(f"location.href = {json.dumps(base + '/runs')}")
                browser.wait("location.pathname === '/runs' && Boolean(document.querySelector('#primary-navigation'))")
                browser.scroll_to('.site-footer')
                browser.screenshot(output / "site-footer-history.png", 1440, 900)
                browser.click('.site-footer-links a[href="/runs/new"]')
                browser.wait("location.pathname === '/runs/new'")
                browser.scroll_to('.site-footer')
                browser.screenshot(output / "site-footer-upload.png", 1440, 900)
                browser.click('.site-footer-links a[href="/alerts"]')
                browser.wait("location.pathname === '/alerts'")
                browser.scroll_to('.site-footer')
                browser.screenshot(output / "site-footer-alerts.png", 1440, 900)
                browser.evaluate(f"location.href = {json.dumps(base + '/trang-khong-ton-tai')}")
                browser.wait("document.body.innerText.includes('Không tìm thấy trang') && Boolean(document.querySelector('.site-footer'))")
                assert browser.evaluate("document.querySelectorAll('.site-footer').length") == 1
                browser.screenshot(output / "site-footer-not-found.png", 1440, 900)
                browser.click('.site-footer-links a[href="/dashboard"]')
                browser.wait("location.pathname === '/dashboard' && Boolean(document.querySelector('#dashboard-metrics dd'))")
                assert len(gemini.calls) == 0
                record("Footer chung: liên kết thật và đúng một footer trên lịch sử/tạo run/cảnh báo/theo dõi/dự đoán/mẫu/xuất/404, không gọi Gemini")
                browser.change('#dashboard-filters select[name="period"]', "today")
                browser.change('#dashboard-filters select[name="run_id"]', run_id)
                browser.click('#dashboard-filters button[type="submit"]')
                browser.wait("location.search.includes('period=today') && document.querySelectorAll('.activity-chart g[tabindex]').length === 1")
                browser.call("Page.reload")
                browser.wait("document.querySelector('#dashboard-filters select[name=run_id]')?.value === '" + run_id + "' && Boolean(document.querySelector('#dashboard-metrics dd'))")
                browser.change('#dashboard-filters select[name="period"]', "all")
                browser.change('#dashboard-filters select[name="run_id"]', "")
                browser.click('#dashboard-filters button[type="submit"]')
                browser.wait("document.querySelectorAll('.activity-chart g[tabindex]').length === 30")
                browser.evaluate("document.querySelector('.activity-chart g[tabindex]').focus()")
                browser.click('.dashboard-data-table summary')
                assert browser.evaluate("document.querySelectorAll('.dashboard-data-table tbody tr').length") == 30
                assert len(gemini.calls) == 0
                browser.click('.dashboard-data-table summary')
                record("Dashboard: số liệu khớp API, bộ lọc/URL giữ qua reload, chart ngày và tám lớp; mobile/dark và không gọi Gemini")
                browser.evaluate(f"location.href='/runs/{run_id}/monitor'")
                browser.wait("Boolean(document.querySelector('#run-overview'))")

                browser.screenshot(output / "monitor-wide.png", 1920, 1080)
                assert browser.evaluate("""(() => {
                    const cards = [...document.querySelectorAll('.monitor-panels > .panel')].map(node => node.getBoundingClientRect());
                    const stats = [...document.querySelectorAll('.monitor-stat')].map(node => node.getBoundingClientRect());
                    const progress = document.querySelector('progress');
                    return cards.length === 2 && Math.abs(cards[0].bottom - cards[1].bottom) < 1
                        && stats.length === 4 && stats.every((card, index) => index === 0 || card.left > stats[index - 1].right)
                        && document.querySelector('#run-overview').contains(progress)
                        && document.querySelector('.monitor-recent .monitor-card-heading a').textContent.includes('Xem bảng dự đoán');
                })()""")
                browser.screenshot(output / "monitor-mobile.png", 390, 844)
                assert browser.evaluate("""(() => {
                    const cards = [...document.querySelectorAll('.monitor-panels > .panel')].map(node => node.getBoundingClientRect());
                    return cards[1].top > cards[0].bottom && document.querySelectorAll('.monitor-class-row').length === 8;
                })()""")
                browser.screenshot(output / "monitor-desktop.png")
                record("Theo dõi: tiến độ trong thẻ file, bốn ô thống kê riêng, hai panel cùng đáy trên desktop và xếp dọc trên mobile")
                browser.click(f'a[href="/runs/{run_id}/predictions"]')
                browser.wait("document.querySelectorAll('[data-select-row]').length === 20")
                browser.click('[data-page="next"]')
                browser.wait("Boolean(document.querySelector('[data-select-row=\"20\"]'))")
                browser.click('[data-page="prev"]')
                browser.wait("Boolean(document.querySelector('[data-select-row=\"0\"]'))")
                record("Phân trang đúng row_index")
                browser.change("#prediction-jump-row", "#000024")
                browser.click(".prediction-jump button")
                browser.wait("new URLSearchParams(location.search).get('row') === '24' && Boolean(document.querySelector('[data-select-row=\"24\"]'))")
                browser.wait("document.querySelector('#peek .peek-identity').innerText.includes('#000024')")
                browser.change("#prediction-jump-row", "#999999")
                browser.click(".prediction-jump button")
                browser.wait("document.querySelector('#page-message')?.innerText.includes('chưa có kết quả dự đoán')")
                assert browser.evaluate("new URLSearchParams(location.search).get('row')") == "24"
                browser.change("#prediction-jump-row", "#000000")
                browser.click(".prediction-jump button")
                browser.wait("new URLSearchParams(location.search).get('row') === '0' && Boolean(document.querySelector('[data-select-row=\"0\"]'))")
                assert not gemini.calls
                record("Đi tới dòng đổi đúng trang/mẫu, từ chối dòng chưa dự đoán và không gọi Gemini")
                browser.change("#class-filter", "Web-Based")
                browser.wait("document.querySelectorAll('[data-select-row]').length === 3")
                assert http.get(f"/api/runs/{run_id}/predictions?predicted_class=Web-Based").json()["total"] == 3
                browser.change("#class-filter", "")
                browser.wait("document.querySelectorAll('[data-select-row]').length === 20")
                for row in [0, 2, 14]:
                    browser.click(f'[data-select-row="{row}"]')
                browser.click('[data-peek-row="14"]')
                browser.wait("document.querySelector('#peek').innerText.includes('Web-Based')")
                browser.click("#close-peek")
                assert browser.evaluate("document.querySelectorAll('[data-select-row]:checked').length") == 3
                browser.click('[data-peek-row="14"]')
                assert browser.evaluate("document.querySelector('#peek-toggle') === null")
                assert browser.evaluate("Array.from(document.querySelectorAll('#prediction-table th')).some(node => node.textContent.trim() === 'Giải thích')")
                browser.screenshot(output / "bulk-selection-desktop.png")
                browser.screenshot(output / "bulk-selection-mobile.png", 390, 844)
                browser.screenshot(output / "bulk-selection-desktop.png")
                browser.change("#audience-filter", "basic")
                browser.wait("document.querySelector('#audience-filter').value === 'basic'")
                assert browser.evaluate("document.querySelector('#bulk-action .bulk-audience strong').innerText") == "Kỹ thuật"
                assert browser.evaluate("document.querySelector('#bulk-action select') === null")
                assert not browser.evaluate("document.querySelector('#bulk-action').innerText.includes('Thêm diễn giải tiếng Việt')")
                browser.click("#explain-selected")
                browser.wait("document.querySelector('#bulk-action').hidden")
                browser.wait("document.querySelector('#audience-filter').value === 'technical'")
                deadline = time.monotonic() + 90
                while True:
                    browser.evaluate("true")
                    states = http.get(f"/api/runs/{run_id}/explanations").json()["items"]
                    if len(states) == 3 and all(item["status"] == "completed" for item in states):
                        break
                    assert time.monotonic() < deadline, states
                    time.sleep(0.2)
                assert not gemini.calls
                assert http.get(f"/api/runs/{run_id}/explanations?audience_level=basic").json()["total"] == 0
                browser.click('#peek [data-tab="shap"]')
                browser.wait("document.querySelector('#peek').innerText.includes('IAT')")
                assert browser.evaluate("document.querySelectorAll('#peek .shap-peek-track').length") == 3
                record("Lọc lớp, chọn nhiều dòng độc lập xem nhanh, SHAP thật cho Normal/BruteForce/Web-Based")
                browser.screenshot(output / "predictions-desktop.png")
                browser.scroll_to('.pagehead')
                browser.wait("Boolean(document.querySelector('.prediction-timing time'))")
                assert browser.evaluate("document.querySelector('.prediction-timing time').dateTime") == actual[0]["created_at"]
                assert browser.evaluate("document.querySelector('.prediction-timing small').textContent.startsWith('Bình quân batch:')")
                browser.screenshot(output / "predictions-1440.png", 1440, 900)
                browser.screenshot(output / "predictions-tablet.png", 768, 1024)
                browser.screenshot(output / "predictions-mobile.png", 390, 844)
                browser.screenshot(output / "predictions-desktop.png")
                browser.click('[data-select-row="2"]')
                browser.evaluate("document.querySelector('#main-content').scrollTop=180")
                browser.wait(f"JSON.parse(sessionStorage.getItem('iot:next:table:{run_id}') || '{{}}').scrollTop === 180")
                browser.click("#peek .peek-footer a")
                browser.wait("location.pathname.includes('/rows/14') && new URLSearchParams(location.search).get('stage') === 'overview'")
                browser.click('[data-stage="shap"]')
                browser.wait("location.pathname.includes('/rows/14') && document.querySelector('#stage-content').innerText.includes('IAT')")
                browser.call("Page.reload")
                browser.wait("Boolean(document.querySelector('#stage-content .waterfall-row'))")
                record("Refresh deep-link mẫu production giữ đúng run/dòng/bằng chứng")
                assert browser.evaluate("getComputedStyle(document.querySelector('[data-stage=\"shap\"]')).backgroundColor !== 'rgba(0, 0, 0, 0)'")
                browser.click('[data-tab="input"]')
                browser.wait("Boolean(document.querySelector('#stage-content .json-view'))")
                values = json.loads(browser.evaluate("document.querySelector('#stage-content .json-view').value"))
                assert len(values) == 46 and "label" not in values
                assert values == http.get(f"/api/runs/{run_id}/inputs/14").json()["features"]
                browser.screenshot(output / "input-desktop.png")
                browser.click('[data-tab="metadata"]')
                browser.wait("document.querySelector('#stage-content').innerText.includes('max_evals')")
                browser.click('[data-tab="output"]')
                browser.screenshot(output / "explanation-desktop.png")
                browser.screenshot(output / "explanation-mobile.png", 390, 844)
                browser.evaluate("document.querySelector('#stage-content').scrollIntoView()")
                browser.screenshot(output / "explanation-mobile-evidence.png", 390, 844)
                browser.screenshot(output / "explanation-desktop.png")
                record("46 đặc trưng, SHAP/metadata đúng mẫu và desktop/mobile không tràn ngang")
                assert browser.evaluate("document.querySelector('#detail-audience') === null")
                assert not gemini.calls
                assert http.get(f"/api/runs/{run_id}/explanations?audience_level=basic").json()["total"] == 0
                browser.click("#detail-use-gemini")
                browser.click("#explain-one")
                deadline = time.monotonic() + 45
                while True:
                    browser.evaluate("true")
                    state = http.get(f"/api/runs/{run_id}/explanations/14?audience_level=technical").json()
                    if state.get("status") in ["completed", "partial"] and state.get("use_gemini"):
                        assert state["gemini_status"] == "accepted", state
                        break
                    assert time.monotonic() < deadline, state
                    time.sleep(0.1)
                assert len(gemini.calls) == 1
                browser.click('[data-stage="gemini"]')
                browser.wait("document.querySelector('#stage-content').innerText.includes('Các đặc trưng nổi bật')")
                browser.screenshot(output / "gemini-desktop.png")
                browser.screenshot(output / "gemini-report-wide.png", 1920, 1080)
                browser.screenshot(output / "gemini-report-mobile.png", 390, 844)
                browser.evaluate("document.querySelector('.gemini-report').scrollIntoView()")
                browser.screenshot(output / "gemini-report-mobile-content.png", 390, 844)
                browser.screenshot(output / "gemini-desktop.png")
                result = state["gemini"]
                paragraphs = [result["tom_tat"], result["so_sanh_hai_lop"]["dien_giai"], result["tong_hop_shap"]["dien_giai"]]
                paragraphs += [item["dien_giai"] for item in result["giai_thich_dac_trung"]]
                paragraphs += [text for item in result["de_xuat_kiem_tra"] for text in [item["nguon_du_lieu"], item["noi_dung_can_kiem_tra"], item["muc_dich"]]]
                paragraphs += result["gioi_han"]
                for text in paragraphs:
                    assert browser.evaluate(f"document.querySelector('.gemini-report').textContent.includes({json.dumps(text)})")
                assert browser.evaluate("getComputedStyle(document.querySelector('.gemini-playbook')).display !== 'none' && !document.querySelector('.gemini-playbook').open")

                browser.click('[data-artifact="explanation.json"]')
                browser.wait("Boolean(document.querySelector('#artifact-preview .json-view'))")
                expected_json = http.get(state["files"]["explanation.json"]).json()
                assert json.loads(browser.evaluate("document.querySelector('#artifact-preview .json-view').value")) == expected_json
                browser.click('[data-artifact="top5_features.csv"]')
                browser.wait("document.querySelectorAll('#artifact-preview tbody tr').length === 5")
                expected_csv = pd.read_csv(__import__('io').StringIO(http.get(state["files"]["top5_features.csv"]).text), dtype=str).fillna("")
                actual_csv = browser.evaluate("Array.from(document.querySelectorAll('#artifact-preview tbody tr')).map(row => Array.from(row.querySelectorAll('td')).map(cell => cell.dataset.rawValue))")
                assert actual_csv == expected_csv.values.tolist()
                assert browser.evaluate("Array.from(document.querySelectorAll('#artifact-preview tbody td')).some(cell => cell.textContent !== cell.dataset.rawValue)")
                browser.scroll_to('#case-files')
                browser.screenshot(output / "video-polish-csv-desktop.png", 1440, 900)
                browser.click('[data-artifact="report_vi.md"]')
                browser.wait("Boolean(document.querySelector('#artifact-preview .artifact-markdown strong'))")
                expected_markdown = http.get(state["files"]["report_vi.md"]).text
                browser.scroll_to('#case-files')
                browser.screenshot(output / "video-polish-markdown-desktop.png", 1440, 900)
                browser.call("Emulation.setDeviceMetricsOverride", {"width": 768, "height": 1024, "deviceScaleFactor": 1, "mobile": False})
                browser.scroll_to('#case-files')
                browser.screenshot(output / "video-polish-markdown-tablet.png", 768, 1024)
                browser.call("Emulation.setDeviceMetricsOverride", {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": False})
                browser.scroll_to('#case-files')
                browser.screenshot(output / "video-polish-markdown-mobile.png", 390, 844)
                browser.call("Emulation.setDeviceMetricsOverride", {"width": 320, "height": 760, "deviceScaleFactor": 1, "mobile": False})
                browser.scroll_to('#case-files')
                browser.screenshot(output / "video-polish-markdown-small.png", 320, 760)
                browser.call("Emulation.setDeviceMetricsOverride", {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False})
                browser.scroll_to('#case-files')
                browser.click('#theme-toggle')
                browser.screenshot(output / "video-polish-markdown-dark.png", 1440, 900)
                browser.click('#theme-toggle')
                browser.click('.artifact-view-mode button:nth-child(2)')
                browser.wait("Boolean(document.querySelector('#artifact-preview .artifact-source'))")
                assert browser.evaluate("document.querySelector('#artifact-preview .artifact-source').textContent") == expected_markdown
                browser.screenshot(output / "video-polish-source.png", 1440, 900)
                browser.click('.artifact-view-mode button:first-child')
                browser.wait("Boolean(document.querySelector('#artifact-preview .artifact-markdown'))")
                stage_url = browser.evaluate("location.href")
                calls_before_scroll = len(gemini.calls)
                browser.scroll_to('#case-files')
                browser.wait("document.querySelector('.section-outline a[aria-current=location]')?.getAttribute('href') === '#case-files'")
                browser.scroll_to('#human-review')
                browser.wait("document.querySelector('.section-outline a[aria-current=location]')?.getAttribute('href') === '#human-review'")
                assert browser.evaluate("document.querySelector('.section-outline').getBoundingClientRect().top >= 0")
                browser.screenshot(output / "video-polish-outline.png", 1440, 900)
                browser.click('.section-outline a[href="#stage-content"]')
                browser.wait("document.querySelector('.section-outline a[aria-current=location]')?.getAttribute('href') === '#stage-content'")
                assert browser.evaluate("location.href") == stage_url
                assert len(gemini.calls) == calls_before_scroll
                record("Markdown render định dạng và nguồn khớp file; CSV hiển thị gọn, dữ liệu gốc giữ nguyên; mục lục cuộn không đổi stage/URL hoặc gọi Gemini")
                browser.click('[data-artifact="waterfall.png"]')
                browser.evaluate("document.querySelector('#case-files').scrollIntoView()")
                browser.wait("document.querySelector('#artifact-preview img')?.naturalWidth > 0")
                browser.evaluate("document.querySelector('#case-files').scrollIntoView()")
                browser.screenshot(output / "artifact-preview-desktop.png")
                browser.call("Emulation.setDeviceMetricsOverride", {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": False})
                browser.evaluate("document.querySelector('#case-files').scrollIntoView()")
                browser.screenshot(output / "artifact-preview-mobile.png", 390, 844)
                browser.screenshot(output / "artifact-preview-desktop.png")
                record("Xem trước đúng JSON/CSV/Markdown/PNG của mẫu; JSON và năm dòng CSV khớp tệp gốc")

                current_review = http.get(f"/api/runs/{run_id}/human-reviews/14").json()
                browser.wait(f"document.querySelector('#human-review')?.dataset.evidenceSignature === '{current_review['context']['evidence_signature']}'")
                assert browser.evaluate("document.querySelector('#review-decision').value") == "not_reviewed"
                assert browser.evaluate("document.querySelector('[data-review-rating=\"explanation_clarity\"]').value") == ""
                browser.change("#reviewer-name", "Người kiểm tra mẫu")
                browser.change("#review-decision", "uncertain")
                browser.change('[data-review-rating="explanation_clarity"]', "4")
                browser.change("#review-notes", "Cần đối chiếu nhật ký <script>window.reviewInjected=true</script>")
                browser.click("#review-confirm")
                browser.click("#save-human-review")
                browser.wait("document.querySelector('#human-review .review-status').innerText.includes('Đã lưu bởi')")
                saved_review = http.get(f"/api/runs/{run_id}/human-reviews/14").json()["review"]
                assert saved_review["prediction_assessment"] == "uncertain" and saved_review["explanation_clarity"] == 4
                assert saved_review["evidence_faithfulness"] is None
                browser.click('[data-filename="human_review_row_14_technical.json"]')
                deadline = time.monotonic() + 10
                while not (downloads / "human_review_row_14_technical.json").is_file():
                    assert time.monotonic() < deadline
                    browser.evaluate("true")
                    time.sleep(0.1)
                downloaded_review = json.loads((downloads / "human_review_row_14_technical.json").read_text())
                assert downloaded_review["review"] == saved_review
                browser.evaluate("document.querySelector('#human-review').scrollIntoView()")
                browser.screenshot(output / "human-review-desktop.png")
                browser.call("Emulation.setDeviceMetricsOverride", {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": False})
                browser.evaluate("document.querySelector('#human-review').scrollIntoView()")
                browser.screenshot(output / "human-review-mobile.png", 390, 844)
                browser.screenshot(output / "human-review-desktop.png")
                browser.call("Page.reload")
                browser.wait("document.querySelector('#reviewer-name')?.value === 'Người kiểm tra mẫu'")
                assert browser.evaluate("document.querySelector('#review-notes').value") == saved_review["notes"]
                assert not browser.evaluate("Boolean(window.reviewInjected)")
                assert len(gemini.calls) == 1
                record("Human review không tự chấm; lưu SQLite đúng mẫu, reload giữ dữ liệu, tải JSON khớp bản lưu và không đổi dự đoán/Gemini")

                record("Trang mẫu cố định Kỹ thuật; Gemini giả lập chỉ chạy sau nút yêu cầu, dùng lại SHAP")
                # Giữ kiểm tra khả năng đọc các báo cáo Basic cũ từ bảng/xuất kết quả.
                assert http.post(f"/api/runs/{run_id}/explanations", json={"row_indices": [14], "audience_level": "basic", "use_gemini": True}).status_code == 202
                deadline = time.monotonic() + 45
                while http.get(f"/api/runs/{run_id}/explanations/14?audience_level=basic").json().get("gemini_status") != "accepted":
                    assert time.monotonic() < deadline
                    browser.evaluate("true")
                    time.sleep(0.1)
                assert len(gemini.calls) == 2
                browser.click("#theme-toggle")
                assert browser.evaluate("document.documentElement.dataset.theme") == "dark"
                browser.screenshot(output / "explanation-dark.png")
                browser.click("#theme-toggle")
                browser.click('.pagehead a[href^="/runs/"]')
                browser.wait("Boolean(document.querySelector('#class-filter'))")
                assert browser.evaluate("document.querySelector('#audience-filter').value") == "technical"
                browser.wait("document.querySelector('#peek').innerText.includes('Dòng #000014')")
                assert browser.evaluate("new URLSearchParams(location.search).get('row')") == "14"
                browser.wait("Boolean(document.querySelector('[data-select-row=\"2\"]'))")
                browser.wait("document.querySelector('[data-select-row=\"2\"]')?.checked && document.querySelector('#main-content').scrollTop === 180")
                record("Quay về bảng giữ mức, dòng xem nhanh, checkbox và vị trí cuộn")
                browser.change("#audience-filter", "basic")
                browser.click('#peek [data-tab="gemini"]')
                browser.wait("document.querySelector('#peek-full-results')?.getAttribute('href').includes('audience=basic') && Boolean(document.querySelector('#peek .gemini-more'))")
                assert browser.evaluate("document.querySelector('#peek .gemini-more').getAttribute('aria-expanded')") == "false"
                pane_height = browser.evaluate("document.querySelector('#peek').getBoundingClientRect().height")
                assert pane_height <= 642
                assert browser.evaluate("document.querySelector('#peek .gemini-more').getBoundingClientRect().bottom <= document.querySelector('#peek .peek-body').getBoundingClientRect().bottom + 1")
                browser.screenshot(output / "gemini-preview-desktop.png")
                browser.click("#peek .gemini-more")
                browser.wait("document.querySelector('#peek .reading') !== null")
                assert abs(browser.evaluate("document.querySelector('#peek').getBoundingClientRect().height") - pane_height) < 1
                assert browser.evaluate("document.querySelector('#peek .peek-body').scrollHeight > document.querySelector('#peek .peek-body').clientHeight")
                browser.screenshot(output / "gemini-expanded-desktop.png")
                browser.click("#peek .gemini-more")
                browser.wait("document.querySelector('#peek .reading') === null")
                assert len(gemini.calls) == 2
                record("Gemini Xem thêm/Thu gọn giữ chiều cao panel, cuộn riêng và không gọi API mới")
                browser.change("#audience-filter", "technical")
                browser.wait("document.querySelector('#audience-filter').value === 'technical' && location.search.includes('audience=technical')")
                browser.click('[data-peek-row="14"]')
                browser.wait("document.querySelector('#peek').innerText.includes('Web-Based')")
                browser.click("#peek .peek-footer a")
                browser.wait("Boolean(document.querySelector('#sample-outcome a'))")
                browser.click("#sample-outcome a")
                browser.wait("Boolean(document.querySelector('#alert-note'))")
                browser.change("#alert-note", "Đã kiểm tra mẫu thử <script>window.unwanted=true</script>")
                assert browser.evaluate("document.querySelector('.alert-note-heading small').textContent.trim()") == "57 / 2.000"
                browser.click('[data-alert-status="acknowledged"]')
                browser.wait("Boolean(document.querySelector('[data-alert-status=\"closed\"]'))")
                browser.click('[data-alert-status="closed"]')
                browser.wait("document.querySelector('#confirm-dialog').open")
                browser.click("#confirm-accept")
                browser.wait("document.querySelector('#alert-detail').innerText.includes('Mở lại cảnh báo')")
                browser.click('[data-alert-status="acknowledged"].primary')
                browser.wait("Boolean(document.querySelector('[data-alert-status=\"closed\"]'))")
                assert not browser.evaluate("Boolean(window.unwanted)")
                record("Tiếp nhận, ghi chú, đóng có xác nhận, mở lại; chuỗi HTML được giữ dạng văn bản")
                browser.wait("document.querySelector('#toast').hidden")
                browser.screenshot(output / "alerts-desktop.png")
                browser.screenshot(output / "alerts-mobile.png", 390, 844)
                browser.screenshot(output / "alerts-desktop.png")
                browser.click("#close-alert")
                browser.wait("document.querySelector('#alert-detail').hidden")
                browser.click("[data-alert]")
                browser.wait("!document.querySelector('#alert-detail').hidden && Boolean(document.querySelector('#alert-note'))")
                browser.change('#alert-filters select[name="class"]', "DDoS")
                browser.click('#alert-filters button[type="submit"]')
                browser.wait("document.querySelector('.alert-prediction h3')?.innerText === 'DDoS'")
                assert browser.evaluate("Array.from(document.querySelectorAll('#alert-list tbody tr td:first-child')).every(cell => /^#\\d{6}$/.test(cell.textContent.trim()))")
                scoped_run = browser.evaluate("new URLSearchParams(location.search).get('run_id') || ''")
                overview_counts = []
                for lifecycle in ["", "new", "acknowledged", "closed"]:
                    filters = {"run_id": scoped_run, "predicted_class": "DDoS", "limit": 1}
                    if lifecycle:
                        filters["status"] = lifecycle
                    overview_counts.append(http.get("/api/alerts", params=filters).json()["total"])
                expected_counts = json.dumps([str(value) for value in overview_counts])
                browser.wait(f"JSON.stringify(Array.from(document.querySelectorAll('#alert-overview dd')).map(node => node.textContent.trim())) === JSON.stringify({expected_counts})")
                assert browser.evaluate("!document.querySelector('.alert-run-context').open")
                browser.click('.alert-run-context summary')
                assert scoped_run in browser.evaluate("document.querySelector('.alert-run-context').textContent")
                browser.click('.alert-run-context summary')
                browser.click('.alert-history summary')
                assert browser.evaluate("document.querySelector('.alert-history').open && document.querySelectorAll('.alert-history li').length > 0")
                browser.click('.alert-history summary')
                record("Cảnh báo: cột chỉ mã mẫu, bốn tổng khớp API theo bộ lọc; UUID và lịch sử mở theo nhu cầu")
                browser.screenshot(output / "alerts-desktop.png")
                browser.screenshot(output / "alerts-wide.png", 1440, 900)
                browser.click("#theme-toggle")
                browser.screenshot(output / "alerts-dark.png", 1440, 900)
                browser.click('.alert-disclosure:not(.alert-history) summary')
                browser.wait("getComputedStyle(document.querySelector('#alert-detail .source-links a')).color === getComputedStyle(document.querySelector('#primary-navigation a[aria-current]')).color")
                browser.evaluate("document.querySelector('.alert-detail-body').scrollTop = document.querySelector('.alert-detail-body').scrollHeight")
                browser.screenshot(output / "alerts-dark-playbook.png", 1440, 900)
                browser.click('.alert-disclosure:not(.alert-history) summary')
                browser.evaluate("document.querySelector('.alert-detail-body').scrollTop = 0")
                browser.click("#theme-toggle")
                browser.screenshot(output / "alerts-tablet.png", 768, 1024)
                browser.screenshot(output / "alerts-mobile.png", 390, 844)
                browser.evaluate("document.querySelector('#alert-detail').scrollIntoView()")
                browser.screenshot(output / "alerts-mobile-detail.png", 390, 844)
                browser.screenshot(output / "alerts-desktop.png")
                browser.evaluate("document.querySelector('#alert-detail').scrollIntoView()")
                browser.screenshot(output / "alerts-detail-desktop.png")
                record("Nút x đóng panel cảnh báo, chọn dòng mở lại và lọc lớp đúng")
                browser.evaluate(f"location.href='/runs/{run_id}/export'")
                browser.wait("Boolean(document.querySelector('[data-filename$=\"_reports.zip\"]'))")
                assert browser.evaluate("document.querySelectorAll('.export-options .export-card').length") == 3
                assert browser.evaluate("document.querySelector('#export-snapshot').innerText.includes('50 / 50')")
                browser.screenshot(output / "export-desktop.png")
                browser.screenshot(output / "export-wide.png", 1920, 1080)
                browser.screenshot(output / "export-mobile.png", 390, 844)
                assert browser.evaluate("document.querySelector('#export-snapshot > div').getBoundingClientRect().width > 200")
                assert browser.evaluate("document.querySelector('.export-snapshot-note').getBoundingClientRect().top >= document.querySelector('#export-snapshot > div').getBoundingClientRect().bottom")
                browser.screenshot(output / "export-desktop.png")
                browser.click("#theme-toggle")
                browser.screenshot(output / "export-dark.png")
                browser.click("#theme-toggle")
                browser.click('[data-filename$="_predictions.csv"]')
                browser.wait("document.querySelector('#toast').innerText.includes('Đã tải')")
                browser.click('[data-filename$="_reports.zip"]')
                browser.wait("document.querySelector('#toast').innerText.includes('Đã tải')")
                deadline = time.monotonic() + 10
                while not (downloads / f"{run_id}_predictions.csv").is_file() or not (downloads / f"{run_id}_reports.zip").is_file():
                    assert time.monotonic() < deadline
                    time.sleep(0.1)
                assert len(pd.read_csv(downloads / f"{run_id}_predictions.csv")) == 50
                assert (downloads / f"{run_id}_reports.zip").is_file()
                with zipfile.ZipFile(downloads / f"{run_id}_reports.zip") as archive:
                    listed = browser.evaluate("Array.from(document.querySelector('#export-files > .table-wrap').querySelectorAll('tbody tr td:first-child')).map(node => node.textContent.trim())")
                    assert len(listed) == 8 and set(listed).issubset(set(archive.namelist()))
                record("Tải CSV 50 dòng và ZIP qua trình duyệt đã xác thực")
                count = len(gemini.calls)
                browser.change("#export-audience", "basic")
                browser.wait("document.querySelector('#export-case')?.value === '14' && Boolean(document.querySelector('#export-case-files'))")
                actual_files = http.get(f"/api/runs/{run_id}/explanations/14?audience_level=basic").json()["files"]
                displayed_files = browser.evaluate("Array.from(document.querySelectorAll('#export-case-files [data-filename]')).map(node => node.dataset.filename)")
                assert set(displayed_files) == set(actual_files)
                for filename in ["waterfall.png", "report_vi.md"]:
                    browser.click(f'#export-case-files [data-filename="{filename}"]')
                    deadline = time.monotonic() + 10
                    while not (downloads / filename).is_file():
                        assert time.monotonic() < deadline
                        browser.evaluate("true")
                        time.sleep(0.1)
                    assert (downloads / filename).stat().st_size > 20
                browser.evaluate("document.querySelector('#export-case-files').scrollIntoView()")
                browser.screenshot(output / "export-case-files-desktop.png")
                browser.screenshot(output / "export-case-files-mobile.png", 390, 844)
                browser.screenshot(output / "export-case-files-desktop.png")
                assert len(gemini.calls) == count
                record("Xuất: ba thẻ, danh mục khớp ZIP/API và đúng mẫu/mức, tải PNG/Markdown thật mà không gọi Gemini")
                for filename, file_url in state.get("files", {}).items():
                    if filename in ["waterfall.png", "report_vi.md"]:
                        response = http.get(file_url)
                        assert response.status_code == 200 and len(response.content) > 20
                        assert http.get(file_url, auth=None).status_code == 401
                record("PNG/Markdown đúng mức diễn giải tải được và được bảo vệ")
                # Kiểm tra Gemini lỗi vẫn giữ SHAP và không tự gọi lại API.
                gemini.behavior = "quota"
                browser.evaluate(f"location.href='/runs/{run_id}/rows/14?audience=technical&stage=gemini'")
                browser.wait("Boolean(document.querySelector('#retry-gemini')) && !document.querySelector('#retry-gemini').hidden")
                browser.click("#retry-gemini")
                browser.wait("document.querySelector('#confirm-dialog').open")
                browser.click("#confirm-accept")
                deadline = time.monotonic() + 30
                while True:
                    browser.evaluate("true")
                    state = http.get(f"/api/runs/{run_id}/explanations/14").json()
                    if state.get("status") == "partial":
                        assert state["explanation"] and state["gemini_status"] == "api_error"
                        break
                    assert time.monotonic() < deadline, state
                    time.sleep(0.1)
                browser.wait("document.querySelector('#stage-content').innerText.includes('Lỗi API')")
                browser.click('[data-stage="shap"]')
                browser.wait("document.querySelector('#stage-content').innerText.includes('IAT')")
                count = len(gemini.calls)
                for _ in range(35):
                    browser.evaluate("true")
                    time.sleep(0.1)
                assert len(gemini.calls) == count == 3
                record("Gemini 429 giữ SHAP, trạng thái partial và không tự retry")
                browser.screenshot(output / "partial-desktop.png")
                # Mất kết nối phải giữ nguyên bằng chứng đang đọc.
                browser.call("Network.enable")
                browser.call("Network.emulateNetworkConditions", {"offline": True, "latency": 0, "downloadThroughput": -1, "uploadThroughput": -1})
                browser.wait("!document.querySelector('#connection-error').hidden")
                assert browser.evaluate("document.querySelector('#stage-content').innerText.includes('IAT')")
                browser.call("Network.emulateNetworkConditions", {"offline": False, "latency": 0, "downloadThroughput": -1, "uploadThroughput": -1})
                browser.wait("document.querySelector('#connection-error').hidden")
                record("Ngoại tuyến giữ dữ liệu cuối; kết nối phục hồi chỉ đọc lại")
                # Replay điều khiển từ FE; không dùng runtime vận hành.
                replay_file = directory / "replay.csv"
                # Dừng ở giữa 50 dòng để kiểm tra cả bố cục khi Replay đang chạy.
                samples.to_csv(replay_file, index=False)
                browser.evaluate("location.href='/runs/new'")
                browser.wait("Boolean(document.querySelector('#csv-file'))")
                browser.upload(replay_file)
                browser.click('input[name="mode"][value="replay"]')
                browser.change("#interval", "1")
                browser.click("#create-submit")
                browser.wait("Boolean(document.querySelector('[data-control=\"pause\"]'))")
                replay_id = browser.evaluate("location.pathname.split('/')[2]")
                browser.wait("document.querySelector('progress')?.value >= 20", timeout=45)
                browser.screenshot(output / "replay-running-wide.png", 1920, 1080)
                browser.screenshot(output / "replay-running-desktop.png")
                browser.click('[data-control="pause"]')
                browser.wait("Boolean(document.querySelector('[data-control=\"resume\"]'))")
                assert http.get(f"/api/runs/{replay_id}").json()["status"] == "paused"
                browser.screenshot(output / "replay-paused-desktop.png")
                browser.screenshot(output / "replay-paused-mobile.png", 390, 844)
                browser.click("#theme-toggle")
                browser.screenshot(output / "replay-paused-dark.png", 1280, 900)
                browser.click("#theme-toggle")
                browser.screenshot(output / "replay-paused-desktop.png")
                browser.click('[data-control="resume"]')
                browser.wait("Boolean(document.querySelector('[data-control=\"pause\"]'))")
                browser.click('[data-control="stop"]')
                browser.wait("document.querySelector('#confirm-dialog').open")
                browser.click("#confirm-accept")
                browser.wait("document.querySelector('#run-overview').innerText.includes('Đã dừng')")
                rows = http.get(f"/api/runs/{replay_id}/predictions").json()["items"]
                assert len(rows) == len({item["row_index"] for item in rows})
                record("Replay tạm dừng, tiếp tục và dừng có xác nhận; không nhân đôi dòng")
                # CSV hợp lệ sát 10 MiB: padding chỉ trong label, model không nhận label.
                csv_lines = source.head(1).to_csv(index=False).splitlines()
                beginning = (csv_lines[0] + ",label\n" + csv_lines[1] + ",").encode()
                boundary_csv = beginning + b"x" * (10 * 1024 * 1024 - len(beginning) - 1) + b"\n"
                accepted = http.post("/api/runs", files={"file": ("valid_10mib.csv", boundary_csv, "text/csv")})
                assert accepted.status_code == 202, accepted.text[:200]
                boundary_id = accepted.json()["id"]
                deadline = time.monotonic() + 30
                while http.get(f"/api/runs/{boundary_id}").json()["status"] != "completed":
                    browser.evaluate("true")
                    assert time.monotonic() < deadline
                    time.sleep(0.1)
                assert http.get(f"/api/runs/{boundary_id}/predictions").json()["items"][0]["predicted_class"] == "Normal"
                record("CSV hợp lệ đúng 10 MiB đi hết gateway và suy luận đúng, label không vào model")
                browser.call("Page.navigate", {"url": base + f"/runs/{boundary_id}/predictions"})
                browser.wait("Boolean(document.querySelector('[data-select-row=\"0\"]'))")
                browser.click('[data-select-row="0"]')
                browser.wait(f"localStorage.getItem('iot:last-run') === '{boundary_id}' && JSON.parse(sessionStorage.getItem('iot:next:table:{boundary_id}') || '{{}}').selected?.includes(0)")
                browser.call("Page.navigate", {"url": base + "/runs"})
                browser.wait("Boolean(document.querySelector('tbody tr'))")
                assert not browser.evaluate(f"document.querySelector('table').innerText.includes('{run_id}')")
                browser.screenshot(output / "history-desktop.png")
                record("Lịch sử chỉ hiện tên CSV, giữ liên kết kết quả và ẩn run ID")

                # Chỉ xóa run fixture; các run khác còn dùng cho phần kiểm tra sau.
                delete_selector = f'button[data-delete-run="{boundary_id}"]'
                browser.click(delete_selector)
                browser.wait("Boolean(document.querySelector('#confirm-dialog')?.open)")
                assert browser.evaluate("document.querySelector('#confirm-dialog').innerText.includes('Không thể hoàn tác')")
                browser.screenshot(output / "history-delete-confirm-desktop.png")
                # Trang dài có scrollbar: tâm layout dùng clientWidth, không gồm rãnh cuộn.
                assert browser.evaluate("(()=>{const r=document.querySelector('#confirm-dialog').getBoundingClientRect();return Math.abs(r.left + r.width/2 - document.documentElement.clientWidth/2) < 2 && Math.abs(r.top + r.height/2 - innerHeight/2) < 2})()")
                browser.screenshot(output / "history-delete-confirm-mobile.png", 390, 844)
                assert browser.evaluate("(()=>{const r=document.querySelector('#confirm-dialog').getBoundingClientRect();return Math.abs(r.left + r.width/2 - document.documentElement.clientWidth/2) < 2 && Math.abs(r.top + r.height/2 - innerHeight/2) < 2})()")
                browser.click('#confirm-dialog button:not(#confirm-accept)')
                assert http.get(f"/api/runs/{boundary_id}").status_code == 200
                browser.screenshot(output / "history-delete-desktop.png")
                browser.click(delete_selector)
                browser.click("#confirm-accept")
                browser.wait(f"!document.querySelector('{delete_selector}')")
                assert http.get(f"/api/runs/{boundary_id}").status_code == 404
                assert not app.state.manager.run_dir(boundary_id).exists()
                assert http.get(f"/api/runs/{run_id}/predictions").status_code == 200
                assert browser.evaluate("localStorage.getItem('iot:last-run')") != boundary_id
                assert browser.evaluate("sessionStorage.getItem('iot:next:table:" + boundary_id + "')") is None
                record("Xóa lịch sử: Hủy giữ dữ liệu; xác nhận xóa đúng run/tệp, cập nhật bảng và dọn lần chạy hiện tại, giữ run khác")

                # Nút duy nhất của peek mở toàn bộ kết quả, chỉ đọc dữ liệu đã lưu.
                count = len(gemini.calls)
                browser.call("Page.navigate", {"url": base + f"/runs/{run_id}/predictions?row=0&audience=basic"})
                browser.wait("Boolean(document.querySelector('#peek-full-results'))")
                assert browser.evaluate("document.querySelectorAll('#peek .peek-footer a, #peek .peek-footer button').length") == 1
                browser.click('#peek [data-tab="predict"]')
                browser.wait("document.querySelectorAll('#peek .prob-row').length === 8")
                assert browser.evaluate("document.querySelector('#peek .prob-row[data-predicted=true] > span').textContent") == "Normal"
                assert browser.evaluate("Array.from(document.querySelectorAll('#peek .prob-row > span')).map(e => e.textContent)") == http.get("/api/schema").json()["class_names"]
                selection = browser.evaluate("Array.from(document.querySelectorAll('[data-select-row]:checked')).map(e => e.getAttribute('data-select-row'))")
                browser.screenshot(output / "peek-prediction-wide.png", 1920, 1080)
                assert browser.evaluate("document.querySelector('#peek .peek-body').scrollHeight <= document.querySelector('#peek .peek-body').clientHeight + 1")
                browser.call("Emulation.setDeviceMetricsOverride", {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": False})
                browser.evaluate("document.querySelector('#peek').scrollIntoView({block: 'center'})")
                browser.screenshot(output / "peek-prediction-mobile.png", 390, 844)
                assert len(gemini.calls) == count
                browser.click("#peek-full-results")
                browser.wait("location.pathname.endsWith('/rows/0') && Boolean(document.querySelector('#stage-content'))")
                assert browser.evaluate("new URLSearchParams(location.search).get('stage')") == "overview"
                browser.wait("new URLSearchParams(location.search).get('audience') === 'technical'")
                assert browser.evaluate("document.querySelectorAll('[data-stage]').length") == 4
                browser.click('[data-stage="gemini"]')
                browser.wait("Boolean(document.querySelector('#stage-content [data-status=\"gemini_disabled\"]'))")
                assert len(gemini.calls) == count
                browser.click('a[href*="/predictions?"]')
                browser.wait("Boolean(document.querySelector('#peek-full-results'))")
                assert browser.evaluate("Array.from(document.querySelectorAll('[data-select-row]:checked')).map(e => e.getAttribute('data-select-row'))") == selection
                browser.click('#peek [data-tab="predict"]')
                browser.call("Emulation.setDeviceMetricsOverride", {"width": 1280, "height": 720, "deviceScaleFactor": 1, "mobile": False})
                browser.evaluate("document.querySelector('#peek').scrollIntoView({block: 'center'})")
                browser.screenshot(output / "peek-prediction-desktop.png")
                browser.click("#theme-toggle")
                browser.screenshot(output / "peek-prediction-dark.png")
                browser.click("#theme-toggle")
                assert len(gemini.calls) == count
                record("Peek: tám lớp đúng thứ tự; một nút mở trang đầy đủ đúng dòng/mức, có bốn bước, giữ checkbox khi quay lại và không gọi Gemini")
                browser.click("#logout-button")
                browser.wait("location.pathname === '/login' && Boolean(document.querySelector('#login-submit'))")
                assert not any(item["name"] == "iot_session" for item in browser.call("Network.getCookies")["cookies"])
                return_path = f"/runs/{run_id}/predictions?class=Normal&row=0&audience=basic&context=truoc%26sau%3D1"
                browser.call("Page.navigate", {"url": base + return_path})
                browser.wait("Boolean(document.querySelector('#login-username'))")
                assert browser.evaluate("new URLSearchParams(location.search).get('next')") == return_path
                browser.change("#login-username", settings.admin_username)
                browser.change("#login-password", settings.admin_password)
                browser.click("#login-remember")
                browser.click("#login-submit")
                browser.wait("location.pathname.endsWith('/predictions') && Boolean(document.querySelector('#class-filter'))")
                assert browser.evaluate("new URLSearchParams(location.search).get('class')") == "Normal"
                assert browser.evaluate("new URLSearchParams(location.search).get('row')") == "0"
                assert browser.evaluate("new URLSearchParams(location.search).get('audience')") == "basic"
                assert browser.evaluate("new URLSearchParams(location.search).get('context')") == "truoc&sau=1"
                cookie = next(item for item in browser.call("Network.getCookies")["cookies"] if item["name"] == "iot_session")
                assert cookie["session"] is False and 0 < cookie["expires"] - time.time() <= 8 * 60 * 60
                http.post("/api/auth/logout", auth=None, headers={"Cookie": "iot_session=" + cookie["value"]})
                browser.call("Page.reload")
                browser.wait("location.pathname === '/login' && Boolean(document.querySelector('#login-submit'))")
                # Giả lập trình duyệt từng lưu Basic ở phiên ứng dụng cũ.
                basic = base64.b64encode(f"{settings.admin_username}:{settings.admin_password}".encode()).decode()
                browser.call("Network.setExtraHTTPHeaders", {"headers": {"Authorization": "Basic " + basic}})
                browser.call("Page.navigate", {"url": base + return_path})
                browser.wait("location.pathname === '/login' && Boolean(document.querySelector('#login-submit'))")
                browser.call("Network.setExtraHTTPHeaders", {"headers": {}})
                record("Đăng xuất thu hồi cookie; deep link yêu cầu đăng nhập, trở về đúng bảng và phiên bị thu hồi không đọc lại được")
                browser.call("Page.navigate", {"url": base + "/login"})
                browser.wait("Boolean(document.querySelector('#login-submit'))")
                browser.change("#login-username", settings.admin_username)
                browser.change("#login-password", settings.admin_password)
                browser.click("#login-submit")
                browser.wait("location.pathname === '/dashboard' && Boolean(document.querySelector('#dashboard-metrics dd'))")
                overview = http.get("/api/dashboard").json()
                assert overview["metrics"]["shap_rows"] == 3
                assert overview["saved_reviews"] == 1
                assert str(overview["saved_reviews"]) in browser.evaluate("document.querySelector('.dashboard-pipeline-columns section:last-child').textContent")
                record("Đăng nhập không có next mở Tổng quan; bằng chứng SHAP/phiếu đã lưu vẫn được tổng hợp sau lỗi Gemini")
                browser.evaluate("document.querySelector('.dashboard-pipeline').scrollIntoView()")
                browser.screenshot(output / "dashboard-pipeline-filled.png", 1440, 900)
                browser.call("Emulation.setDeviceMetricsOverride", {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": False})
                browser.wait("innerWidth === 390")
                browser.evaluate("document.querySelector('.dashboard-pipeline').scrollIntoView({block: 'start'})")
                browser.wait("document.querySelector('.dashboard-pipeline-columns section:last-child .pipeline-stat strong').getBoundingClientRect().top > 0 && document.querySelector('.dashboard-pipeline-columns section:last-child .pipeline-stat strong').getBoundingClientRect().bottom < innerHeight")
                browser.screenshot(output / "dashboard-mobile-pipeline-filled.png", 390, 844)

                assert app.state.manager.runtime.load_count == 1
                assert not browser.errors, browser.errors
                record("Không có lỗi JavaScript; model nạp một lần")
                result = {"checks": checks, "passed": len(checks), "gemini": "mocked", "model_load_count": 1, "runtime": "temporary; removed after test", "screenshots": sorted(path.name for path in output.glob('*.png'))}
                (output / "browser_checks.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
                print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
        finally:
            if chrome:
                chrome.terminate()
                chrome.wait(timeout=10)
            if gateway_started:
                subprocess.run(["docker", "stop", "-t", "2", gateway_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if next_server:
                next_server.terminate()
                next_server.wait(timeout=10)
            next_log.close()
            server.should_exit = True
            worker.join(timeout=30)
            listener.close()


if __name__ == "__main__":
    main()
