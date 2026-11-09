# NIDR + Kafka local + Langfuse Cloud + Netdata local

Airflow để giai đoạn sau. Không có Grafana/Prometheus hoặc server Langfuse local. Model vẫn nạp đúng một lần trong BE, giữ SQLite và volume kết quả hiện tại.

## Cấu hình riêng trên máy

Chạy từ repo root. Giữ tài khoản/Gemini trong `BE/.env`. Sao chép `.env.observability.example` thành `.env.observability` nếu chưa có; không ghi đè file đã điền khóa. File thật phải được Git bỏ qua và có quyền `600` trên Linux.

Trong `.env.observability`, đặt `LANGFUSE_ENABLED=true`, endpoint EU `https://cloud.langfuse.com` và hai khóa của project. Có thể dùng endpoint US `https://us.cloud.langfuse.com` nếu project ở US. Không dùng khóa Gemini làm khóa Langfuse. `LANGFUSE_CAPTURE_CONTENT=true` cho phép gửi prompt bằng chứng SHAP và câu trả lời Gemini; đặt `false` để chỉ gửi metadata/usage/trạng thái. Không gửi CSV đầy đủ, label, tài khoản, API key hoặc nội dung exception HTTP.

Hai `--env-file` phải được giữ trong các lệnh dưới; file sau bổ sung biến, không in cấu hình đầy đủ vì có secret. Chỉ dùng `config --quiet` để kiểm tra.

```bash
docker compose --env-file BE/.env --env-file .env.observability \
  -f docker-compose.yml -f docker-compose.observability.yml \
  --profile kafka --profile monitoring --profile ingest config --quiet

docker compose --env-file BE/.env --env-file .env.observability \
  -f docker-compose.yml -f docker-compose.observability.yml build backend csv-consumer
```

Hoàn tất/chủ động dừng các tác vụ đang chạy và backup runtime trước khi nâng BE. Tạo lại backend làm hết hạn phiên đăng nhập; model/background/kết quả vẫn ở image/volume. Khi đã sẵn sàng cập nhật:

```bash
docker compose --env-file BE/.env --env-file .env.observability \
  -f docker-compose.yml -f docker-compose.observability.yml \
  --profile kafka --profile monitoring up -d --wait
```

Lệnh này bật BE có tracing, Kafka, consumer và Netdata. Producer thuộc profile `ingest`, không tự chạy khi bật stack. Mở NIDR tại `http://localhost:8080` và Netdata tại `http://localhost:19999`. Lần đầu Netdata hiện màn hình chào, chọn **Skip and use the dashboard anonymously** để xem local mà không đăng nhập Netdata Cloud.

## Phát CSV qua Kafka

`NIDR_UPLOAD_DIR=./upload` được mount chỉ đọc vào producer. Chỉ chọn `nidr_test_*.csv`, không chọn `manifest.csv`, JSON hoặc ZIP. Dữ liệu giữ nguyên chuỗi số/thang đo gốc; BE thực hiện transform bằng bundle đóng băng. Cột label được bỏ trước khi phát lên Kafka. Producer dùng schema đóng băng trong image, không cần BE online hoặc tài khoản quản trị; consumer mới cần xác thực BE.

```bash
# Một file chưa phát, mặc định 50 dòng/giây.
docker compose --env-file BE/.env --env-file .env.observability \
  -f docker-compose.yml -f docker-compose.observability.yml \
  --profile kafka --profile ingest run --rm csv-producer

# Chọn rõ một file. Chỉ tăng max-files sau khi đo tài nguyên.
docker compose --env-file BE/.env --env-file .env.observability \
  -f docker-compose.yml -f docker-compose.observability.yml \
  --profile kafka --profile ingest run --rm csv-producer \
  python -m streaming.producer --file nidr_test_00001.csv --max-files 1 --rate 50
```

Consumer staging từng dòng lên volume; khi đủ CSV mới gửi một run tối đa 1.000 dòng sang BE, mặc định Batch. Đây là vận chuyển theo dòng và suy luận theo file, không phải suy luận tức thì ngay khi mỗi record đến broker. Muốn hiển thị tiến độ từng dòng của NIDR, đặt `KAFKA_RUN_MODE=replay`, nhịp `KAFKA_REPLAY_INTERVAL` tối thiểu 0,05 giây rồi tạo lại consumer. Không tự chạy SHAP/Gemini; chọn mẫu trên giao diện như trước để kiểm soát quota.

## Lưu giữ và khôi phục

