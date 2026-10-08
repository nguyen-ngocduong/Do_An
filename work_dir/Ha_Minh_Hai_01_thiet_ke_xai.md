# Hà Minh Hải — 01: Thiết kế mô-đun XAI

- **Phụ trách:** Hà Minh Hải.
- **Phụ thuộc:** schema/mapping Dương 02; thiết kế có thể bắt đầu trước model.
- **Trạng thái ngày 08/10/2026:** chưa có bằng chứng hoàn thành.
- **Phạm vi:** phân loại có giám sát 8 lớp; dữ liệu và huấn luyện chạy trên Kaggle.

## Công việc

- [ ] Đọc đề cương/tài liệu XAI; xác định phạm vi SHAP và LIME cho mô hình phân loại 8 lớp.
- [ ] Thiết kế interface nhận model/preprocessing, sample ID, feature order và lớp giải thích; thống nhất với Dương và Kiên.
- [ ] Chọn SHAP làm hướng triển khai đầu tiên; lập kế hoạch LIME đối chiếu các ca tiêu biểu sau khi SHAP hoạt động.
- [ ] Định nghĩa output chứa model/run ID, sample ID, class index/name, baseline, đóng góp, output space, cấu hình và thời gian.
- [ ] Thiết kế mẫu nền từ train nếu explainer yêu cầu; mẫu giải thích validation cố định có support từng lớp và seed.
- [ ] Đặt tiêu chí kiểm tra tính cộng, ánh xạ lớp, tái lập/ổn định và thời gian; viết nháp cơ sở XAI mục 2.4.

## Đầu ra và nghiệm thu

Thiết kế module XAI, contract đầu vào/đầu ra, protocol chọn mẫu và kiểm tra giải thích.

## Bằng chứng và giới hạn

Có schema từ Dương không có nghĩa là Hải đã triển khai XAI. Chưa có code/kết quả XAI được xác nhận.

## Bước tiếp theo

Hải 02 sau khi Dương bàn giao model cây baseline.
