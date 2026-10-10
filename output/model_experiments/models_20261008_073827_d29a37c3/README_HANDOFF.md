# Bàn giao detection 8 lớp — models_20261008_073827_d29a37c3

Nguồn processing: 20261007_164739_35f682b9. Pilot: pilot_20261008_022915_ea9a88b0. Budget: 1000000.
Trạng thái: complete. Model demo chọn bằng validation: RF_n1000000_none_s42.

## Kết quả cần đọc
- baseline_size_comparison.csv, budget_summary.csv, budget_selection.json: quy mô và lý do chọn.
- weight_comparison.csv, selected_validation_results.csv: lựa chọn trọng số/model bằng validation.
- val_float32_purge_audit.json / test_float32_purge_audit.json và *_float32_kept_processed_indices.npy: số dòng/lớp trước-sau, lý do loại và index tái tạo tập đánh giá.
- final_test_comparison.csv: chỉ tồn tại khi test hoàn tất; không dùng để chọn lại model.
- all_per_class_metrics.csv: precision/recall/F1/support đủ 8 lớp.
- all_inference_benchmarks.csv: thời gian warmed predict_proba, batch 1 và batch cố định.
- experiments/<id>/validation và test/<id>: confusion matrix PNG/CSV, report, probabilities.npy và predictions.csv.gz cùng thứ tự.
- fit_seconds và fit_peak_rss_mib: thời gian fit và peak RSS process, không phải riêng model hay VRAM.
- protocol.json, environment.json, requirements_runtime.txt, input_integrity.json và frozen_selection.json: cấu hình, nguồn và khóa lựa chọn.

## Hải — XAI
Nạp handoff/<DT|RF|XGBoost>/pipeline.joblib. Estimator nằm ở named_steps['model']; input estimator là 44 feature raw đã impute/chọn cột và cast float32. Khi dùng TreeExplainer cho estimator, đưa đúng ma trận này, không đưa 46 cột gốc hoặc nhánh scaled. Classes 0..7 theo label_mapping.json. Mẫu nền lấy từ train; lưu sample ID/run ID. predict_proba trả 8 cột theo thứ tự lớp; không coi raw SHAP margin là xác suất.

## Kiên — tích hợp
Dùng predict_csv.py và handoff/<model>/. Ví dụ:
```python
from predict_csv import predict_csv
predict_csv('handoff/RF', 'input.csv', 'predictions.csv')
```
Đặt đường dẫn theo thư mục thực. Giữ đúng chính tả Magnitue. 44 feature đầu ra là bắt buộc; cột dư/nhãn bị bỏ qua. Helper chuyển numeric, Inf sang NaN; pipeline điền median nguồn, không fit lại. model.joblib chỉ nhận feature đã xử lý, pipeline.joblib nhận DataFrame numeric theo schema. example_processed_features.csv chứa giá trị đã xử lý phục vụ smoke check, không phải bản trích CSV gốc.

## Tái lập
1. Tái tạo processing từ notebook ciciot2023-do-an-processing.ipynb và nguồn trong source_snapshot/source_manifest.json.
2. Tái tạo pilot từ notebook ciciot2023-do-an-pilot.ipynb, seed 42 và ba budget.
3. Chạy notebook ciciot2023-do-an-models.ipynb cùng protocol.json, phiên bản và phần cứng được ghi. Dùng source run ID/hash tương ứng; không đổi ID để giả làm cùng một run.
4. Đối chiếu support, hash input, class/feature order, metrics/dự đoán và golden_samples.npz. Sai khác số học giữa môi trường cần được ghi, không hứa bit-identical trên mọi máy.

## Giới hạn
Một seed; chưa tuning sâu, SHAP feature selection hoặc xác minh độc lập theo phiên/thiết bị. Preprocessing fit toàn train nguồn, dùng cố định cho pilot. Sampling thay tỷ lệ lớp; tăng budget không thêm mẫu hai lớp hiếm. Validation/test tiếp tục được purge theo raw float32, ưu tiên hợp của mọi pilot train → validation → test; đọc audit để lấy số dòng/support thực dùng, không dùng số nguồn thay cho số đánh giá. Tập đánh giá đổi theo quy tắc label-independent và dùng chung cho mọi model; không so trực tiếp điểm với paper dùng split hoặc test cân bằng khác. RSS lấy mẫu mỗi 0,1 giây có thể bỏ qua peak rất ngắn; benchmark không gồm CSV/XAI/UI.
Test đã được dùng thì không thay cấu hình theo điểm test; mọi cải tiến sau cần công bố việc đã xem test. Chưa có chứng cứ độc lập end-to-end từ raw CSV mới hoặc giao diện/XAI chạy thật chỉ từ notebook này.