- Kafka một broker KRaft, một partition, replication factor 1: phù hợp demo, không có dự phòng khi mất máy/volume.
- Topic giữ tối đa khoảng 24 giờ hoặc 512 MiB/partition, xóa theo segment. Không phải hard quota tức thời; dung lượng có thể vượt ngưỡng tạm thời. Kết quả lâu dài ở SQLite/files của BE.
- Producer chỉ ghi checkpoint sau khi Kafka ACK đủ file. `--republish` cho phép phát lại để khôi phục sự cố; không tạo lần chạy mới nếu source đã được BE nhận.
- Consumer commit offset sau khi SQLite staging đã commit trên `consumer-state`. Đó là bàn giao bền vững sang staging, chưa có nghĩa dự đoán đã hoàn tất. Phải giữ cả volume Kafka, staging và runtime.
- BE 1.8.0+ lưu receipt và run cùng transaction. Nếu response mất, consumer gửi lại cùng `Idempotency-Key`, BE trả run cũ. Không tuyên bố exactly-once toàn hệ thống. Cơ chế này chống trùng theo Idempotency-Key, không tự gộp các lần upload thủ công trước đó.
- Receipt được giữ khi người dùng xóa run; phát lại cùng nguồn không tự hồi sinh run đã xóa. Muốn chạy lại có chủ đích, dùng topic mới và cập nhật producer/consumer cùng topic.
- CSV lỗi không được tự bỏ qua; consumer dừng, giữ offset/staging để người vận hành kiểm tra. Run bị dừng/lỗi/gián đoạn cần xử lý/tiếp tục trên NIDR rồi khởi động lại consumer. Không tự gọi lại Gemini khi lỗi API.
- Không dùng `docker compose down -v` nếu muốn giữ lịch sử, offset và checkpoint.

## Langfuse Cloud

Skill chính thức: <https://github.com/langfuse/skills>. SDK Python pin `langfuse==5.2.0`. Các span `nidr.predict`, `nidr.explanation`, `nidr.shap` và generation `nidr.gemini` giữ tên ổn định, metadata run/dòng và trace ID trong `execution.json`. Một lời gọi API thật là một generation; cache không được ghi thành lời gọi mới. Chọn manual spans tại ranh giới cache/API để giữ cách xử lý lỗi, bảo vệ nội dung và không ghi trùng generation.

SDK export bất đồng bộ với queue tối đa mặc định 128 span, batch 16, mỗi 5 giây, timeout HTTP 3 giây. Queue đầy có thể mất telemetry, không chặn model. SDK chỉ export span do Langfuse SDK tạo, không tự thu thập mọi OTel span của thư viện khác. Chưa có log tập trung hoặc trace HTTP tổng quát.

`GET /api/observability` yêu cầu đăng nhập, chỉ trả trạng thái cấu hình; `active=true` không khẳng định Cloud đã nhận trace. Nội dung chuỗi giới hạn 32.000 ký tự để giữ bộ nhớ hữu hạn; bản đầy đủ vẫn ở BE. Token dùng số liệu provider trả về, không đoán khi thiếu. Chi phí có thể chưa hiển thị nếu Langfuse chưa có bảng giá đúng model. Trạng thái accepted của Gemini chỉ là kiểm tra tự động, không thay đánh giá chuyên gia.

Đổi key trực tiếp trong `.env.observability`, không gửi lên Git/chat. Tạo lại riêng backend để nạp biến mới. Langfuse Cloud lưu dữ liệu được gửi ra ngoài máy; không coi đó là bản sao lưu thay cho SQLite/runtime.

## Netdata local trên Linux

Agent dùng host network/PID và các mount host read-only để đọc đúng máy Ubuntu; UI bind `127.0.0.1:19999`. Nếu đổi cổng, sửa `[web] bind to` trong `netdata.conf`. Không mở giao diện này ra Internet. Không kết nối Netdata Cloud, tắt anonymous telemetry/ML và các plugin nặng; chu kỳ 5 giây, một storage tier, retention 128 MiB hoặc một ngày. Giới hạn này áp dụng metric data, không phải tổng kích thước mọi file/log.

Kafka giới hạn 1.280 MiB, heap tối đa 512 MiB; consumer/producer mỗi tiến trình tối đa 192 MiB; Netdata tối đa 512 MiB. Đây là trần container, không phải mức tiêu thụ được cam kết. Theo dõi swap/CPU trong lúc chạy SHAP trước khi tăng tải.

Docker socket được mount cho Netdata để phân giải tên/đọc trạng thái container; mount `:ro` không làm Docker API thành read-only. Chỉ agent tin cậy trên máy local sử dụng socket. Không bật `privileged`, SYS_ADMIN hoặc tắt AppArmor cho bộ metrics cơ bản. Một số tính năng mạng/process nâng cao sẽ không có. Trên Windows Docker Desktop, số liệu host phản ánh VM Linux, không phải toàn bộ Windows; cấu hình này được kiểm chứng trên Ubuntu.

## Kiểm tra

```bash
.venv/bin/python -m pytest BE/tests streaming/tests -q --disable-warnings
.venv/bin/python deploy/observability/smoke_test.py
```

Smoke test dùng broker local nhưng topic, BE, credentials và runtime tạm; model thật đối chiếu 50 dòng golden, kiểm phát trùng và restart consumer. Không gọi Gemini thật hoặc sửa runtime NIDR đang vận hành.

Nguồn: [Kafka Docker](https://kafka.apache.org/44/getting-started/docker/), [Langfuse best practices](https://langfuse.com/docs/observability/best-practices), [Netdata Docker](https://learn.netdata.cloud/docs/netdata-agent/installation/docker).

Bằng chứng triển khai và giới hạn thực tế: [VERIFICATION.md](VERIFICATION.md).
