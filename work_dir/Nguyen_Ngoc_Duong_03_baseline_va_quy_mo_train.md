# Nguyễn Ngọc Dương — 03: Huấn luyện baseline và chốt quy mô train

- **Phụ trách:** Nguyễn Ngọc Dương.
- **Phụ thuộc:** pilot/schema Dương 02; không chờ module XAI hay giao diện.
- **Trạng thái ngày 08/10/2026:** đã có đầu vào và mẫu bảng; chưa huấn luyện.
- **Phạm vi:** phân loại có giám sát 8 lớp; dữ liệu và huấn luyện chạy trên Kaggle.

## Công việc

- [x] Chốt macro-F1 validation làm chỉ số chính; báo precision/recall/F1/support đủ 8 lớp, confusion matrix 8×8, thêm weighted-F1 và accuracy.
- [x] Chuẩn bị bảng benchmark cho 3 budget × Logistic Regression, Decision Tree, Random Forest; các dòng hiện là not_run.
- [ ] Cụ thể hóa protocol, cấu hình 3 mô hình, seed, ngân sách RAM/thời gian, cách xử lý chỉ số không xác định và log cảnh báo hội tụ.
- [ ] Viết notebook runner Kaggle chung: đọc pilot và validation nguồn, kiểm tra schema/classes, train/evaluate/save theo run ID.
- [ ] Huấn luyện LR trên scaled, DT/RF trên raw ở 100k; không transform lại ma trận đã xử lý. Lưu preprocessing tương ứng cùng model để suy luận CSV gốc.
- [ ] Chạy 500k và 1M khi ngân sách cho phép, cùng cấu hình/protocol và validation 862.150 dòng; ghi trường hợp không chạy được và nguyên nhân.
- [ ] Đo thời gian fit/predict, RAM, cảnh báo hội tụ; lưu dự đoán validation có sample ID, metrics từng lớp và confusion matrix.
- [ ] So sánh baseline không cân bằng và class_weight thành các thí nghiệm riêng; ghi tương tác với pilot đã thay phân bố.
- [ ] Chốt budget train chính dựa trên macro-F1, recall lớp hiếm/Normal và tài nguyên; không lựa chọn bằng test.
- [ ] Lưu model/config/version/feature order/class order; kiểm tra dự đoán và xác suất 8 lớp trước/sau nạp trên 10–20 mẫu cố định.
- [ ] Bàn giao sớm model cây baseline và mẫu chuẩn cho Hải thử XAI, Kiên tích hợp; xác nhận đúng run ID.

## Đầu ra và nghiệm thu

Ít nhất ba baseline, bảng so sánh validation và tài nguyên theo budget, quyết định quy mô có số liệu, model/config cùng mẫu suy luận chuẩn.

## Bằng chứng và giới hạn

[Bảng mẫu](../output/pilot_data/pilot_20261008_022915_ea9a88b0/benchmark_template.csv) có 9 dòng `not_run`; [manifest pilot](../output/pilot_data/pilot_20261008_022915_ea9a88b0/pilot_manifest.json) ghi `model_training_status=not_run`. Chưa có bằng chứng huấn luyện hoàn tất. Đây là công việc của Nguyễn Ngọc Dương, gồm cả dữ liệu và mô hình.

## Bước tiếp theo

Dương 04 khi baseline và budget đã được chốt; Hải/ Kiên có thể bắt đầu thiết kế interface từ schema hiện có.
