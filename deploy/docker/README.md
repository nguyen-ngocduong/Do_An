# NIDR — bộ Docker bàn giao

Windows/Linux Intel–AMD (linux/amd64), CPU. Windows cần Docker Desktop chạy Linux containers; Linux cần Docker Engine và Compose plugin. Khuyến nghị Docker được cấp 2 CPU, 4 GiB RAM, đủ dung lượng cho image/volume; xem số đo thực tế trong tài liệu kiểm chứng. Không cần Python/Node hoặc source/model rời trên máy nhận.

## Chạy lần đầu

Giải nén bộ bàn giao. So sánh SHA256 ZIP với file .sha256 đi kèm (PowerShell: `Get-FileHash`, Linux: `sha256sum`). Từ thư mục vừa giải nén:

```console
docker load --input nidr-images.tar
```

Tạo `.env` từ `.env.docker.example`: PowerShell `Copy-Item .env.docker.example .env`; Bash `cp .env.docker.example .env`. Mở `.env`, đặt `ADMIN_PASSWORD` riêng, thêm `GEMINI_API_KEY` nếu cần diễn giải. Giá trị có `$` nên đặt trong dấu nháy đơn để Compose giữ nguyên. Không dùng hoặc gửi mật khẩu/key trong image, Git hoặc chat. Chỉ backend nhận các biến bí mật.

```console
docker compose up -d --wait
docker compose ps
```

Mở http://localhost:8080, đăng nhập với tài khoản trong .env. Có thể đổi NIDR_PORT nếu cổng bận. Tải `samples/integration_input_50.csv`, chạy Batch, chọn một dòng và yêu cầu SHAP/Gemini. CSV này thuộc bộ demo đã dùng lại, không phải test độc lập mới. Chưa có key vẫn dự đoán/SHAP được; Gemini báo chưa cấu hình. Gemini cần Internet; Swagger UI sử dụng CDN nên cũng cần Internet để hiển thị tài liệu.

## Dữ liệu và vận hành

Named volume `runtime` giữ SQLite, CSV, SHAP/Gemini, cảnh báo, Human review. `docker compose down` không xóa volume. Không dùng `down -v` trừ khi chủ động xóa toàn bộ dữ liệu. Restart backend thu hồi phiên đăng nhập; kết quả vẫn giữ. Không scale backend: model, hàng đợi và phiên nằm trong một process; SQLite không dùng chung giữa nhiều replica.

Xem lỗi: `docker compose logs --tail 100 backend` hoặc `gateway`. Thiếu mật khẩu sẽ bị chặn trước khi khởi động. Thiếu image: nạp archive và kiểm tra NIDR_VERSION. Model lỗi checksum/version: giữ log, dùng lại đúng image phát hành; không tự đổi model/thư viện. Đổi key trong .env rồi `docker compose up -d` để tạo lại backend. Không tự retry Gemini khi lỗi API.

## Backup và restore

Chờ hoàn tất tác vụ rồi dừng stack bằng `docker compose stop`. Trên Linux, lấy tên volume:

```bash
volume=$(docker volume ls -q --filter label=com.docker.compose.project=nidr --filter label=com.docker.compose.volume=runtime)
test -n "$volume"
docker run --rm -v "$volume":/data:ro -v "$PWD":/backup --entrypoint sh nidr-gateway:1.0.0 -c 'tar czf /backup/nidr-runtime.tgz -C /data .'
docker compose start
```

PowerShell dùng `$volume = docker volume ls -q --filter label=com.docker.compose.project=nidr --filter label=com.docker.compose.volume=runtime`, rồi mount `"${volume}:/data:ro"` và `"${PWD}:/backup"` với cùng lệnh docker run. Nếu phiên bản khác, thay tag gateway đúng phiên bản đã nạp.

Để restore trên máy mới: cấu hình .env và nạp đúng image; `docker compose create backend`, lấy tên volume mới theo label, rồi chạy gateway với volume gắn `/data` (bỏ `:ro`) và archive gắn `/backup:ro`, lệnh `tar xzf /backup/nidr-runtime.tgz -C /data`. Chỉ restore vào volume trống khi backend đã dừng. Sau đó `docker compose up -d --wait`. Giữ owner UID10001 của dữ liệu. Luôn backup cả SQLite và files khi stack đã dừng, tránh tách DB khỏi WAL hoặc tệp đang ghi.

## Nâng cấp và VPS

Backup trước, nạp archive phiên bản mới, đổi NIDR_VERSION trong .env, `docker compose up -d --wait`; giữ cùng project/volume. Không rollback schema tùy tiện; dùng backup tương ứng nếu schema đổi ở phiên bản sau.

VPS x86_64 Linux: cùng image, đặt DNS trỏ domain tới server. Cung cấp chứng chỉ được tin cậy cho domain, `server.crt` và `server.key` trong thư mục ngoài bộ bàn giao, đặt NIDR_TLS_DIR thành đường dẫn tuyệt đối trong .env. Compose >=2.24.4:

```console
docker compose -f docker-compose.yml -f docker-compose.prod.yml config --quiet
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --wait
```

Overlay thay cổng localhost bằng80/443, HTTP chuyển HTTPS; chỉ gateway public. Cert mount read-only, backend/frontend chỉ mạng Docker. Không thay cấu hình Nginx của website khác. Tự gia hạn chứng chỉ theo hạ tầng VPS rồi reload gateway. Chưa có dịch vụ cấp chứng chỉ tự động trong bộ này.

## Monitoring và Kafka tùy chọn

Ba service có healthcheck, version tag và log stdout/stderr giới hạn 10 MiB ×3/service. Gateway tạo X-Request-ID, log JSON thời gian/status/latency/URI, không ghi query/body/cookie/Authorization. Header request ID được chuyển tới BE/FE; chưa phải distributed tracing toàn luồng.

Stack tùy chọn dùng Kafka local, Langfuse Cloud và Netdata local; Airflow để sau. Không triển khai Grafana/Prometheus. Trong source repo, xem `deploy/observability/README.md` và `docker-compose.observability.yml`. Khóa Cloud đặt trong `.env.observability` riêng. Monitoring không tự gọi lại Gemini, không nạp model thứ hai. Bộ archive cơ bản vẫn chỉ gồm BE/FE/gateway; archive đã tạo trước đây chưa được cập nhật với tracing mới hoặc các dịch vụ Kafka/Netdata. Cài stack mở rộng từ source repo theo hướng dẫn trên.
