# Kafka local, Langfuse Cloud và Netdata local

Nhánh triển khai: `duong`. Giữ model đóng băng, một BE và SQLite hiện tại.

1. Producer chỉ đọc `nidr_test_*.csv` trong upload, kiểm schema và checksum, phát từng dòng vào một partition Kafka. Mặc định một file mỗi lệnh, có giới hạn tốc độ; không tự nạp cả tập test.
2. Consumer lưu từng sự kiện vào SQLite staging trên volume trước khi commit offset. Khi đủ một file, dựng lại CSV chỉ có đặc trưng và gọi BE. Header Idempotency-Key bảo vệ trường hợp BE đã nhận nhưng response bị mất. Không nạp model trong producer/consumer.
3. BE lưu receipt và run trong cùng transaction. Consumer chờ xử lý xong trước file kế tiếp. Không tự chạy SHAP hoặc Gemini; người dùng chọn mẫu trong NIDR như trước.
4. Langfuse Cloud nhận span dự đoán, giải thích, SHAP, generation Gemini và kết quả kiểm tra. Chỉ capture nội dung prompt/response khi được cấu hình, không gửi label hoặc CSV đầy đủ. Telemetry lỗi không làm hỏng xử lý; export nền có queue/timeout giới hạn.
5. Netdata local thu thập CPU/RAM/swap/ổ đĩa/container, giao diện chỉ bind localhost. Tắt ML và Cloud, giảm chu kỳ thu thập và giới hạn retention/tài nguyên.
6. Không triển khai Grafana/Prometheus/Airflow. Giữ Docker logs có xoay vòng. Bỏ đề xuất Grafana trong kế hoạch hiện tại.

Kiểm chứng: test receipt/restart/duplicate/conflict, producer/staging/consumer, telemetry hỏng và không có khóa; test Docker Kafka thật với runtime BE tạm và model thật; không gọi Gemini trả phí để test. Chỉ cập nhật BE đang vận hành sau bước review/cho phép restart theo AGENTS.md. Cấu hình Langfuse Cloud cần project/key do người dùng tự điền, không gửi trong chat.
