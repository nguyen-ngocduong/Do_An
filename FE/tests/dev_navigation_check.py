"""Kiểm tra điều hướng ở Next dev/Webpack bằng Chrome thật.

Chạy từ repo root: .venv/bin/python FE/tests/dev_navigation_check.py
Bản sao FE, Next/BE, Chrome và runtime đều riêng; không sửa .next đang dùng.
Không đọc .env, gọi Gemini hoặc sửa dữ liệu của server vận hành.
"""

import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

import httpx
import uvicorn
from websockets.sync.client import connect

project = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project))
from BE.config import Settings
from BE.main import create_app
from BE.tests.conftest import FakeGeminiClient
from browser_check import Browser, free_port


def main():
    chrome_path = shutil.which('google-chrome') or shutil.which('chromium')
    if not chrome_path:
        raise SystemExit('Cần Google Chrome hoặc Chromium để kiểm tra chế độ dev.')
    results = project / 'FE/tests/results/dev-navigation'
    results.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='nidr-dev-direct-') as temporary:
        root = Path(temporary)
        frontend = root / 'FE'
        frontend.mkdir()
        for folder in ['src', 'public']:
            shutil.copytree(project / 'FE' / folder, frontend / folder)
        for file in (project / 'FE').iterdir():
            if file.is_file() and file.suffix in {'.json', '.ts', '.mjs', '.mts'} and '.tsbuildinfo' not in file.name:
                shutil.copy2(file, frontend / file.name)
        (frontend / 'node_modules').symlink_to(project / 'FE/node_modules', target_is_directory=True)
        settings = Settings(runtime_dir=root / 'runtime', admin_username='browser-tester', admin_password='browser-test-password', gemini_pause_seconds=0)
        app = create_app(settings, gemini_client=FakeGeminiClient())
        listener = socket.socket()
        listener.bind(('127.0.0.1', 0))
        be_port = listener.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=be_port, log_level='error'))
        worker = threading.Thread(target=lambda: server.run(sockets=[listener]), daemon=True)
        worker.start()
        port = free_port()
        base = f'http://127.0.0.1:{port}'
        node = str(Path.home() / '.nvm/versions/node/v22.23.4/bin/node')
        if not Path(node).is_file():
            node = shutil.which('node') or 'node'
        next_log = (results / 'next-dev.log').open('w')
        next_server = subprocess.Popen([node, 'node_modules/next/dist/bin/next', 'dev', '--webpack', '--hostname', '127.0.0.1', '--port', str(port)], cwd=frontend, env={**os.environ, 'API_PROXY_TARGET':f'http://127.0.0.1:{be_port}'}, stdout=next_log, stderr=next_log, start_new_session=True)
        chrome = None
        try:
            with httpx.Client(timeout=90) as http:
                deadline = time.monotonic() + 120
                while True:
                    try:
                        if http.get(base + '/login').status_code == 200:
                            break
                    except httpx.TransportError:
                        pass
                    assert time.monotonic() < deadline
                    time.sleep(.2)
            profile = root / 'chrome'
            chrome = subprocess.Popen([chrome_path, '--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--no-first-run', '--remote-debugging-port=0', f'--user-data-dir={profile}', 'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            deadline = time.monotonic() + 15
            while not (profile / 'DevToolsActivePort').exists():
                assert time.monotonic() < deadline
                time.sleep(.1)
            debug_port = (profile / 'DevToolsActivePort').read_text().splitlines()[0]
            with urllib.request.urlopen(f'http://127.0.0.1:{debug_port}/json') as response:
                target = next(item for item in json.load(response) if item['type']=='page')
            with connect(target['webSocketDebuggerUrl'], max_size=20*1024*1024) as connection:
                browser = Browser(connection)
                browser.call('Runtime.enable')
                browser.call('Page.enable')
                browser.call('Page.navigate', {'url':base+'/login'})
                browser.wait("Boolean(document.querySelector('#login-submit'))")
                browser.wait("Object.keys(document.querySelector('#login-submit')).some(key => key.startsWith('__reactProps$'))", timeout=60)
                browser.change('#login-username', settings.admin_username)
                browser.change('#login-password', settings.admin_password)
                browser.click('#login-submit')
                browser.wait("Boolean(document.querySelector('#primary-navigation'))", timeout=60)
                print('Login dev succeeded', flush=True)
                paths = [('/dashboard','#dashboard-metrics'),('/alerts','#alert-filters'),('/runs','.pagehead'),('/runs/new','#create-form')]
                for attempt in range(4):
                    for path, selector in paths:
                        browser.click(f'#primary-navigation a[href="{path}"]')
                        browser.wait(f"location.pathname === '{path}' && Boolean(document.querySelector('{selector}'))",timeout=60)
                        print('Navigation',attempt,path,flush=True)
                # Đổi số hook trong bản sao tạm để kiểm tra Fast Refresh như khi sửa UI.
                browser.click('#primary-navigation a[href="/alerts"]')
                browser.wait("Boolean(document.querySelector('#alert-filters'))", timeout=60)
                component = frontend / 'src/components/alerts/alert-browser.tsx'
                original = component.read_text()
                changed = original.replace('const [dirty, setDirty] = useState(false);', 'const [dirty, setDirty] = useState(false);\n    const [refreshMarker] = useState("ready");')
                changed = changed.replace('<div className="alert-page">', '<div className="alert-page" data-dev-check={refreshMarker}>')
                assert changed != original
                try:
                    component.write_text(changed)
                    browser.wait("document.querySelector('.alert-page')?.dataset.devCheck === 'ready'", timeout=60)
                finally:
                    component.write_text(original)
                browser.wait("Boolean(document.querySelector('.alert-page')) && !document.querySelector('.alert-page').hasAttribute('data-dev-check')", timeout=60)
                data={'mode':'development --webpack', 'navigations':17, 'fast_refresh':'add/remove hook in temporary copy', 'runtime_errors':browser.errors}
                (results/'result.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
                assert not browser.errors, browser.errors
                print('DEV NAVIGATION PASSED',flush=True)
        finally:
            if chrome:
                chrome.terminate()
                chrome.wait(timeout=10)
            if next_server.poll() is None:
                os.killpg(next_server.pid, signal.SIGTERM)
                next_server.wait(timeout=15)
            next_log.close()
            server.should_exit=True
            worker.join(timeout=30)
            listener.close()


if __name__ == "__main__":
    main()
