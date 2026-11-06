"""Chạy từ repo root: .venv/bin/python -m BE."""

import argparse

import uvicorn

from BE.config import load_settings


def main():
    parser = argparse.ArgumentParser(description="Khởi động BE CICIoT2023 với một process.")
    parser.add_argument("--host", help="Mặc định 127.0.0.1; dùng 0.0.0.0 khi mở LAN qua HTTPS.")
    parser.add_argument("--port", type=int)
    parser.add_argument("--ssl-certfile")
    parser.add_argument("--ssl-keyfile")
    args = parser.parse_args()
    settings = load_settings()
    host = args.host or settings.host
    certfile = args.ssl_certfile or settings.ssl_certfile or None
    keyfile = args.ssl_keyfile or settings.ssl_keyfile or None
    if bool(certfile) != bool(keyfile):
        parser.error("Cần cả SSL_CERTFILE và SSL_KEYFILE.")
    if host not in ["127.0.0.1", "localhost", "::1"] and not certfile:
        parser.error("Khi mở LAN, cấu hình HTTPS bằng --ssl-certfile và --ssl-keyfile.")
    uvicorn.run(
        "BE.main:app", host=host, port=args.port or settings.port,
        workers=1, ssl_certfile=certfile, ssl_keyfile=keyfile,
    )


if __name__ == "__main__":
    main()
