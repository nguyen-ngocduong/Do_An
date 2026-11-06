# Kiểm chứng Kafka, Langfuse Cloud và Netdata — 06/11/2026

Nhánh duong. Model, tiền xử lý và SHAP background đóng băng không thay đổi.

## Kiểm thử

- `.venv/bin/python -m pytest BE/tests streaming/tests -q --disable-warnings --tb=short`: **85 passed**, 693 cảnh báo thư viện, 37,89 giây. Phủ golden/API, auth, receipt tồn tại qua restart/xóa, rollback CSV lỗi, staging/ACK, phát trùng, lỗi API, schema sự kiện, SDK thật export vào bộ nhớ, token/reasoning, cache và masking.
- `pip check` local và trong image BE: đạt. Lint/TypeScript/build FE không chạy lại vì không sửa FE.
- Docker build backend/streaming đạt; Compose config kiểm bằng `--quiet` cho mọi profile.
- Kafka thật + BE/model thật ở runtime tạm: phát 50 dòng golden hai lần, restart consumer, giữ một run/50 dự đoán; xác suất khớp trong 1e-6, model_load_count=1, không gọi Gemini thật. Topic/container/volume kiểm thử đã dọn. Lượt đầu phát hiện bind mount thư mục tạm thiếu quyền cho UID 10001; đã sửa quyền test và thêm lỗi rõ khi producer từ chối thư mục không có CSV đọc được, rồi chạy lại đạt.
- Langfuse Cloud EU trả 200 khi truy vấn project và observations bằng CLI của skill chính thức. Trace kiểm thử dùng model/SHAP thật, Gemini giả lập tên mock-gemini, environment nidr-test. Cả ba observation có input/output, parent-child đúng, generation có model/usage; không có Secret Key, tài khoản, Gemini key hoặc label. Public key trong metadata project do SDK thêm là định danh công khai, không phải nội dung prompt/output.
- [Trace kiểm thử đã audit](https://cloud.langfuse.com/project/cmw4dhpfh01duad0jcnbz3ek9/traces/100a7b810210f41d97a898cbefac54de). Đây không phải kết quả chất lượng Gemini thật hoặc chi phí Google mới.
- Chrome mở Netdata local, chọn Skip and use the dashboard anonymously: hiển thị CPU/RAM/network/disk và số liệu thực. API có system.cpu, system.ram, mem.swap, disk_space và cgroup theo tên container. Netdata ACLK xác nhận Claimed: No, Online: No, reconnect count 0. Ảnh kiểm tra ở /tmp/nidr-netdata-ui.png và /tmp/nidr-netdata-ready-ui.png, không nằm trong source.

## Áp dụng trên máy người dùng

Người dùng đã cho phép tạo lại riêng backend. Đã sao lưu SQLite bằng sqlite3.backup vào `BE/runtime/backups/before-observability-20261106.sqlite3` trong volume, giữ image rollback `nidr-backend:before-observability-20261106`. Đây là backup DB phục vụ lần nâng cấp này; không thay thế backup toàn runtime theo hướng dẫn Docker.

Backend hiện dùng image `sha256:3cb16b582f87ec8d64f56717f6e815365a1cf368cc3c1ba1b8fa49581ee8008e`, API 1.8.0, SDK active. FE và gateway giữ nguyên ID container; NIDR /health trả ready. Kafka, Netdata và consumer healthy. Không có Grafana/Prometheus/Airflow hoặc server Langfuse local.

Đã phát `upload/**/nidr_test_00003.csv` thật: Kafka ACK 1.000 dòng, sau phát lại có offset 2.000/end 2.000/lag 0; BE hoàn tất run `9f803c8905d34d1580a658dcf29fbec0`. [Trace dự đoán thật](https://cloud.langfuse.com/project/cmw4dhpfh01duad0jcnbz3ek9/traces/a90a9a5fe93df60feb520fc3f10b7ba3) được đọc lại từ Cloud, environment nidr-local, output completed/1000.

Producer đã được tách khỏi BE: schema được đóng gói từ artifact, không cần tài khoản quản trị hoặc BE online. Kiểm thử thực tế phát lại 1.000 dòng với NIDR_API_URL trỏ vào cổng không hoạt động và không truyền credentials vẫn ACK đủ; consumer không tạo run trùng. Unit test kiểm tra producer checkpoint qua hai lần chạy và republish đạt.

Sau áp dụng có 3 run/3.000 dự đoán. Đối chiếu backup xác nhận hai run cũ, 2.000 dự đoán cũ, giải thích và Human review được giữ nguyên. Run mới chưa có yêu cầu giải thích, không tự gọi SHAP/Gemini. Producer checkpoint và staging/receipt tồn tại trên volume.

Tại thời điểm chờ sau khi chạy, Docker stats xấp xỉ Kafka 178 MiB, Netdata 81 MiB, consumer 31 MiB và BE 609 MiB. Đây không phải RAM đỉnh hoặc benchmark tải lớn. Máy 8 GB vẫn cần theo dõi swap khi mở IDE/Chrome và chạy SHAP.

## Giới hạn

- Một broker không có dự phòng; retention Kafka theo thời gian/dung lượng, kết quả dài hạn ở BE. Commit offset là đã lưu vào staging, không phải dự đoán xong. Không tuyên bố exactly-once toàn hệ thống.
- Không phát toàn bộ 729 file và không chạy thêm Gemini trả phí trong kiểm thử này.
- Gói ZIP bàn giao cũ chưa được đóng lại với stack mở rộng. Khóa thật nằm ở `.env.observability` mode 600, Git/Docker context bỏ qua; source đã quét theo khóa thực và không có kết quả trùng.
- Secret Key đã được người dùng gửi qua chat; cần thu hồi/tạo lại sau kiểm tra, cập nhật file riêng và tạo lại backend để nạp khóa mới.
