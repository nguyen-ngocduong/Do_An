# Nguyễn Ngọc Dương — 03: Huấn luyện baseline và chốt quy mô train

- **Phụ trách:** Nguyễn Ngọc Dương.
- **Phụ thuộc:** pilot/schema Dương 02.
- **Trạng thái ngày 08/10/2026:** baseline đã có kết quả Kaggle; quy mô train chính là 1 triệu dòng.
- **Phạm vi:** phân loại 8 lớp bằng DT, RF và XGBoost, chạy trên Kaggle.

## Công việc

- [x] Lưu protocol, cấu hình, seed 42, phiên bản thư viện, feature/class order và chính sách float32 overlap.
- [x] Có notebook runner Kaggle để kiểm tra đầu vào, huấn luyện, đánh giá và lưu theo run ID.
- [x] Đối sánh DT/RF/XGBoost không trọng số ở 100k, 500k và 1M: 9 thí nghiệm.
- [x] Đối sánh none/sqrt/balanced ở 1M: thêm 6 fit, tổng cộng 15 fit khác nhau.
- [x] Báo precision/recall/F1/support đủ 8 lớp, macro-F1, confusion matrix, thời gian fit/suy luận và RAM.
- [x] Chọn budget 1M và cấu hình bằng validation, đóng băng trước báo cáo test baseline.
- [x] Lưu model/config, dự đoán truy vết được, pipeline CSV và kiểm tra suy luận trước/sau nạp trong Kaggle.
- [ ] Hải và Kiên xác nhận nạp/chạy được bundle baseline trên môi trường của người nhận.

## Bằng chứng và giới hạn

Run [models_20261008_073827_d29a37c3](../output/model_experiments/models_20261008_073827_d29a37c3/README_HANDOFF.md) ghi `status=complete`. Xem [checklist](../output/model_experiments/models_20261008_073827_d29a37c3/completion_checklist.json), [bảng validation](../output/model_experiments/models_20261008_073827_d29a37c3/validation_results.csv), [quyết định budget](../output/model_experiments/models_20261008_073827_d29a37c3/budget_selection.json) và [test](../output/model_experiments/models_20261008_073827_d29a37c3/final_test_comparison.csv).

Validation còn 808.943 dòng và test còn 765.991 dòng sau purge vector raw float32 giao nhau. Preprocessing được fit trên toàn train nguồn, classifier dùng pilot. RF không trọng số 1M là model demo baseline. Chưa có multi-seed, feature selection hoặc tái lập độc lập từ CSV gốc; chưa nghiệm thu XAI/UI.

## Bước tiếp theo

Dương 04: cải thiện recall BruteForce/Web-Based bằng quy tắc quyết định, lấy mẫu/trọng số và tuning có giới hạn. Hai lớp cần precision từng lớp ≥30%; recall ≥85% là mục tiêu thực nghiệm. Validation/test baseline đã được xem, phải công bố khi đánh giá vòng tiếp theo.
