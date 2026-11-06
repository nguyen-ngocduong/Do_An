"""Tạo chứng chỉ nội bộ để demo HTTPS trên một server LAN."""

import argparse
import ipaddress
import re
import shutil
import subprocess
from pathlib import Path

from BE.config import REPO_DIR


def main():
    parser = argparse.ArgumentParser(description="Tạo chứng chỉ TLS tự ký cho localhost hoặc IP/tên máy LAN.")
    parser.add_argument("--host", default="localhost", help="IP hoặc tên máy mà trình duyệt sẽ truy cập.")
    parser.add_argument("--output", type=Path, default=REPO_DIR / "BE/runtime/tls")
    args = parser.parse_args()
    try:
        ipaddress.ip_address(args.host)
        alternative = "IP:" + args.host
    except ValueError:
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9.-]{0,251}[a-zA-Z0-9]|localhost", args.host):
            parser.error("Tên host không hợp lệ.")
        alternative = "DNS:" + args.host
    if not shutil.which("openssl"):
        parser.error("Cần cài openssl để tạo chứng chỉ nội bộ.")
    directory = args.output.expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    certificate = directory / "cert.pem"
    private_key = directory / "key.pem"
    if certificate.exists() or private_key.exists():
        parser.error("Thư mục đã có chứng chỉ/key; chọn thư mục khác để tránh ghi đè.")
    result = subprocess.run([
        "openssl", "req", "-x509", "-nodes", "-newkey", "rsa:2048", "-days", "365",
        "-keyout", str(private_key), "-out", str(certificate),
        "-subj", "/CN=" + args.host,
        "-addext", "subjectAltName=" + alternative + ",DNS:localhost,IP:127.0.0.1",
    ], capture_output=True, text=True)
    if result.returncode:
        parser.error("Không tạo được chứng chỉ; kiểm tra openssl và quyền ghi thư mục.")
    private_key.chmod(0o600)
    print("Certificate:", certificate)
    print("Private key:", private_key)
    print("Đây là chứng chỉ tự ký cho demo nội bộ; cài tin cậy trên máy dùng để truy cập LAN.")


if __name__ == "__main__":
    main()
