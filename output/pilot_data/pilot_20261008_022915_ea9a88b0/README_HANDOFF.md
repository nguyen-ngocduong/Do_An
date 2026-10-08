# Bàn giao pilot CICIoT2023 — 8 lớp

- Pilot run: `pilot_20261008_022915_ea9a88b0`.
- Processing nguồn: `20261007_164739_35f682b9`.
- Seed lấy mẫu: `42`; budgets: `[100000, 500000, 1000000]`.
- Giữ toàn bộ lớp: `['BruteForce', 'Web-Based']`; tất cả tập con đủ 8 lớp, không lấy lặp ID.
- Preprocessing dùng chung bộ đã fit trên toàn train nguồn. Đây là so sánh quy mô huấn luyện classifier với preprocessing cố định.
- Feature order/mapping: `source_reference/feature_schema.json` và `source_reference/label_mapping.json`.

## File cho từng budget

Mỗi `train_<budget>/` có index, nhãn, source-row ID, sample metadata, bảng support và manifest. `X_train_raw.npy`/`X_train_scaled.npy` được xuất khi `EXPORT_FEATURE_ARRAYS=True` (lần này: `True`). Nếu chỉ xuất index, đọc source train qua mmap rồi chọn đúng `train_indices.npy` theo batch.

Raw là dữ liệu đã chọn cột/điền thiếu, giữ thang gốc. Scaled đã áp dụng log/scale. Khi train trực tiếp trên các file này, không transform thêm lần nữa. Khi suy luận từ feature CSV gốc, dùng transformer tương ứng trong `source_reference/` cùng model đã huấn luyện; dùng phiên bản thư viện của processing config khi nạp joblib.

## Validation và test

Gắn lại bộ processed nguồn cùng output pilot trong notebook huấn luyện. Dùng `evaluation_reference.json` để lấy tên file tương đối; tìm lại đường dẫn Kaggle thực sau khi gắn dataset. Giữ cùng validation cho mọi budget/model. Test dùng cuối, sau khi chốt model và quy mô. Phân bố evaluation là bộ đã qua `purge_eval` của run nguồn.

## Cách quyết định quy mô train

1. Chạy cùng một protocol ở từng budget; ghi model seed, cấu hình và phần cứng.
2. Điền `benchmark_template.csv` bằng kết quả thực. Ghi precision/recall/F1/support đủ 8 lớp và confusion matrix 8×8 trong báo cáo mô hình.
3. So sánh macro-F1 cùng recall/F1 các lớp hiếm trên cùng validation; xem thêm thời gian và RAM. Không suy ra 100k hay 1M là tốt nhất trước khi chạy.
4. Giữ các quyết định xử lý mất cân bằng nhất quán khi so sánh quy mô; nếu thay class_weight hoặc thuật toán, ghi thành thí nghiệm riêng.
5. Cả ba tập đều giữ toàn bộ BruteForce/Web-Based hiện có; tăng budget chủ yếu bổ sung các lớp khác. Các tập không độc lập với nhau vì được thiết kế lồng nhau.

Các ô metric trống là chưa huấn luyện, không phải điểm 0. Notebook lấy mẫu chưa hoàn thành việc lựa chọn quy mô chính thức cho TV1-03.
