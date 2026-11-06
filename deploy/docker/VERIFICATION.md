# Kiểm chứng Docker — 05/11/2026

Đã build ba image Linux amd64, giữ Python3.13/Node22 và lock BE hiện hành. Bundle/background không train/fit lại. Image backend khoảng1,53GB (gồm môi trường đã khóa và artifact235MiB), frontend297MB, gateway62,1MB. Không cần GPU; giữ cả dependencies của lock nguồn thay vì tự thay package CPU khác phiên bản.

Đã chạy `deploy/docker/smoke_test.py` với project/volume/cổng và credentials tạm, không đọc BE/.env hoặc restart dev. **9 nhóm kiểm tra đạt**:

1. Chạy image từ thư mục chỉ có Compose/config, healthchecks và volume lần đầu ghi được bằng user BE không phải root.
2. Login/session, trang riêng tư, chặn Origin khác, checksum/version/golden khớp, model nạp1lần và lịch sử trống.
3. Batch50, SHAP CPU thật, không cần key khi tắt Gemini và bốn artifact đọc được.
4. Lưu/tải Human review và tải ZIP kết quả.
5. Force-recreate giữ dữ liệu và Nginx DNS tìm lại backend.
6. Gemini giả lập qua override chỉ dành kiểm thử, không có trong image phát hành.
7. Replay50 hoàn tất.
8. Dừng stack, backup và restore vào volume khác; run/review giữ lại.
9. Overlay production, TLS với chứng chỉ thử được client xác minh, Secure cookie và login/logout.

Kiểm tra âm: model giả được bind-mount chỉ đọc vào container test bị từ chối checksum; thiếu mật khẩu bị Compose chặn; user BE không ghi được artifact nguồn nhưng ghi được runtime. Không sửa artifact thật.

RAM quan sát sau thử nghiệm: BE703MiB, FE44MiB, gateway8MiB. Đây là một thời điểm của dữ liệu thử, không phải đỉnh tải hoặc cam kết dung lượng tối thiểu. API Gemini thật không được gọi trong kiểm thử; không chứng minh chất lượng LLM hoặc quota của key người nhận. Swagger cần CDN, Gemini cần Internet; assets/font của FE đã đóng gói.

Gói ZIP793MiB đã được tạo ở dist. Đã giải nén vào thư mục không có BE/FE/output, xác minh checksum các tệp, docker load cả ba image và chạy lại bằng Compose. Chrome thật đăng nhập, mở dashboard và upload page thành công, không có JS error. Bằng chứng: `delivery-check.json`. Các JSON verification/negative-checks/delivery-check là bằng chứng local tái tạo, không chứa key. Kết quả Windows chưa thử trực tiếp: cần hai thành viên xác nhận Docker Desktop Linux containers trên máy họ.

Không triển khai Grafana/Langfuse, không tự cấp chứng chỉ hoặc deploy VPS thật. Chỉ cung cấp nền tảng log/health và tài liệu hook cho đợt sau. Cần Compose>=2.24.4 cho overlay dùng !override.
