# Plan phương án trên nhánh duong: DT/RF/XGBoost + meta-model

Ngày lập: 10/10/2026. Phụ trách chính: **Nguyễn Ngọc Dương**. Trạng thái: **kế hoạch, chưa triển khai hoặc chạy thực nghiệm**.

## Ràng buộc nhánh Git

**Kế hoạch này chỉ được triển khai trên nhánh `duong`.** Trước mỗi lần chỉnh sửa notebook, module, tài liệu hoặc artifact thuộc phương án blending, kiểm tra `git branch --show-current`; chỉ tiếp tục khi kết quả là `duong`. Nếu đang ở nhánh khác, dừng chỉnh sửa phương án này và báo lại người dùng, không tự chuyển nhánh khi có thay đổi đang làm.

Notebook và cấu hình đưa lên Kaggle phải lấy từ phiên bản làm việc trên `duong`; ghi commit ID nếu đã commit hoặc hash notebook nếu chưa commit vào manifest run. Output tải về của phương án này được quản lý trong workspace trên `duong`. Việc đưa thay đổi sang nhánh khác, merge, commit hoặc push cần chỉ dẫn riêng của người dùng.

## 1. Mục tiêu và quyết định thiết kế

Thực hiện phân loại 8 lớp bằng hai tầng:

1. DT, RF, XGBoost học từ train theo preprocessing hiện tại.
2. Ba model tạo xác suất trên val. Ghép thành `Z_val` gồm 24 cột.
3. Chọn cấu hình meta-model bằng các folds bên trong `Z_val`, sau đó fit meta-model trên toàn `Z_val`.
4. Khóa toàn bộ cấu hình, tạo `Z_test` bằng đúng ba model cơ sở và báo kết quả cuối trên test.

**Có thể dùng lại preprocessing và các file chia sẵn.** Trong phương án này, split có tên `val` được sử dụng làm **dữ liệu phát triển/huấn luyện meta-model**; không còn là validation độc lập cho cả hệ thống sau khi đã fit meta trên nó. Điểm meta-model trên chính toàn bộ `Z_val` đã fit chỉ là train score.

