"""Phiên đăng nhập của một tài khoản quản trị, giữ trong process BE duy nhất."""

import hashlib
import secrets
import threading
import time
from urllib.parse import urlsplit

from fastapi import HTTPException, Request


SESSION_COOKIE = "iot_session"
SESSION_SECONDS = 8 * 60 * 60


def valid_credentials(username, password, settings):
    username_ok = secrets.compare_digest(username.encode(), settings.admin_username.encode())
    password_ok = secrets.compare_digest(password.encode(), settings.admin_password.encode())
    return username_ok and password_ok


def verify_browser_origin(request: Request):
    """Chặn thao tác ghi từ origin khác; client CLI không có Origin vẫn dùng được."""
    scheme = request.url.scheme
    if request.headers.get("x-forwarded-proto") == "https":
        scheme = "https"
    host = request.headers.get("host", "")
    # Next rewrites đổi Host sang BE nhưng ghi đè X-Forwarded-Host bằng Host
    # của FE. Chỉ nhận header này từ proxy trên chính máy chủ.
    if request.client and request.client.host in ["127.0.0.1", "::1"]:
        host = request.headers.get("x-forwarded-host") or host
    expected = f"{scheme}://{host}"
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    if not origin and referer:
        parsed = urlsplit(referer)
        origin = f"{parsed.scheme}://{parsed.netloc}"
    if request.headers.get("sec-fetch-site") in ["cross-site", "same-site"]:
        raise HTTPException(403, "Chỉ nhận thao tác từ giao diện cùng địa chỉ server.")
    if origin and origin != expected:
        raise HTTPException(403, "Địa chỉ gửi yêu cầu không khớp server.")


def secure_cookie(request: Request):
    return request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"


class SessionStore:
    def __init__(self):
        self.sessions = {}
        self.failures = {}
        self.lock = threading.Lock()

    def create(self, username):
        token = secrets.token_urlsafe(32)
        digest = hashlib.sha256(token.encode()).hexdigest()
        expires_at = time.time() + SESSION_SECONDS
        with self.lock:
            self.sessions = {
                key: value for key, value in self.sessions.items()
                if value["expires_at"] > time.time()
            }
            # Giới hạn bộ nhớ cho ứng dụng một nhóm người dùng.
            if len(self.sessions) >= 128:
                oldest = list(self.sessions)[0]
                del self.sessions[oldest]
            self.sessions[digest] = {"username": username, "expires_at": expires_at}
        return token, expires_at

    def read(self, token):
        if not token or len(token) > 256:
            return None
        digest = hashlib.sha256(token.encode()).hexdigest()
        with self.lock:
            session = self.sessions.get(digest)
            if session and session["expires_at"] <= time.time():
                del self.sessions[digest]
                return None
            return session

    def revoke(self, token):
        if token:
            digest = hashlib.sha256(token.encode()).hexdigest()
            with self.lock:
                self.sessions.pop(digest, None)

    def login_attempt(self, client_ip, username, password, settings):
        with self.lock:
            now = time.time()
            self.failures = {
                key: value for key, value in self.failures.items()
                if value["until"] > now
            }
            failure = self.failures.get(client_ip)
            if failure and failure["count"] >= 10:
                raise HTTPException(
                    429, "Đã nhập sai quá nhiều lần. Vui lòng thử lại sau một phút.",
                    headers={"Retry-After": "60"},
                )
            passed = valid_credentials(username, password, settings)
            if passed:
                self.failures.pop(client_ip, None)
                return True
            if client_ip not in self.failures:
                if len(self.failures) >= 512:
                    oldest = list(self.failures)[0]
                    del self.failures[oldest]
                self.failures[client_ip] = {"count": 0, "until": time.time() + 60}
            self.failures[client_ip]["count"] += 1
            return False
