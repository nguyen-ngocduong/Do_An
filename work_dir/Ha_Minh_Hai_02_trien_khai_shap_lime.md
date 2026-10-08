# Hà Minh Hải — 02: Triển khai SHAP và LIME

- **Phụ trách:** Hà Minh Hải.
- **Phụ thuộc:** Hải 01 và model cây baseline từ Dương 03.
- **Trạng thái ngày 08/10/2026:** chưa có bằng chứng hoàn thành.
- **Phạm vi:** phân loại có giám sát 8 lớp; dữ liệu và huấn luyện chạy trên Kaggle.

## Công việc

- [ ] Chạy SHAP trên các mẫu validation với model thật; lưu explainer, phiên bản, cấu hình và seed.
- [ ] Dùng đúng dữ liệu estimator nhận sau preprocessing; phân biệt giá trị feature gốc và đã biến đổi.
- [ ] Kiểm tra tensor SHAP đa lớp, classes_, sample ID và lớp đang giải thích; kiểm tra baseline + tổng đóng góp khớp output với dung sai công bố.
- [ ] Sinh giải thích cục bộ mẫu (waterfall/bar) và đầu ra có cấu trúc cho Kiên hiển thị.
- [ ] Triển khai LIME trên các mẫu/lớp tương ứng; lưu seed, cấu hình, đầu ra và local fidelity nếu có.
- [ ] Đo thử thời gian/RAM để giới hạn số mẫu; bàn giao API/module XAI và ví dụ gọi cho Kiên.

## Đầu ra và nghiệm thu

Mã SHAP/LIME chạy được với model thật, ví dụ giải thích kiểm tra được, môi trường và interface bàn giao.

## Bằng chứng và giới hạn

Chưa có model/XAI artifact để nghiệm thu. LIME không được tick nếu mới lập kế hoạch.

## Bước tiếp theo

Hải 03; phối hợp Kiên 03 để tích hợp đầu ra giải thích.
