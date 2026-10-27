# Bộ kết quả chốt để bàn giao

Chỉ dùng một kết quả tích hợp chính: **`integration_20261022_075217_0b67d48f`**. Hai run model và SHAP bên dưới là nguồn phụ thuộc của kết quả này.

| Thành phần | Run được sử dụng | Tài liệu chính |
|---|---|---|
| XGBoost meta-model | `xgb_meta_20261021_092334_9024562d` | [Protocol](stacking_meta_runs/xgb_meta_20261021_092334_9024562d/protocol.json), [validation](stacking_meta_runs/xgb_meta_20261021_092334_9024562d/validation_comparison.csv), [test đã dùng lại](stacking_meta_runs/xgb_meta_20261021_092334_9024562d/test_comparison.csv) |
| SHAP và background train | `shap_20261022_021654_2555e479` | [Hướng dẫn](xai_shap_runs/shap_20261022_021654_2555e479/README_HANDOFF.md), [background](xai_shap_runs/shap_20261022_021654_2555e479/background.npy), [CSV golden](xai_shap_runs/shap_20261022_021654_2555e479/golden_predictions.csv) |
| Pipeline tích hợp 50 mẫu | `integration_20261022_075217_0b67d48f` | [Trạng thái](integration_runs/integration_20261022_075217_0b67d48f/run_status.json), [bảng tổng hợp](integration_runs/integration_20261022_075217_0b67d48f/summary.csv), [diễn giải tiếng Việt](integration_runs/integration_20261022_075217_0b67d48f/all_reports_vi.md) |

Data run nguồn: `20261021_052521_96f61f19`. Run stacking tạo OOF/base models: `stacking_20261021_064141_916da555`. Các run này vẫn được lưu trong output Kaggle nguồn, không nằm trong bản tải local hiện tại.

Model chốt là **`XGB_d4_n200`**, cấu trúc `DT + RF + HGB → XGBoost`. Macro-F1 validation là **0.896137**; macro-F1 trên test đã dùng lại là **0.889495**. Đây là kết quả từ các run được lưu, không phải phép đánh giá độc lập mới.

## Phạm vi dữ liệu trong Git

Git chứa notebook, báo cáo, biểu đồ, prompt, cấu hình, checksum, model meta dạng JSON đã chọn và các mảng SHAP nhỏ cần để đối chiếu. Giữ nguyên byte artifact đã tải từ Kaggle; `.gitattributes` ngăn tự đổi xuống dòng làm sai checksum. Các candidate trong bảng khảo sát thuộc cùng run nguồn; chỉ candidate được freeze ở trên là model được chọn.

Các bundle `.joblib`, mảng train/validation lớn và cache huấn luyện không đưa lên Git. Tải output phiên bản đã lưu của notebook **`ciciot2023-do-an-stacking-xgboost-meta`** trên Kaggle để lấy bundle chạy local, rồi đặt đúng đường dẫn:

```text
output/stacking_meta_runs/xgb_meta_20261021_092334_9024562d/
    frozen_models/XGB_d4_n200.joblib
```

Bundle này chứa cả tiền xử lý, base models và meta-model; JSON XGBoost riêng lẻ không đủ để chạy toàn bộ pipeline.

SHA256 của bundle được chọn:

```text
72d62f8760e48287fff7dcb590944f7169055d7fc0fb6a5b2969e6287f389033
```

Nếu cần kiểm tra toàn bộ manifest của run XGBoost, tải cả bundle baseline `frozen_models/STACK_DT_RF_HGB_LR_C1.joblib` từ cùng output Kaggle. Manifest nguồn được giữ nguyên, nên hai bundle lớn được liệt kê dù không được lưu trong Git. Thư mục `meta_models/` và các cache lớn cũng chỉ nằm trong output đầy đủ trên Kaggle/local.

Các kết quả pilot, model baseline cũ, recall improvement, blending, LIME/counterfactual và các lần chạy tích hợp trước đã được loại khỏi bộ bàn giao. Hình EDA trong `plots/` vẫn là tài liệu khảo sát dữ liệu.

## Bằng chứng đã kiểm tra

- Chạy trên Kaggle: 50 dự đoán, 50 kết quả SHAP, 50 báo cáo Gemini đạt kiểm tra tự động; 48 phản hồi đạt lần đầu và 2 phản hồi đạt sau một lần sửa diễn đạt.
- Thời gian SHAP cộng dồn khoảng 48.59 giây; thời gian API Gemini cộng dồn khoảng 164.00 giây. Tổng phiên khoảng 458.14 giây, có cả thời gian nghỉ giữa các yêu cầu.
- Sai số bảo toàn SHAP lớn nhất khoảng `2.22e-16`, dưới ngưỡng `1e-5`.
- Rà soát artifact local: 745 mục checksum trong ba manifest nguồn đều khớp với tệp đã tải, gồm hai bundle lớn giữ ở local/Kaggle. Rà soát này không chạy lại training, suy luận model hay gọi Gemini.

50 mẫu tích hợp chỉ có Normal, DDoS, DoS, Mirai và Spoofing; chưa có BruteForce, Recon, Web-Based. Đây là chạy thử tích hợp, chưa chứng minh chất lượng trên đủ 8 lớp. Validation/test nguồn đã từng được xem; kiểm tra tự động không thay thế đánh giá ngữ nghĩa bởi chuyên gia. Human review hiện được tạm hoãn.

## Chuẩn bị cho phần local của Kiên

1. Lấy bundle được chọn ở trên, giữ background `background.npy`, schema và CSV golden từ run SHAP.
2. Tạo môi trường theo `protocol.json` và `requirements.txt` của run tích hợp; tránh dùng chung môi trường đang có phiên bản scikit-learn khác nguồn.
3. Tách các bước nạp artifact, dự đoán, SHAP và Gemini thành module đơn giản; nạp model/background một lần.
4. Đối chiếu xác suất/nhãn với CSV golden và kiểm tra đầu vào trước khi xây dựng API/giao diện.

Các bước local trên chưa được triển khai trong commit đồng bộ kết quả.
