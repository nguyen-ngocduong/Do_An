# Hà Minh Hải — 04: Kiểm chứng và đo thời gian giải thích

- **Phụ trách:** Hà Minh Hải.
- **Phụ thuộc:** Hải 02–03; model cuối và dự đoán test Dương 04.
- **Trạng thái ngày 08/10/2026:** chưa có bằng chứng hoàn thành.
- **Phạm vi:** phân loại có giám sát 8 lớp; dữ liệu và huấn luyện chạy trên Kaggle.

## Công việc

- [ ] Kiểm tra tính cộng SHAP đúng output space, lớp và dung sai; lưu sai lệch/tỷ lệ đạt.
- [ ] Lặp cùng model/sample/config; thử thay seed nền từ train có kiểm soát nếu dùng background, so overlap top-5/top-10 và dấu đóng góp.
- [ ] Lặp LIME trên các ca cố định với nhiều seed; ghi overlap/fidelity và giới hạn ổn định.
- [ ] Đo thời gian tách khởi tạo explainer và giải thích mỗi mẫu; warm-up, phần cứng/cỡ mẫu, số lần, median/p95 khi phù hợp.
- [ ] Sau đánh giá test đóng băng, tạo hình và ca đúng/sai cuối theo protocol; không dùng giải thích test để chọn lại model.
- [ ] Đối chiếu output module với hiển thị tích hợp cùng Kiên; ghi model/run/class/sample để phát hiện lệch.
- [ ] Viết 4.3 và phần XAI của 4.4; giao bảng thời gian giải thích và giới hạn cho Kiên tổng hợp.

## Đầu ra và nghiệm thu

Bảng thời gian giải thích, log kiểm chứng/tái lập, phân tích cuối và hình có truy vết.

## Bằng chứng và giới hạn

Chưa có kết quả đo; thời gian pilot dữ liệu không phải thời gian XAI.

## Bước tiếp theo

Hải 05 và hỗ trợ Kiên kiểm thử end-to-end.