Đây là **holdout blending có meta-model**: base-model học trên train, meta-model học trên một split khác. Thiết kế này khác soft voting, nơi chỉ lấy trung bình xác suất. Tầng cơ sở dùng DT/RF/**XGBoost** theo yêu cầu hiện tại; không tuyên bố tái lập nguyên trạng mô hình GB/DT/RF của bài báo.

Mục tiêu thực nghiệm: xem tầng meta có cải thiện macro-F1 và cân bằng precision/recall BruteForce, Web-Based hay không. Không có bảo đảm blending tăng điểm; ba base-model cùng sai vẫn có thể tạo đầu vào khó phân biệt cho meta-model.

Phạm vi lần này là lập một file plan. Notebook, dữ liệu, model và checklist cũ chưa thay đổi. Làm trên nhánh local `duong`; không tự commit hoặc push.

## 2. Những phần preprocessing được tái sử dụng

| Thành phần | Áp dụng trong phương án mới |
| --- | --- |
| Nhãn | Normal, BruteForce, DDoS, DoS, Mirai, Recon, Spoofing, Web-Based; ID 0–7 |
| Đặc trưng | 44 cột theo schema đã lưu; giữ đúng tên `Magnitue` và thứ tự cột |
| Missing/Inf | Dùng chính quy tắc xử lý và median fit từ train nguồn |
| Nhánh cho classifier | Raw đã xử lý, cast float32 giống baseline; không transform thêm nhánh scaled |
| Pilot | Budget chính 1M, có source indices và manifest; hai lớp hiếm đã được giữ toàn bộ |
| Split | Dùng train/val/test hiện có, kèm mask raw-float32 bổ sung của baseline |
| Audit | Checksum/schema/classes/provenance và overlap theo representation thực dùng |

Không fit lại preprocessing trên val, test hoặc `Z_val`. Nếu sau này thử preprocessing mới, đó phải là data/protocol version riêng, đồng thời tạo lại xác suất ba model và mọi artifact meta phụ thuộc vào chúng.

Preprocessing cũ được fit trên toàn source train, còn classifier dùng pilot. Giữ và công bố đúng phạm vi fit này. Khi chỉ chia folds trong `Z_val` và giữ base-model cố định, không cần fit lại preprocessing ở mỗi meta fold. Nếu chuyển sang tuning base-model bằng CV trong train, thống kê mới học từ dữ liệu phải fit trong fold-train tương ứng [R2].

## 3. Đầu vào Kaggle và lịch sử đánh giá

| Notebook nguồn | Run/input cần attach |
| --- | --- |
| `ciciot2023-do-an-processing.ipynb` | `processed_data/20261007_164739_35f682b9/`: arrays raw, targets, metadata, schema, mapping, preprocessing config |
| `ciciot2023-do-an-pilot.ipynb` | `pilot_data/pilot_20261008_022915_ea9a88b0/`: pilot 1M và manifest/indices |
| `ciciot2023-do-an-models.ipynb` | `model_experiments/models_20261008_073827_d29a37c3/`: ba bundles, probability arrays, predictions/row IDs, audit/masks, checksums, frozen selection |

Ba base-model mặc định để chạy phương án khả thi đầu tiên:

| Thứ tự ghép | Base-model | Experiment ID |
| --- | --- | --- |
| 1 | DT | `DT_n1000000_none_s42` |
| 2 | RF | `RF_n1000000_none_s42` |
| 3 | XGBoost | `XGBoost_n1000000_sqrt_s42` |

Có hai chế độ tương đương về cách tạo tầng meta, cần ghi rõ chế độ thực dùng:

- **Reuse mặc định:** nạp đúng model/bundle baseline đã fit. Các model này đã học trên train; không cần train lại chỉ để ghép xác suất. Kiểm tra golden samples và hash trước khi dùng.
- **Refit để tái lập:** fit đúng config, weight policy và train indices đã khóa trên Kaggle. Model có hash mới thì phải tạo lại `Z`; không ghép cache của model cũ vào model mới chỉ vì cùng tên DT/RF/XGBoost.

Lịch sử phải ghi trong báo cáo: base configs/budget đã được chọn bằng val trước đây; validation/test baseline, run recall và một số ca XAI đã được xem. Vì vậy, cross-validation meta có lợi cho chọn cấu hình, nhưng không xóa sự ảnh hưởng lịch sử của val lên base selection. Test cuối của run mới là **báo cáo trên test lịch sử**, không được gọi là test chưa từng xem.

Nếu muốn một xác nhận độc lập mạnh hơn, cần data/group mới chưa dùng hoặc một protocol đánh giá mới với provenance phù hợp. Không gọi việc chia lại dữ liệu đã xem là tạo test độc lập mới.

## 4. P0 — khóa protocol, kiểm tra dữ liệu và model

**Dương; khoảng 1 ngày.**

1. Tạo protocol mới cho blending: source/pilot/base-run ID, ba model hashes, class/feature order, seed 42, batch size, meta candidate list, fold policy và quy tắc chọn.
2. Khóa base-model trước khi fit meta. Giai đoạn đầu không tìm thêm base configs bằng kết quả meta/test; việc đổi base sẽ tạo một thí nghiệm/protocol riêng.
3. Kiểm tra input hashes, `classes_ == [0,...,7]`, 44 input features và golden probabilities.
4. Dùng chung mask `val_float32_kept_processed_indices.npy` của baseline. Val giữ lại **808.943 dòng**, BruteForce 277, Web-Based 628.
5. Test của baseline giữ lại **765.991 dòng**, BruteForce 297, Web-Based 594. Mask test hiện có đã purge raw-float32 trùng train và **toàn val**. Quy tắc này phù hợp khi meta-model sẽ fit toàn val; tiếp tục dùng nguyên mask cho mọi model được so sánh.
6. Truy vết evaluation index → processed row index → source row index. Row ID cần đi cùng xác suất và nhãn; không xem thứ tự file là bằng chứng đủ về alignment.
7. Kiểm tra cache/artifact metadata mà không mở lại test labels để chọn config. Trong runner mới, chỉ mở test để đánh giá sau freeze.

Đầu ra dự kiến: `protocol.json`, `input_integrity.json`, `base_models_snapshot.json`, các masks/row-ID references. Hoàn tất khi model/schema/hashes và input alignment được xác nhận.

## 5. P1 — tạo Z_val đúng 24 cột

**Dương; khoảng 1 ngày.**

Mỗi model trả ma trận `(n_val, 8)`. Ghép theo **DT → RF → XGBoost**, mỗi block giữ thứ tự class 0–7:

```text
Z_val = concat(P_DT_val, P_RF_val, P_XGB_val, axis=1)
shape = (808943, 24)

DT__p_Normal, DT__p_BruteForce, ..., DT__p_Web-Based,
RF__p_Normal, RF__p_BruteForce, ..., RF__p_Web-Based,
XGBoost__p_Normal, XGBoost__p_BruteForce, ..., XGBoost__p_Web-Based
```

Tên cột và thứ tự được lưu trong `meta_feature_schema.json`; không dựa vào thứ tự model trong `frozen_selection.json`, vì file đó hiện sắp RF trước DT.

Có thể lấy probabilities sẵn tại:

```text
experiments/<experiment_id>/validation/probabilities.npy
experiments/<experiment_id>/validation/predictions.csv.gz
```

Đã kiểm tra header artifact hiện có: cả ba probability arrays đều `(808943, 8)`, float32. Khi triển khai vẫn phải đối chiếu **toàn bộ** row IDs/targets của ba file predictions và checksum; không chỉ kiểm tra dòng đầu.

Yêu cầu cho từng block: finite; xác suất trong [0,1] với tolerance đã định; tổng mỗi hàng gần 1; cột khớp `classes_`; target khớp `y_val[kept_indices]`. Cột true/predicted label, row index, original_label không đi vào `Z`.

Nếu không dùng được cache, dự đoán lại theo batch 25.000 từ đúng pipeline/model đã khóa. Không fit trên val khi tạo `Z_val`, không lấy probabilities từ một model đã refit train+val. Sử dụng xác suất gốc, trước multiplier/decision rule của vòng recall.

`Z_val` float32 chỉ khoảng **74,1 MiB** cho riêng 24 cột; giữ memmap/batch cho dữ liệu 44 cột và hạn chế nạp mọi model/ma trận nhiều bản vào RAM. Bộ nhớ fit meta có thể cao hơn kích thước `Z` này.

Đầu ra: `Z_val.npy`, `y_meta.npy`, `meta_row_ids.csv`, `meta_feature_schema.json`, `probability_alignment_audit.json`. Lưu hashes liên kết với base models và mask.

## 6. P2 — chia folds và chọn meta-model

**Dương; khoảng 2–4 ngày.**

### 6.1. Protocol chính: CV bên trong val dùng làm meta-development

Vì base-model đã cố định và chỉ fit trên train, có thể chia `Z_val` thành **3 folds**, mỗi lượt meta học trên 2 folds và dự đoán fold còn lại. Đây là CV cho **tầng meta**, không phải OOF training của ba base-model [R1].

- Dùng `StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=42)` [R3]. Group theo fingerprint 44 raw-float32 canonical của query; giữ bản lặp cùng group để không nằm ở cả meta-train và meta-validation.
- Nếu có session/device/time metadata được kiểm chứng thì dùng group phù hợp. Source row ID chỉ dùng traceability, không tự coi là session ID.
- Lưu fold indices và support thực của đủ 8 lớp. Dự kiến khoảng 92 BF và 209 Web mỗi held-out fold, nhưng stratification theo group không bảo đảm đúng con số này. Nếu có fold thiếu một lớp hoặc quá ít group hiếm, phải báo và điều chỉnh trước tìm kiếm.
- Trong mỗi fold, weight/resampling/calibration nếu có chỉ fit trên meta-train. Không cân bằng held-out fold.
- Với mỗi cấu hình, ghép predictions held-out thành `meta_oof_probabilities.npy`; tính metrics trên toàn OOF và từng fold.

Điểm OOF dùng chọn hyperparameter vẫn chịu selection bias; không trình bày nó như xác nhận độc lập cho candidate đã chọn. Test lịch sử chỉ được báo sau khi đã khóa.

### 6.2. Meta-model đề xuất

**Meta-XGBoost cây nông là ứng viên chính**, vì đầu vào chỉ 24 score và cần thử cách kết hợp phi tuyến. Giữ Meta-DT/Meta-RF làm đối chứng có giới hạn; không cần thêm Logistic theo hướng mô hình hiện tại.

| Meta-model | Cấu hình pilot và hướng thử |
| --- | --- |
| XGBoost chính | `max_depth=2`, `min_child_weight=5`, `n_estimators=200`, `learning_rate=0.05`, `reg_lambda=5`, `reg_alpha=0`, `subsample=1`, `colsample_bytree=1`, `max_bin=256`, CPU hist, `multi:softprob`, `num_class=8` |
| DT đối chứng | `max_depth=6`, `min_samples_leaf=10`, seed 42; thử leaf nhỏ hơn khi có tín hiệu bỏ sót lớp hiếm |
| RF đối chứng | 100 trees, depth 8, leaf 5, `max_features=1.0`, 4 threads, seed 42 |

Vòng pilot: mỗi meta-model chạy 3 folds với none và inverse-sqrt weights → **18 meta fits**. Weight tính từ labels của fold-train, chuẩn hóa trung bình sample weight =1; lưu vector weight theo class. Không tự oversample val ngay ở vòng đầu.

Sau pilot, chỉ mở tuning cho meta-model tốt nhất: tối đa **8 cấu hình**, cùng 3 folds → tối đa 24 fits nữa. Với XGBoost, không gian tham khảo:

```text
max_depth: [2, 3, 4]
min_child_weight: [1, 5, 10]
learning_rate: [0.03, 0.05, 0.1]
n_estimators: [100, 200, 400]
reg_lambda: [1, 5, 10]
reg_alpha: [0, 0.1]
```

Đây là lấy mẫu hữu hạn bằng seed, không chạy toàn Cartesian grid [R4]. Mặc định số trees cố định, chưa dùng early stopping. Nếu dùng early stopping sau này, cần inner split trong meta-train; không dùng outer fold để vừa chọn iteration vừa gọi đó là đánh giá độc lập.

Meta-RF/XGB quá sâu có thể ghi nhớ vài trăm mẫu rare. Chọn mức regularization dựa trên OOF, không dựa training accuracy gần 100%.

### 6.3. Tiêu chí chọn và baseline đối chứng

So sánh trên đúng cùng OOF row IDs với:

1. DT cơ sở.
2. RF cơ sở.
3. XGBoost cơ sở.
4. **Soft voting bằng nhau** của ba probability blocks, không có meta-model hoặc tham số học thêm.
5. Các meta-model, dự đoán held-out theo fold.

Chỉ số chính: macro-F1. Báo riêng precision/recall/F1 BF/Web, min recall hai lớp, accuracy, weighted-F1, Normal false-alarm rate và confusion matrix.

Quy tắc đề xuất khóa trước khi chạy: trong candidate đạt precision **≥0,30 ở mỗi lớp hiếm**, chọn macro-F1 OOF cao nhất; hòa trong 0,002 thì ưu tiên min rare recall, sau đó fit/inference time. Floor 0,30 là mốc kế thừa vòng recall cũ, không phải tiêu chuẩn IDS chung. Nếu không candidate nào đạt, báo thất bại điều kiện, không tự hạ floor.

Lưu thêm bảng Pareto để thấy trường hợp recall tăng nhưng precision/macro-F1 giảm. Recall ≥0,85 cả hai lớp là mục tiêu khám phá; không bắt buộc một model có accuracy cao hơn phải được chốt.

Không thêm multiplier hay threshold class ở vòng đầu: quyết định cuối dùng argmax meta probabilities. Nếu cần tối ưu rule sau đó, tạo phase/protocol riêng với nested CV hoặc một development partition dành riêng; không dùng meta-train score hoặc test labels chọn rule.

Đầu ra: `meta_folds.json`, `meta_cv_results.csv`, OOF probabilities/predictions, per-class metrics, confusion matrices và timing từng trial.

## 7. P3 — fit meta cuối và khóa hệ thống

**Dương; khoảng 1 ngày.**

1. Khóa loại meta-model, params, weight policy và rule bằng kết quả CV.
2. Nếu ngân sách cho phép, kiểm tra ổn định seed 42/2026/3407 của candidate trên cùng folds; ghi đây vẫn là development. Không chọn seed riêng theo test.
3. Fit meta cuối trên **toàn `Z_val` và y_val tương ứng mask**. Tính weights từ toàn meta-training split. Lưu final fit time/RAM riêng, không trộn với chi phí CV.
4. Giữ đúng ba base-model đã tạo `Z_val`. **Không refit chúng trên train+val sau bước này**, vì meta-model đã học từ xác suất của phiên bản base cố định và val còn là train của meta.
5. Xuất một bundle có schema raw 44 cột, schema meta 24 cột, class order, preprocessing, ba base-model và meta-model.
6. Kiểm tra predictions trước/sau save-load bằng golden samples; đối chiếu đường suy luận thủ công với wrapper.
7. Ghi `frozen_blending.json` chứa toàn bộ model/config/hashes và thời điểm freeze, trước mở test để đánh giá.

Lưu `meta_training_rows=808943` và support hiếm 277/628. Tổng dữ liệu có nhãn đã dùng fit hệ thống gồm train base **và val meta**; không mô tả blending chỉ học 1M dòng nếu meta còn học thêm 808.943 dòng.

Khối xác suất của mỗi base-model cộng thành 1 nên 24 cột có phụ thuộc; vẫn giữ đủ 24 theo thiết kế. Audit các vector `Z` giống nhau nhưng labels khác để mô tả giới hạn biểu diễn. Không xóa khỏi test các `Z_test` giống `Z_val` chỉ để tăng điểm: các raw inputs khác nhau có thể tạo cùng probabilities, đây là hành vi tự nhiên của classifier.

## 8. P4 — Z_test và báo cáo cuối sau freeze

**Dương, Kiên đối chiếu; khoảng 1 ngày.**

1. Chỉ chạy phase test khi `RUN_FINAL_TEST=True` và frozen hashes hợp lệ; mặc định notebook thử nghiệm đặt False cho đến khi xong phase chọn.
2. Dùng cùng mask test baseline đã audit; nếu thay nguồn/train/mask thì tạo protocol mới và giải thích population thay đổi.
3. Tạo probabilities test từ ba base-model đã khóa, ghép theo đúng 24 cột để có `Z_test`.
4. Có thể dùng cache `test/<experiment_id>/probabilities.npy` sau freeze nếu hashes/row IDs/classes khớp; cache cũ được tạo trước đây không biến test thành dữ liệu chưa từng xem.
5. Meta-model chỉ gọi `predict_proba`/`predict`, không fit, không chỉnh weight/threshold bằng test.
6. Báo DT/RF/XGBoost, soft voting và blending trên cùng test rows. Ghi rõ đây là test lịch sử, cùng baseline theo preprocessing/split hiện tại.
7. Mỗi candidate cuối được báo một lần trong run, có marker/hash để resume không đổi cấu hình. Nếu sau khi xem test muốn sửa model, đó là vòng development mới và phải công bố lịch sử; không tiếp tục gọi là đánh giá test độc lập.

Bảng tổng hợp: macro precision/recall/F1; accuracy; weighted-F1; precision/recall/F1/support cả 8 lớp; Normal FPR; confusion counts và normalized; log-loss nếu phù hợp; memory/hardware; thời gian base fit, meta search, final meta fit, và inference.

**Đánh giá công bằng cần ghi thêm:** blending được học nhãn val còn base-model đối chứng ban đầu chỉ học train. Đây là so sánh pipeline triển khai trên cùng test, có khác biệt ngân sách dữ liệu huấn luyện. Nếu muốn tách riêng lợi ích kiến trúc, làm ablation riêng refit các classifier đơn trên train+val với hyperparameters đã khóa và cùng held-out test; không thay ba base-model bên trong blending. Không kết luận mọi gain đều do meta architecture.

Khoảng tin cậy/độ lệch seed cần dựa đúng đơn vị query/group; không coi 3 model hoặc 3 seeds là thêm sample độc lập.

## 9. P5 — bàn giao pipeline và XAI cho Hải/Kiên

Luồng suy luận cuối:

```text
CSV/raw frame 44 feature
  → preprocessing cố định + float32
  → DT/RF/XGBoost predict_proba: mỗi model 8 class
  → ghép Z 24 cột theo schema
  → meta-model predict_proba: 8 class
  → argmax → label cuối
```

Các API dự kiến: `load_bundle(bundle_dir)`, `predict_proba_raw(frame)`, `predict_raw(frame)`, và helper `build_meta_features(frame)`. Serialize custom wrapper/module theo đường import ổn định, có `fit`, `predict_proba`, `predict`, `classes_` và fitted-state tương thích sklearn; không chỉ lưu một class nằm trong notebook `__main__`. Đây là hạng mục triển khai sau, chưa tạo module trong bước lập plan.

Hai mức giải thích:

- **Meta-level:** giải thích 24 score để biết meta dựa vào model/lớp nào, ví dụ `RF__p_Web-Based`. Không diễn giải score này như một feature traffic nguyên thủy.
- **Toàn pipeline:** LIME/CF trên 44 feature raw gọi toàn hàm `raw → base probabilities → meta probabilities`. Khi thay query, phải chạy lại cả ba base-model; không giữ `Z` cũ rồi gọi đó là XAI end-to-end.

Nếu giải thích trực tiếp `Z`, 24 số không được perturb tùy ý vì mỗi block có ràng buộc tổng xác suất; ưu tiên các vector score sinh từ raw samples thật hoặc một bộ sinh có ràng buộc được mô tả rõ.

Hải dùng model/run/hash mới và chọn lại ca theo **dự đoán cuối của blending**. Biểu đồ RF hoặc baseline cũ không thể thay cho giải thích blending. Dùng quality gates LIME theo plan XAI đã lập; run LIME trước đây không đạt nên không coi tăng sample count là đủ sửa chất lượng.

Kiên nạp bundle để web demo suy luận trên CSV/mẫu input; không cần tải toàn bộ train/val/test để chạy demo. Đo RAM và end-to-end latency thật của bundle trên máy demo, vì cần giữ/chạy ba base-model và meta-model. Kết quả Kaggle và schema/hashes đủ làm bàn giao model nhưng vẫn cần người nhận xác nhận nạp/chạy được.

## 10. Cấu trúc notebook và artifact dự kiến

Notebook đề xuất: `notebook/ciciot2023-do-an-blending.ipynb`. Kaggle output: `/kaggle/working/blending_experiments/blending_<timestamp>_<id>/`.

Các phần: config/protocol → input/model audit → tạo Z_val → meta folds → pilot/CV → chọn và fit meta cuối → bundle/golden checks → freeze → test khi bật → tổng hợp/handoff.

```text
blending_<run_id>/
  protocol.json
  input_integrity.json
  base_models_snapshot.json
  meta_feature_schema.json
  meta_row_ids.csv
  Z_val.npy
  y_meta.npy
  meta_folds.json
  meta_cv_results.csv
  trials/<trial_id>/
  frozen_blending.json
  test/<candidate_id>/
  final_comparison.csv
  handoff/
    preprocessing/config/schema/label_mapping
    base_models/DT, RF, XGBoost
    meta_model.joblib
    blending_module.py
    bundle_metadata.json
    golden_samples.npz
    example_raw_features.csv
    requirements_runtime.txt
    README_HANDOFF.md
```

Mỗi checkpoint/cache gắn protocol/model/data hashes; hoàn tất trial mới ghi completion marker. Resume skips đúng artifact đã hoàn tất, không trộn trials có input/model/fold khác nhau. Lưu sau mỗi meta fold/trial và mỗi batch tạo Z; phase test có marker riêng. `Z_test` chỉ xuất sau freeze.

Timing cần tách training/search và inference. Đo 3 base predictions + concat + meta prediction để báo chi phí thật; không chỉ đo meta vài milliseconds. Cache có thể giảm chi phí nghiên cứu nhưng không thay thế benchmark suy luận toàn pipeline.

## 11. Lộ trình và tiêu chí nghiệm thu

| Ưu tiên | Công việc | Phụ trách | Thời gian dự kiến |
| --- | --- | --- | --- |
| 01 | Khóa protocol, audit source/base/mask | Dương | 1 ngày |
| 02 | Z_val 24 cột, kiểm tra alignment/provenance | Dương | 1 ngày |
| 03 | Meta CV 3 folds, pilot/tuning hữu hạn | Dương | 2–4 ngày |
| 04 | Fit meta cuối, export/reload/freeze | Dương | 1 ngày |
| 05 | Báo test lịch sử một lần, phân tích lỗi | Dương + Kiên | 1 ngày |
| 06 | XAI blending và demo integration | Hải + Kiên | 2–4 ngày, có thể chuẩn bị song song |

Chạy trên Kaggle CPU, cùng môi trường tương thích baseline (sklearn 1.6.1, XGBoost 3.4.1 và versions theo bundle). Bắt đầu với cache ba base-model để tập trung chi phí ở meta fits. Đặt ngân sách tìm kiếm CPU ban đầu 4 giờ, checkpoint từng trial; đây là budget thực nghiệm đề xuất, không phải giới hạn Kaggle hay cam kết runtime. Chỉ mở rộng nếu pilot có tín hiệu cải thiện.

Điều kiện nghiệm thu phương án: tái tạo đúng Z; meta không học test; model/schema/version có provenance; có OOF development và báo test sau freeze; đủ metrics 8 lớp và timing end-to-end; bundle nạp lại có predictions khớp.

Điều kiện chọn blending làm model demo: ưu tiên macro-F1 và hai lớp hiếm theo protocol; ghi chi phí inference. Nếu meta thua RF/soft voting hoặc gain chỉ do precision giảm mạnh, vẫn báo kết quả âm và giữ model tốt hơn theo tiêu chí đã khóa. Nếu ba base-model cùng sai nhiều trên rare, phân tích error coverage trước khi tăng số tầng/độ sâu.

### Checklist dự kiến

- [ ] P0: protocol/model/masks/input audit.
- [ ] P1: Z_val 24 cột, labels và row IDs khớp.
- [ ] P2: meta CV, bảng đối chứng, chọn candidate.
- [ ] P3: fit meta toàn val, export/reload và freeze.
- [ ] P4: báo test lịch sử, metrics/confusion/time.
- [ ] P5: XAI đúng pipeline blending, Hải/Kiên xác nhận bàn giao.

## 12. References và kế hoạch liên quan

- **[R1]** [sklearn StackingClassifier](https://scikit-learn.org/1.6/modules/generated/sklearn.ensemble.StackingClassifier.html): phân biệt base-models, final estimator, CV và trường hợp prefit. Runner dự kiến tạo Z thủ công để làm đúng holdout blending; không mặc định dùng `StackingClassifier.fit` với train, vì khi đó quy trình mặc định khác thiết kế train/val này.
- **[R2]** [sklearn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html): giữ fit statistics trong training split, tránh leakage.
- **[R3]** [StratifiedGroupKFold](https://scikit-learn.org/1.6/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html): phân tầng class và tránh group xuất hiện ở hai fold.
- **[R4]** [XGBoost parameters](https://xgboost.readthedocs.io/en/stable/parameter.html): multiclass objective, depth/child weight và regularization; khi triển khai đối chiếu API version đã khóa.
- [Bài báo Toward Enhanced Attack Detection and Explanation…](https://doi.org/10.1109/ACCESS.2023.3336678): tham khảo ensemble/XAI; phương án 24 score + meta-model này được mô tả riêng, không gán metric paper cho model mới.
- [Plan kiểm chứng XAI và cải thiện mô hình](Nguyen_Ngoc_Duong_04_ke_hoach_cai_thien_model_tu_xai.md): quality gates, error analysis và lịch sử run trước.
- [Phân công dự án](README.md): Dương data/models; Hải XAI; Kiên integration/evaluation.
