"""Đăng nhập bằng cookie dùng cùng tài khoản với Swagger/CLI."""

from BE.auth import SESSION_COOKIE, SESSION_SECONDS, SessionStore
from BE.auth import verify_browser_origin
from fastapi import HTTPException
from starlette.requests import Request
import pytest


def sign_in(client, remember=False):
    client.auth = None
    return client.post("/api/auth/login", json={"username": "tester", "password": "test-password", "remember": remember})


def test_cookie_login_read_and_logout(client):
    response = sign_in(client, remember=True)
    assert response.status_code == 200
    assert response.json()["username"] == "tester"
    assert "password" not in response.text
    cookie = response.headers["set-cookie"]
    assert "HttpOnly" in cookie and "SameSite=strict" in cookie
    assert f"Max-Age={SESSION_SECONDS}" in cookie and "Path=/" in cookie
    token = client.cookies.get(SESSION_COOKIE)
    assert token and "test-password" not in token
    assert client.get("/api/auth/session").json()["username"] == "tester"
    assert client.get("/api/schema").status_code == 200
    assert client.get("/docs").status_code == 200
    assert client.get("/api/model").json()["model_load_count"] == 1
    assert client.post("/api/auth/logout").status_code == 200
    assert client.cookies.get(SESSION_COOKIE) is None
    assert client.get("/api/auth/session").status_code == 401
    # Token bị thu hồi ở BE, không chỉ xóa trong trình duyệt.
    assert client.get("/api/schema", headers={"Cookie": f"{SESSION_COOKIE}={token}"}).status_code == 401


def test_relogin_rotates_cookie_and_invalid_basic_is_not_masked(client):
    assert sign_in(client).status_code == 200
    old = client.cookies.get(SESSION_COOKIE)
    assert sign_in(client).status_code == 200
    assert client.cookies.get(SESSION_COOKIE) != old
    assert client.get("/api/schema", headers={"Cookie": f"{SESSION_COOKIE}={old}"}).status_code == 401
    assert client.get("/api/schema", auth=("tester", "wrong")).status_code == 401


def test_remember_controls_browser_cookie_persistence(client):
    response = sign_in(client)
    cookie = response.headers["set-cookie"].lower()
    assert "max-age" not in cookie and "expires=" not in cookie
    session_expiry = response.json()["expires_at"]
    assert client.get("/api/auth/session").json()["expires_at"] == session_expiry
    remembered = sign_in(client, remember=True)
    assert f"Max-Age={SESSION_SECONDS}" in remembered.headers["set-cookie"]
    assert remembered.json()["expires_at"] - session_expiry < 10
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/auth/session").status_code == 401


def test_wrong_login_has_no_browser_challenge_or_credential_echo(client):
    client.auth = None
    response = client.post("/api/auth/login", json={"username": "tester", "password": "wrong-private-value"})
    assert response.status_code == 401
    assert "www-authenticate" not in response.headers
    assert "set-cookie" not in response.headers and "wrong-private-value" not in response.text
    invalid = client.post("/api/auth/login", json={"username": "tester", "password": "private" * 1000})
    assert invalid.status_code == 422 and "privateprivate" not in invalid.text
    assert "www-authenticate" not in client.get("/api/schema").headers
    assert client.get("/docs").headers["www-authenticate"] == "Basic"


def test_cookie_security_and_same_origin_mutations(client):
    client.auth = None
    response = client.post(
        "/api/auth/login", json={"username": "tester", "password": "test-password"},
        headers={"X-Forwarded-Proto": "https", "Origin": "https://testserver"},
    )
    assert response.status_code == 200 and "Secure" in response.headers["set-cookie"]
    client.cookies.clear()
    assert sign_in(client).status_code == 200
    token = client.cookies.get(SESSION_COOKIE)
    assert client.post("/api/auth/logout", headers={"Origin": "https://external.invalid"}).status_code == 403
    assert client.get("/api/auth/session").status_code == 200
    assert client.patch("/api/alerts/1", json={"note": "test"}, headers={"Origin": "https://external.invalid"}).status_code == 403
    assert client.patch("/api/alerts/1", auth=("tester", "test-password"), json={"note": "test"}, headers={"Origin": "https://external.invalid"}).status_code == 403
    assert client.post("/api/auth/logout", headers={"Sec-Fetch-Site": "same-site"}).status_code == 403
    assert client.post("/api/auth/logout", headers={"Origin": "http://testserver"}).status_code == 200
    assert not client.app.state.sessions.read(token)
    assert client.post("/api/auth/login", json={"username": "tester", "password": "test-password"}, headers={"Origin": "null"}).status_code == 403


def test_session_expires_and_restart_store_has_no_old_sessions():
    store = SessionStore()
    token, _ = store.create("tester")
    assert store.read(token)["username"] == "tester"
    assert SessionStore().read(token) is None
    for item in store.sessions.values():
        item["expires_at"] = 0
    assert store.read(token) is None
    assert store.read("modified-token") is None


def test_repeated_wrong_logins_are_throttled(client):
    client.auth = None
    for _ in range(10):
        assert client.post("/api/auth/login", json={"username": "tester", "password": "wrong"}).status_code == 401
    response = client.post("/api/auth/login", json={"username": "tester", "password": "test-password"})
    assert response.status_code == 429 and response.headers["retry-after"] == "60"
    for item in client.app.state.sessions.failures.values():
        item["until"] = 0
    assert sign_in(client).status_code == 200


def origin_request(client_ip, origin, forwarded_host=None, referer=None):
    headers = [(b"host", b"127.0.0.1:8000")]
    if origin:
        headers.append((b"origin", origin.encode()))
    if forwarded_host:
        headers.append((b"x-forwarded-host", forwarded_host.encode()))
    if referer:
        headers.append((b"referer", referer.encode()))
    return Request({
        "type": "http", "method": "POST", "scheme": "http", "path": "/api/auth/login",
        "server": ("127.0.0.1", 8000), "client": (client_ip, 50000), "headers": headers,
    })


def test_next_forwarded_host_is_used_only_for_loopback_proxy():
    for client_ip in ["127.0.0.1", "::1"]:
        verify_browser_origin(origin_request(client_ip, "http://localhost:3000", "localhost:3000"))
        verify_browser_origin(origin_request(client_ip, None, "localhost:3000", "http://localhost:3000/login"))
    with pytest.raises(HTTPException) as error:
        verify_browser_origin(origin_request("203.0.113.10", "http://external.invalid", "external.invalid"))
    assert error.value.status_code == 403


def test_forwarded_host_does_not_accept_different_origin():
    for origin in ["https://external.invalid", "http://localhost:3000.external.invalid", "null"]:
        with pytest.raises(HTTPException) as error:
            verify_browser_origin(origin_request("127.0.0.1", origin, "localhost:3000"))
        assert error.value.status_code == 403
