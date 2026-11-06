"""Tạo BE/.env cho lần chạy đầu; không ghi đè cấu hình đã có."""

import os
import secrets

from BE.config import REPO_DIR


def main():
    path = REPO_DIR / "BE/.env"
    if path.exists():
        print("Giữ nguyên BE/.env đã có; mở file này để xem hoặc cập nhật cấu hình.")
        return
    template = (REPO_DIR / "BE/.env.example").read_text(encoding="utf-8")
    password = secrets.token_urlsafe(24)
    content = template.replace("ADMIN_PASSWORD=\n", "ADMIN_PASSWORD=" + password + "\n", 1)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        stream.write(content)
    print("Đã tạo BE/.env với tài khoản admin và mật khẩu ngẫu nhiên.")
    print("Mở BE/.env để xem mật khẩu hoặc thêm GEMINI_API_KEY; không commit file này.")


if __name__ == "__main__":
    main()
