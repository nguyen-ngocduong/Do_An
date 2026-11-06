# Cổng HTTPS cho một server

Một máy chạy ba process: Next.js ở `127.0.0.1:3000`, **một** process BE ở `127.0.0.1:8000`, Nginx phục vụ HTTPS. Model/background chỉ nạp trong BE. Không chạy nhiều worker BE hoặc mở thêm process dùng chung runtime.

## Chuẩn bị

1. Cài BE và artifact theo [BE/README.md](../../BE/README.md), giữ `BE/.env` hiện có.
2. Cài/build FE bằng Node.js 22 theo [FE/README.md](../README.md). Chốt `API_PROXY_TARGET` trước build; Nginx production chuyển API trực tiếp sang BE.
3. Chuẩn bị Nginx có `http_auth_request_module`; xem bằng `nginx -V`. Image kiểm thử `nginx:1.28-alpine` có module này và đã chạy `nginx -t` thành công.
4. Tạo hoặc cung cấp chứng chỉ cho hostname/IP thực tế, được máy truy cập tin cậy. Có thể dùng công cụ `BE.make_certificate` theo tài liệu BE khi thử LAN. Giữ private key ngoài Git.

## Cấu hình

[nginx.conf](nginx.conf) là cấu hình **đầy đủ** cho instance Nginx chuyên phục vụ ứng dụng. Không chép đè cấu hình một server đang phục vụ website khác. Nếu Nginx đã có cấu hình hệ thống, ghép block `server` và các directive cần thiết vào cấu hình hiện có rồi kiểm tra.

- Sửa `server_name localhost` thành hostname/IP thực tế.
- Sửa đường dẫn `/etc/nginx/tls/server.crt` và `server.key` tới chứng chỉ của máy chủ.
- Sửa các upstream loopback nếu dùng cổng khác.
- Với cổng HTTPS khác 443, sửa `listen` và dùng đúng URL tương ứng.
- Chỉ mở cổng gateway; hai process ứng dụng tiếp tục bind loopback.

```bash
# Terminal BE: dùng process đang chạy nếu đã có.
.venv/bin/python -m BE

# Terminal FE, từ FE/:
HOSTNAME=127.0.0.1 PORT=3000 npm run start

# Sau khi chuẩn bị cấu hình/chứng chỉ cho Nginx thực tế:
nginx -t -c /duong/dan/tuyet/doi/nginx.conf
```

Chỉ khởi động/reload Nginx sau khi cấu hình và chứng chỉ của máy chủ đã được chuẩn bị. Lượt triển khai source không thay dịch vụ Nginx của người dùng.

## Routing và xác thực

| URL | Upstream / xác thực |
|---|---|
| `/`, `/runs/...`, `/alerts` | Next.js, được Nginx kiểm tra phiên cookie hoặc HTTP Basic qua GET BE `/api/schema`; thiếu phiên chuyển tới `/login` |
| `/login`, `/_next/static/...`, `/icon.svg` | Next.js, công khai để form hoạt động trước đăng nhập; không chứa dữ liệu lần chạy |
| `/api/...` | FastAPI; BE kiểm tra quyền, không cache |
| `/docs`, `/openapi.json` | FastAPI, giữ HTTP Basic và `WWW-Authenticate` |
| `/health` | FastAPI; kiểm tra sẵn sàng công khai theo hợp đồng BE |
| `/_be_auth` | Location nội bộ; không mở ra bên ngoài |
| `/login/redirect` | Next helper chỉ được gọi qua location nội bộ Nginx để mã hóa đầy đủ return URL; truy cập ngoài trả 404 |

Cookie, `Authorization`, Host và forwarded host/protocol được chuyển tiếp. Auth subrequest không gửi body. API/file giữ nguyên đường dẫn và query; không chèn `/api/v1`. Nginx không cache và `proxy_next_upstream off` tránh tự gửi lại thao tác ghi. Body gateway tối đa 11 MiB để chứa multipart; BE giữ giới hạn **file 10 MiB / 1.000 dòng**.

Mở `https://<may-chu>/login`; dùng tài khoản BE hiện có. Phiên cookie tối đa tám giờ, HttpOnly/Strict/Secure, dùng cho trang/API/tải file và bị thu hồi khi đăng xuất hoặc restart BE. Swagger vẫn tại `/docs`, hỗ trợ cả cookie đã đăng nhập và HTTP Basic. Nginx cần dùng template mới, BE cần bản 1.4.0; không tự reload dịch vụ đang vận hành khi chỉ chỉnh source.

## Kiểm chứng hiện có

[Browser suite](../tests/browser_check.py) tạo chứng chỉ, cấu hình Nginx từ chính template này, Next standalone và BE/model thật trên cổng/runtime tạm; kiểm tra upload, HTTP Basic, deep-link, SHAP, Gemini giả lập và tải báo cáo. Xem [VERIFICATION.md](../VERIFICATION.md). Chưa triển khai cổng 443 của máy vận hành, chưa thử từ thiết bị LAN khác.
