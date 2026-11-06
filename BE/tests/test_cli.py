import os
import subprocess
import sys

from BE.config import REPO_DIR


def test_cli_requires_https_for_lan():
    environment = os.environ.copy()
    environment.update(ADMIN_USERNAME="tester", ADMIN_PASSWORD="test-password", SSL_CERTFILE="", SSL_KEYFILE="")
    result = subprocess.run(
        [sys.executable, "-m", "BE", "--host", "0.0.0.0"], cwd=REPO_DIR,
        env=environment, capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 2
    assert "HTTPS" in result.stderr


def test_certificate_has_host_and_does_not_overwrite(tmp_path):
    directory = tmp_path / "tls"
    command = [sys.executable, "-m", "BE.create_certificate", "--host", "127.0.0.1", "--output", str(directory)]
    first = subprocess.run(command, cwd=REPO_DIR, capture_output=True, text=True, timeout=10)
    assert first.returncode == 0, first.stderr
    key = directory / "key.pem"
    original_key = key.read_bytes()
    assert key.stat().st_mode & 0o777 == 0o600
    certificate = subprocess.run(
        ["openssl", "x509", "-in", str(directory / "cert.pem"), "-noout", "-ext", "subjectAltName"],
        capture_output=True, text=True, check=True,
    )
    assert "IP Address:127.0.0.1" in certificate.stdout
    second = subprocess.run(command, cwd=REPO_DIR, capture_output=True, text=True, timeout=10)
    assert second.returncode == 2
    assert key.read_bytes() == original_key
