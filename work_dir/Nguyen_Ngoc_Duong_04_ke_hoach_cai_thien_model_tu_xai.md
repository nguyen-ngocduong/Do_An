# Plan: kiểm chứng XAI và cải thiện DT/RF/XGBoost cho phân loại 8 lớp

Ngày lập: 10/10/2026. Trạng thái: **kế hoạch để xem xét, chưa triển khai**. Không thay đổi notebook, preprocessing, model hoặc checklist hiện hành trong lần lập kế hoạch này.

Dương phụ trách dữ liệu/mô hình; Hải phụ trách kiểm chứng và phân tích LIME/counterfactual; Kiên phụ trách khả năng nạp pipeline và trình bày kết quả. Các thực nghiệm mới chạy trên **Kaggle CPU**; local chỉ đọc artifact, sửa tài liệu và kiểm tra tĩnh.

## 1. Phạm vi và nguồn bằng chứng

Giữ bài toán 8 lớp, theo thứ tự: Normal, BruteForce, DDoS, DoS, Mirai, Recon, Spoofing, Web-Based. Nhãn gốc dùng phân tầng và truy vết, không đưa vào feature và không mở rộng đầu ra thành 34 lớp.

| Nguồn | Run và nội dung dùng đối chiếu |
| --- | --- |
| XAI mới | `output/xai_lime_counterfactual/lime_cf_20261010_041117_9d2778fc/`: manifest, fidelity, predictions, CF, timing và biểu đồ |
| Model được giải thích | `output/model_experiments/models_20261008_073827_d29a37c3/`: handoff DT/RF/XGBoost và toàn bộ metrics/confusion matrix validation |
| Processing | `output/processed_data/20261007_164739_35f682b9/`: schema, support, missing/overlap/correlation audits |
| Pilot | `output/pilot_data/pilot_20261008_022915_ea9a88b0/`: train 1M và manifest |
| Vòng cải thiện đã chạy | `output/recall_experiments/recall_20261008_093605_937d9815/`: ablation, confirmation, old-test và protocol |

XAI mới đang giải thích **baseline**, không phải model cải thiện recall của run `recall_*`. Sau khi đổi model, phải giải thích lại đúng hash/model ID; không dùng biểu đồ baseline như bằng chứng cho model mới.

Các kết luận bên dưới đến từ đọc artifact đã tải về, không phải một lần chạy lại model độc lập.

## 2. Nhận xét kết quả hiện tại

### 2.1. Chạy thành công nhưng chất lượng LIME chưa đạt

`run_status.json` ghi `execution_complete`; manifest ghi golden check đạt cho ba pipeline. Sáu ca phân tích sâu gồm đúng/sai của Normal, BruteForce và Web-Based. Hai ca Web-Based đều là **CommandInjection**, chưa đại diện cho các nhãn gốc khác thuộc Web-Based.

| Model | R² holdout trung bình, config được chọn | Sai số xác suất tại query | Tỷ lệ đạt quy tắc chất lượng |
| --- | ---: | ---: | ---: |
| DT | 0,1678 | 0,4745 | 0% |
| RF | 0,3237 | 0,2666 | 0% |
| XGBoost | 0,2549 | 0,4791 | 0% |

Nguồn: [`lime_model_comparison.csv`](../output/xai_lime_counterfactual/lime_cf_20261010_041117_9d2778fc/lime_model_comparison.csv). Sai số 0,4745 tương đương khoảng 47,45 điểm phần trăm xác suất. `explanations=18` mỗi model là tổ hợp ca/lớp giải thích/seed; **không phải 18 query độc lập**. Cả 54 bản giải thích được chọn đều không đạt.

Trung bình chỉ **7,91%** holdout neighbors của các config được chọn đạt kiểm tra miền. Khi tách config: `local_continuous` chỉ đạt khoảng **0,061%**, còn `local_quartile` khoảng **71,62%**. Vẫn chưa có giải thích nào đạt toàn bộ ngưỡng fidelity/point error/domain. Không được suy luận feature quan trọng rồi xóa cột dựa trên các thanh LIME này.

Code hiện tại sinh biến liên tục độc lập; kiểm tra miền được dùng báo cáo, chưa dùng bảo đảm neighborhood hợp lệ trước fit. Chọn config chủ yếu bằng R² còn có thể ưu tiên một neighborhood gần như hoàn toàn không hợp lệ. Đây là vấn đề của thiết kế explainer cần sửa trước khi mở rộng số ca, không chứng minh dữ liệu đầu vào thật bị hỏng.

RF có Jaccard top-feature trung bình khoảng 0,842 qua hai seed, nhưng sự ổn định không bù được fidelity thấp. Một surrogate sai có thể ổn định.

### 2.2. Counterfactual hữu ích để đặt giả thuyết

Mỗi model có 5 lượt tìm CF và 1 lượt `already_target`. Cả **15/15 lượt tìm** thành công, tạo 30 CF. Số feature thay đổi của CF tốt nhất trung bình: DT 5,0; RF 5,6; XGBoost 4,4. Nguồn: [`counterfactual_model_comparison.csv`](../output/xai_lime_counterfactual/lime_cf_20261010_041117_9d2778fc/counterfactual_model_comparison.csv).

Các CF đều được ghi `synthetic_hybrid=True`, `traffic_feasibility=not_certified`. Thành công nghĩa là vector tìm được đạt lớp đích theo model và các checks hiện có; không phải traffic thật đã đổi nhãn, không phải 100% recall, và không chứng minh CF gần nhất toàn cục. Sáu query được chọn có chủ đích, nhiều lượt cùng query nên không coi 15 lượt là 15 quan sát độc lập.

| Ca | Bằng chứng dự đoán | CF và hàm ý cần kiểm chứng |
| --- | --- | --- |
| `case_09`, BruteForce | DT → Recon; RF/XGBoost đúng. RF đúng nhưng xác suất BruteForce chỉ 0,28994 | DT CF1 đổi timing và một số flag-counts, tổng 6 cột, chuyển về BruteForce. Giả thuyết ranh giới DT chưa tách tốt vùng này; không chứng minh chỉ một cột gây lỗi |
| `case_12`, CommandInjection | Cả ba → BruteForce. DT hòa 0,5/0,5; RF BF 0,27706 vs Web 0,22673; XGB BF 0,39138 vs Web 0,32431 | DT/XGB CF1 đổi 10 thống kê kích thước; RF đổi 13 cột gồm kích thước, header và rate. Đây là bằng chứng một phép thay đổi **đồng thời theo nhóm** có thể vượt ranh giới |
| `case_19`, Normal | DT đúng với hòa Normal/Web 0,5/0,5; RF/XGB → Web-Based | RF CF1 đổi header/rates/counts; XGB đổi timing. Gợi ý cần kiểm tra false positives từ Normal, không chỉ cứu false negatives |
| `case_02` và `case_08`, attack đúng | BruteForce và CommandInjection đúng ở cả ba | CF tốt nhất sang Normal đổi nhóm timing 3 cột. Cần xem độ phụ thuộc timing lặp lại ở nhiều ca và subtype hay chỉ là đường tìm CF của thuật toán |

DT hòa xác suất chọn class ID nhỏ hơn theo `argmax`: `case_12` chọn BruteForce trước Web-Based. Đây là cơ chế cụ thể tại ca này. Chưa đủ bằng chứng nói toàn bộ lỗi do tie hoặc overfitting; cần kiểm tra leaf support, depth, purity và tần suất tie.

**Chỉnh cách trình bày ở vòng triển khai sau:** ảnh CF `case_12` RF ghi 12 feature do chỉ vẽ top 12, trong CSV thực tế thay đổi 13. Cần tách tổng số thay đổi và số cột được vẽ. Nhãn khoảng cách trên ảnh ghi `|Δx|/IQR`, trong code có log1p và fallback std; phải dùng đúng công thức trong manifest. Cột thay đổi lớn không tự động là cột có tác động dự đoán lớn nhất.

### 2.3. Lỗi phổ biến phải lấy từ toàn validation

Validation baseline sau audit có 808.943 dòng, trong đó BruteForce 277 và Web-Based 628. Recall baseline:

| Model | BruteForce | Web-Based | Precision BruteForce | Precision Web-Based |
| --- | ---: | ---: | ---: | ---: |
| DT | 62,82% | 67,68% | 33,40% | 42,12% |
| RF | 56,68% | 53,66% | 89,71% | 42,34% |
| XGBoost | 69,68% | 74,68% | 37,33% | 29,59% |

Nguồn: `experiments/<experiment_id>/validation/per_class_metrics.csv` và `confusion_matrix_counts.csv` của baseline.

Với RF: BruteForce đúng 157/277, nhầm Normal **60**, Recon **30**, Spoofing **20**, Web-Based **10**. Web-Based đúng 337/628, nhầm Spoofing **132**, Recon **83**, Normal **75**, BruteForce **1**. Vì vậy `case_12` rất đáng nghiên cứu nhưng không đại diện cho lỗi Web-Based của RF. XGBoost cũng nhầm Web-Based sang Recon/Spoofing nhiều hơn sang BruteForce.

Plan phải ưu tiên các cặp BruteForce ↔ Normal/Recon/Spoofing và Web-Based ↔ Spoofing/Recon/Normal; vẫn giữ các ca Web-Based ↔ BruteForce để nghiên cứu vùng khó chung.

### 2.4. Các nguyên nhân được hỗ trợ đến mức nào?

| Giả thuyết | Bằng chứng hiện tại | Trạng thái |
| --- | --- | --- |
| Ít dữ liệu lớp hiếm, mất cân bằng mạnh | Pilot 1M có 1.488 BF, 2.768 Web, 725.553 DDoS và 172.471 DoS | Đã xác nhận phân bố; tác động lên lỗi cần ablation |
| Trùng/chồng lấn vùng đặc trưng thống kê giữa các lớp | Ca khó có dự đoán gần nhau; CF theo nhóm size/timing đổi dự đoán | Có dấu hiệu cục bộ, chưa chứng minh cho toàn lớp |
| DT/RF chưa đủ độ phân giải ở vùng hiếm | DT depth=20, leaf=2; RF 200 trees, depth=20, leaf=2, max_features=sqrt | Giả thuyết; cần leaf audit và tuning có đối chứng |
| Web-Based chứa nhiều subtype khác nhau | Nhãn gốc thuộc nhiều loại tấn công; XAI hiện chỉ xem CommandInjection | Cần phân tích đủ subtype trong dữ liệu của đồ án [R1] |
| Lỗi nhãn/NaN/imputation là nguyên nhân chính | Audit báo 0 NaN/Inf cả ba split và 0 nhóm conflicting label trong các representation đã audit | Chưa có bằng chứng hỗ trợ; không relabel hoặc đổi imputation tùy ý |
| Feature tương quan làm perturbation thiếu thực tế | Train audit: Rate/Srate=1; Std/Radius≈0,99998; Number/Weight≈0,99946; miền LIME rất thấp | Cơ sở thiết kế lại neighborhood; tương quan không tự chứng minh nên xóa feature |

Pilot đã giữ **toàn bộ BF/Web của processed train**. Tăng từ 1M lên toàn train 5,36M không tăng hai support này, chủ yếu thêm lớp khác. Muốn có nhiều mẫu hiếm thật phải kiểm tra nguồn bổ sung hợp lệ, không nhân bản rồi gọi là tăng độ đa dạng.

Vòng recall cũ đã có **63 dòng ablation** về sampling, weighting, tuning, feature selection và seed. Trên old-test, ứng viên `C_2f13b00cf8811500` có recall BF 73,40%, Web 69,70%, precision 32,68%/44,56%; ứng viên balanced có recall 73,06%/78,45% nhưng precision Web chỉ 29,68%. Không xem đây là các thử nghiệm chưa làm hoặc lặp lại nguyên grid mà kỳ vọng khác.

## 3. Protocol trước khi thực nghiệm mới — P0

**Dương + Hải, khoảng 1–2 ngày.**

1. Khóa một protocol mới: model IDs/hash, feature/class order, budget, seed, tiêu chí chọn, lịch sử đã xem validation/test. Không resume bằng protocol cũ khi đã đổi thiết kế.
2. Tách hai luồng: validation cũ dùng chẩn đoán và báo cáo lịch sử; lựa chọn mới ưu tiên prediction **out-of-fold từ train**. Các file confirmation/test cũ đã được xem, không gọi chúng là holdout mới chưa đụng tới.
3. Tạo 3 folds train, stratify theo 8 lớp và giữ cùng nhóm fingerprint raw-float32 trong một fold. Nếu có metadata session/device/time đáng tin cậy, ưu tiên group theo đơn vị đó; source row index không phải session ID.
4. Trong mỗi fold, sampling/weights/feature-selection/thống kê mới chỉ fit trên fold-train. Nếu cần refit preprocessing hoặc khôi phục giá trị trước imputation, đọc CSV nguồn trên Kaggle với mapping source indices. Không fit scaler/feature selection trước chia fold [R7].
5. Tạo sổ thí nghiệm gắn giả thuyết với biến thay đổi. So sánh candidate với baseline **refit trên cùng fold**, rồi mới báo bảng validation lịch sử. Không so điểm từ hai tập support khác nhau như một ablation thuần.
6. Nếu có dữ liệu nguồn mới chưa dùng, dự trữ group độc lập để xác nhận cuối. Nếu không có, dùng CV/OOF và công bố giới hạn; reshuffle dữ liệu cũ không xóa lịch sử đã xem.

Đầu ra dự kiến: `protocol_v2.json`, `fold_manifest.json`, `experiment_registry.csv`. Tiêu chí hoàn tất: không overlap nhóm giữa folds; đủ support; IDs và preprocessing truy vết được.

## 4. Sửa và kiểm chứng explainer — P1

**Hải chủ trì, Dương đối chiếu feature; khoảng 2–4 ngày.** Đây là bước ưu tiên trước mở rộng LIME.

### LIME

- Chạy pilot **60 query**, trải đều các nhóm đúng/sai, subtype và đích nhầm lẫn. Giữ nhóm ca chung cho cả ba model.
- Ghi số perturbation vi phạm theo nguyên nhân: âm, ngoài miền, binary, Min/AVG/Max, context, và quan hệ phụ thuộc được xác minh từ train. Hiện chỉ có tỷ lệ tổng nên chưa biết ràng buộc nào gây phần lớn rejection.
- Ưu tiên background train cùng context thật. Hiện `case_19` chỉ có 249 hàng; bốn ca khác fallback toàn context. Ghi số hàng cùng context, khoảng cách và độ phủ. Không ép đủ 2.000 bằng cách lấy hàng xa hoặc lặp rồi coi như quan sát mới.
- So sánh hai cách sinh: perturbation liên tục trong không gian phù hợp rồi **reject** vi phạm; và sampling có điều kiện theo nhóm feature từ các hàng train gần query. Với Rate/Srate, size-statistics, timing/count-weight, giữ quan hệ đã xác minh. Không mặc định count là integer vì dữ liệu chứa giá trị trung bình phân số.
- Nếu dùng mask nhóm hoặc bộ sinh mới, đây là **biến thể LIME có ràng buộc**: xuất thuật toán và không gọi là tái lập nguyên trạng LIME chuẩn/bài báo. Ma trận giải thích dùng fit/holdout phải khớp chính bộ sinh mới, không ghép coefficient từ hai representation khác nhau [R2].
- Tách fit-neighborhood và holdout-neighborhood. Holdout sinh riêng, bỏ query gốc khi đo fidelity. Giữ hash bằng nhau giữa models cho cùng config/case/seed.
- Chọn cấu hình đạt domain trước, rồi xét fidelity/point error. Nếu không có config đạt, ghi **không có giải thích đủ tin cậy**, không tự chọn best để diễn giải.
- Mốc pilot: 2.000–5.000 perturbation **được chấp nhận** cho fit, 1.000 holdout hợp lệ; tối đa số đề xuất/thời gian mỗi ca để tránh rejection loop vô hạn. Ghi cả acceptance rate trước lọc, không chỉ 100% sau lọc.
- Giữ ngưỡng ban đầu R² ≥0,70 và point error ≤0,05; neighborhood dùng fit/holdout đạt checks ≥90%, mục tiêu ≥95%. Đo effective sample size sau weighting, variance xác suất và độ đa dạng hàng. Surrogate đầu ra gần hằng cần ghi riêng; không coi R² NaN là thất bại classifier hoặc giải thích đạt.
- Dùng 3 seed trên pilot; báo Jaccard, dấu/rank hệ số và tỷ lệ đạt theo từng nhóm lỗi. Không giảm ngưỡng chỉ để có nhiều biểu đồ đẹp.
- Khóa config từ pilot; dùng các ca khác để đánh giá chất lượng cuối. Nếu quality không đạt, chuyển phần kết luận sang CF, native tree-path/leaf diagnostics và đối chiếu hàng thật, công bố giới hạn LIME.

### Counterfactual

- Giữ prototype truy xuất từ **train**, không lấy validation/test làm donor. Thử pool lớn hơn từ processed train để tăng Normal/Recon/Spoofing đa dạng; BF/Web đã có toàn bộ trong reference hiện tại.
- So sánh prototype thật chưa trộn và hybrid sau restore, giữ fixed context. Thử số donor 3 → 10 → 20 trên pilot, không áp dụng ngay toàn bộ query.
- Đo success, số cột/nhóm thay đổi, distance, target gap, thời gian, đa dạng CF và lý do không tìm được. Tách ca vốn đã đúng khỏi ca cần cứu; đúng với xác suất <0,50 vẫn là đúng theo argmax, không nhập lẫn với thất bại search.
- So sánh ràng buộc cơ bản và ràng buộc phụ thuộc mạnh hơn. Mẫu hybrid vượt basic checks vẫn không có chứng nhận traffic khả thi [R3].
- Với query thiếu donor cùng context, báo thiếu coverage; có thể làm phân tích context khác riêng, không gọi đó là cùng bài toán CF cố định context.
- Không dùng target của CF synthetic làm ground-truth rồi thêm vào train.

Đầu ra: `xai_quality_audit.csv`, `neighbor_rejection_reasons.csv`, `lime_quality_by_error_group.csv`, `cf_quality_by_error_group.csv`, protocol explainer đã khóa. Chỉ mở rộng phần LIME đã chứng minh đủ chất lượng cho nhóm ca tương ứng.

## 5. Mở rộng số mẫu để tìm quy luật lỗi — P2

**Hải phân tích, Dương chuẩn bị prediction/metadata; khoảng 3–5 ngày.**

Không có trần khoa học 200 hoặc 2.000 query. Phân biệt query thật được giải thích, background train và perturbation synthetic; tăng perturbation không tăng số query thật.

| Luồng | Quy mô đề xuất | Vai trò |
| --- | --- | --- |
| Prediction/error audit | Toàn 808.943 validation rows từ artifact baseline; train OOF mới | Đếm đúng/sai và các cặp nhầm lẫn; không phải chạy LIME cho toàn tập |
| Focal validation bank | Toàn bộ 277 BF + 628 Web = **905 query thật** | Bao phủ toàn lớp hiếm trên validation hiện có; đây vẫn là development data |
| Nhóm đối chứng | Khoảng 600 query Normal/Recon/Spoofing, cân bằng đúng/FP vào lớp hiếm | Tránh tăng recall bằng cách dự đoán lớp hiếm cho quá nhiều mẫu khác |
| Quality pilot | 60 query từ bank | Khóa phương pháp, kiểm tra coverage và đo chi phí |
| XAI diện rộng ban đầu | 240–400 query chung, không trùng quality pilot khi còn đủ ca | LIME có quality gate; CF và native diagnostics cho nhóm lỗi |
| Mở rộng sau pilot | CF tối đa 905 focal query + đối chứng; LIME mở rộng dần theo chi phí và tỷ lệ đạt | Không bắt buộc chạy toàn bank nếu quality/coverage chưa ổn |

Chọn ngẫu nhiên với seed trong từng tầng `(true class, original label, predicted class/error pattern, margin band)`; bao gồm đúng high-margin, đúng low-margin, sai high-margin, sai low-margin và model disagreement. Không lấy hàng đầu tiên trong file. Giữ same query cho ba model, nhưng outcome ghi riêng từng model.

Web-Based phải phủ `CommandInjection`, `SqlInjection`, `XSS`, `Uploading_Attack`, `BrowserHijacking`, `Backdoor_Malware` khi các subtype hiện diện. Subtype ít thì lấy hết và ghi support; mục tiêu tối thiểu 20–30/query mỗi subtype nếu đủ, không nhân bản để đạt quota. BF vẫn một lớp đầu ra, phân tích theo context, nguồn và cặp nhầm lẫn.

Bank lấy mẫu có chủ đích chỉ dùng chẩn đoán. Khi tổng hợp, báo tỷ lệ theo tầng và trọng số theo population nếu cần; không tính accuracy/recall population trực tiếp từ bank cân bằng đúng/sai. Kiểm tra fingerprint trùng trong validation; báo raw-row support và unique-vector support. Bootstrap theo nhóm/vector hoặc session hợp lệ, không theo bản lặp seed của cùng query.

Tổng hợp các nhóm feature hay xuất hiện trong **CF thành công và LIME đạt**, so với ca đúng cùng subtype/context. Cụm feature có tương quan cần báo theo nhóm; tần suất được greedy algorithm thay đổi còn chịu ảnh hưởng cách chia nhóm và donor, không tự là causal importance. Có thể thêm grouped permutation trên OOF để đối chiếu; công bố giới hạn tương quan [R8].

Đầu ra: case-bank manifest, bảng lỗi theo subtype/context, bảng feature-group theo nhóm lỗi, khoảng tin cậy và 8–12 ca điển hình. Không suy ra nguyên nhân toàn lớp từ một ảnh.

## 6. Fine-tune có giả thuyết và đối chứng — P3

**Dương chủ trì, Hải cung cấp error evidence; khoảng 7–10 ngày.** Thứ tự: data/sampling → weighting → capacity → feature experiments → decision rule. Mỗi vòng chỉ đổi một nhóm yếu tố trước khi thử kết hợp.

### 6.1. Sampling và hard examples từ train

1. Tái hiện baseline và ứng viên recall cũ tốt nhất trên cùng folds. Chép đúng config/rule từ run cũ, không chỉ tên model.
2. Giữ toàn bộ BF/Web có sẵn; lấy thêm Normal/Recon/Spoofing từ **processed train đầy đủ**, vì đây là nguồn gây nhiều nhầm lẫn. Pilot hiện chỉ có Normal 23.511, Recon 7.549, Spoofing 10.435, trong processed train lần lượt 126.395/40.576/56.096.
3. Một sampling arm mới: giữ toàn bộ 5 lớp Normal/BF/Recon/Spoofing/Web (227.323 hàng); sample DDoS 300k, DoS 100k, Mirai 100k → khoảng **727.323 hàng**. So sánh với arm cũ cùng cap DDoS/DoS để phân biệt lợi ích tăng hard-negative coverage và thay đổi Mirai. Các số là budget thử nghiệm, không phải phân bố để sửa validation/test.
4. Chỉ lấy hard examples qua inner-OOF trong fold-train. Tăng trọng số có giới hạn cho rare FN và Normal/Recon/Spoofing FP vào lớp hiếm; vẫn giữ negative ngẫu nhiên. Không lấy validation sai hoặc CF giả làm training examples.
5. Thử multiplier hard-example 1/2/4 trên arm có triển vọng. Đây là train-side reweighting, không phải threshold tuning. Nếu nhóm lỗi được xác định từ OOF cả outer train, phải có inner split để outer validation không đi vào việc chọn mẫu.

### 6.2. Trọng số

- Đối chứng none/sqrt và cấu hình best cũ. Thử class weights nhẹ có cap và multiplier riêng BF/Web 1/2/4; ghi weight thực mỗi lớp, chuẩn hóa mean sample weight để so regularization hợp lý.
- Tính tần suất trên fold-train sau sampling, không dùng support validation để fit weights. RF/DT dùng một nguồn weight rõ ràng; nếu vừa class_weight vừa sample_weight, phải ghi tích và chủ đích [R4, R5].
- XGBoost multiclass dùng `sample_weight` trong fit với `multi:softprob`, `num_class=8`; không dùng `scale_pos_weight` như giải pháp mặc định cho hai lớp hiếm trong 8 lớp [R6].
- Class_weight cân bằng đã thử; không coi bật `balanced` là bảo đảm recall/precision cùng tăng.

### 6.3. Tuning theo model

Các giá trị là không gian ứng viên, **không chạy Cartesian grid**. Sàng lọc 8 config/model, sau đó mở tối đa 12–16 config/model nếu có tín hiệu tốt. Giữ train đủ hai lớp hiếm và negative khó ngay trong vòng nhanh.

| Model | Baseline hiện tại | Hướng và không gian thử |
| --- | --- | --- |
| DT | depth=20, leaf=2 | Leaf support/purity/tie audit trước. `max_depth=[12,20,30,None]`, `min_samples_leaf=[1,2,4,8]`, `criterion=['gini','entropy']`, `ccp_alpha=[0,1e-6,1e-5]`; thử cả tăng độ phân giải và pruning, không chỉ làm cây sâu hơn [R5] |
| RF | 200 trees, depth=20, leaf=2, sqrt | Ưu tiên `max_features=['sqrt',0.5,1.0]`, `max_depth=[20,30,None]`, `min_samples_leaf=[1,2,4]`; `n_estimators=[200,400]`; weighting none/best custom/`balanced_subsample` là arm riêng. Tăng số cây chủ yếu kiểm tra độ ổn định, không giả định giải quyết thiếu feature hoặc ít mẫu [R4] |
| XGBoost | depth=6, child_weight=5, 300 trees, lr=0,1, hist/bin=256 | `max_depth=[4,6,8]`, `min_child_weight=[1,3,5]`, `learning_rate=[0.03,0.05,0.1]`, `reg_lambda=[1,5,10]`, `reg_alpha=[0,0.1,1]`, `subsample=[0.8,1.0]`, `colsample_bytree=[0.8,1.0]`, `max_bin=[256,512]`; trees tối đa 800 với early stopping trên inner-train holdout. Child weight nhỏ giúp thử chia vùng hiếm nhưng có thể tăng overfit [R6] |

Nếu dùng early stopping, không dùng outer validation để vừa chọn số cây vừa báo CV như đánh giá độc lập. Log best iteration và dùng số cây/rule đóng băng khi bàn giao.

### 6.4. Feature/preprocessing chỉ thay khi có kiểm chứng

- Đối chứng raw 44 cột hiện tại. Audit không có NaN/Inf; đổi median không phải ưu tiên. Không xóa outlier theo IQR vì có thể xóa tín hiệu attack.
- Arm redundancy: Rate vs Srate; Std/Radius và các nhóm tương quan phải kiểm tra ở **rare-class/context** trước, không dựa chỉ global correlation. Xóa theo nhóm/cặp từng arm, giữ schema version mới [R8].
- Arm feature engineering: `Std/(AVG+epsilon)`, `(Max-Min)/(AVG+epsilon)`, `Min/(AVG+epsilon)`, `Max/(AVG+epsilon)` để thử độ phân tán/tỷ lệ size. Epsilon/zero-denominator policy và finite checks phải rõ; chưa dùng tỷ lệ duration/IAT khi chưa xác minh đơn vị.
- Có thể thử log1p trên feature không âm lệch mạnh riêng cho XGBoost hist nếu cần kiểm tra hiệu ứng bin/numerical. Transform đơn điệu/scaling không tự tạo thông tin mới; không kỳ vọng scaling đơn thuần sửa lỗi cây.
- Không đưa original_label, target, row/source ID hoặc feature tạo từ nhãn validation vào model. Không xóa size/timing chỉ vì CF thay đổi chúng; đó có thể là tín hiệu hữu ích cần giữ.
- Nếu nghi float32 làm mất khả năng phân biệt, audit số vector mất phân giải/collision theo cặp lớp trước. Không kết luận từ DT hòa; audit hiện có báo 0 conflicting groups trong các representation được kiểm tra. Sklearn tree dùng float32 nội bộ nên đổi npy về float64 riêng lẻ chưa chắc giải quyết [R4, R5].
- Nếu bổ sung sample hiếm thật từ nguồn CICIoT2023 lớn hơn, phải có nguồn/hash, nhãn gốc, cùng cách trích feature và audit overlap với toàn bộ data cũ. Không nhập thêm test/validation cũ vào train để tăng support. Tạo data version mới và evaluation protocol riêng [R1].

### 6.5. Decision rule và hướng dự phòng

- Sau khi khóa estimator, thử multiplier BF/Web trên OOF/inner development; grid nhỏ quanh best cũ. Báo cả argmax và adjusted rule để thấy gain do estimator hay do dịch ranh giới.
- Vẽ đường precision–recall và bảng Pareto; model probability chưa được calibration thì không gọi nó là độ tin cậy thống kê. Nếu calibration có ích, fit bằng train OOF/inner split, rồi chọn rule trên phần khác hoặc nested procedure [R9].
- Nếu mô hình trực tiếp 8 lớp vẫn plateau, thử kiến trúc hai tầng bằng các thuật toán cây đã chọn: tầng 1 định tuyến flood/Mirai vs nhóm còn lại; tầng 2 phân biệt các lớp trong nhóm. Đầu ra cuối vẫn 8 lớp. Đây là nhánh cuối, có nguy cơ mất rare ở gate, phải báo recall qua gate, metric end-to-end, thời gian và XAI từng tầng. Không so nó như một model đơn có cùng chi phí.

## 7. Tiêu chí chọn và dừng — P4

Precision floor **0,30 mỗi lớp hiếm** và mục tiêu recall **0,85 mỗi lớp** là protocol cũ. Floor này khá thấp và không phải chuẩn IDS chung. Vòng mới báo Pareto tại precision floor 0,30 / 0,40 / 0,50; không hứa đạt recall 0,85 ở mọi floor.

Đề xuất chọn theo thứ tự: thỏa floor đã khóa → ưu tiên min(recall BF, recall Web) → macro-F1 và false alarms. Giữ một ứng viên cân bằng macro-F1, một ứng viên ưu tiên rare recall nếu có trade-off đáng kể. Accuracy và weighted-F1 là chỉ số phụ vì lớp lớn chi phối.

Mốc cải thiện thực dụng đề xuất: recall hai lớp tăng khoảng **5 điểm phần trăm** so với baseline cùng model/fold; macro-F1 không giảm quá 0,01, Normal false-alarm rate không tăng quá 1 điểm phần trăm. Đây là tiêu chí cần thống nhất khi triển khai, không phải kết quả đã đạt; nếu chỉ một lớp tăng phải trình bày trade-off và không tự gọi thành công cả hai.

Ứng viên cuối chạy seed 42/2026/3407 trên cùng protocol; báo mean/std và khoảng tin cậy theo nhóm trên prediction. Các seed không tạo thêm query độc lập. Support rare nhỏ nên tránh kết luận từ chênh 1–2 mẫu đúng.

Khóa feature set, preprocessing, weights, estimator, number of trees và rule trước đánh giá cuối. Đối chiếu validation/test cũ một lần cho báo cáo lịch sử sau khóa; nêu chúng đã được xem. Kết luận độc lập mạnh hơn chỉ khi có holdout/group mới thực sự phù hợp [R7].

**Dừng nhánh khi:** LIME chưa đạt nhưng cứ tăng số ca; gain chỉ đến từ FPs tăng quá mức; gain mất qua seed/fold; đổi processing không có lợi ích trong ablation; hoặc không còn dữ liệu/feature đủ để tách vùng chồng lấn. Khi đó báo giới hạn thông tin và dữ liệu thay vì chạy grid lớn vô hạn.

## 8. Ngân sách, checkpoint và bàn giao

| Mốc | Ngân sách ban đầu và checkpoint | Người phụ trách |
| --- | --- | --- |
| P0 | 1–2 ngày; đọc artifact, tạo protocol/folds | Dương + Hải |
| P1 | 2–4 ngày; 60 ca, max 3 seeds; đo toàn bộ elapsed/peak RAM/acceptance | Hải |
| P2 | 3–5 ngày; mở 240–400 ca; lưu mỗi 25 ca, resume theo model-hash + case + config + seed | Hải + Dương |
| P3 | 7–10 ngày; sàng lọc 8 config/model; chặn theo ngân sách 4 CPU-hours/phiên đề xuất, checkpoint từng fit, chỉ mở rộng nhánh có tín hiệu | Dương |
| P4 | 3–5 ngày; 3 seeds ứng viên cuối, XAI lại ca khóa, bàn giao | Cả nhóm |

Tổng khoảng 3–4 tuần, có thể song song phần artifact/error audit với sửa explainer; điều chỉnh theo timing pilot. Các mốc là dự kiến, không phải giới hạn chính thức của Kaggle hay bằng chứng hoàn thành. Resume không được trộn checkpoint khác protocol/model/data hash.

Timing run cũ có 36 LIME fits/model (DT 1,63s, RF 5,09s, XGB 6,11s), 5 CF searches/model (1,14/5,68/1,49s). Đây chỉ là tổng các phần được instrument trên 6 ca với bộ sinh cũ, không phải tổng runtime và không suy tuyến tính chắc chắn sang neighborhood có rejection/constraint mạnh hơn. Dự toán bằng median/p95 mới × số calls thực, cộng setup và serialization; dùng max proposal cap để kiểm soát chi phí.

Kết quả dự kiến nằm trong run mới dưới `output/` sau tải về: protocol/folds, error-bank, XAI quality, bảng ablation, per-class precision/recall/F1/support, macro-F1, 8×8 confusion matrices, train/inference/explanation time và hardware. Pipeline bàn giao gồm preprocessing + feature engineering nếu có + estimator + decision rule, schema/class order, config/hashes và golden samples/reload parity.

Kiên nạp đúng bundle mới và hiển thị XAI đúng model/sample. Chỉ hiển thị LIME đạt quality hoặc cảnh báo rõ trạng thái; hình CF ghi số thay đổi thực, metric khoảng cách đúng và tính giả định. Dương không bị chuyển trách nhiệm mô hình sang Hải: Hải đưa bằng chứng/giả thuyết, Dương xác nhận bằng ablation.

## 9. Checklist dự kiến — chưa tick thực nghiệm mới

- [ ] P0: khóa protocol, lịch sử evaluation và folds có audit.
- [ ] P1: giải thích được nguyên nhân rejection; kiểm chứng LIME/CF trên 60 ca.
- [ ] P2: mở bank theo subtype/cặp nhầm lẫn; báo quality, coverage và uncertainty.
- [ ] P3: chạy ablation sampling/weights/capacity/features, tránh lặp grid cũ.
- [ ] P4: xác nhận candidate qua folds/seeds, khóa model và giải thích lại.
- [ ] Bàn giao: pipeline/config/metrics/golden checks và demo tương thích.

## 10. References

- **[R1]** [CICIoT2023 official dataset](https://www.unb.ca/cic/datasets/iotdataset-2023.html): nhóm tấn công, subtype và thống kê feature; phân tích của đồ án vẫn dùng 8 lớp.
- **[R2]** Ribeiro, Singh, Guestrin (2016), [“Why Should I Trust You?”: Explaining the Predictions of Any Classifier](https://arxiv.org/abs/1602.04938): surrogate cục bộ, locality và fidelity. XAI chất lượng thấp không đủ để kết luận nguyên nhân model sai.
- **[R3]** [DiCE model-agnostic counterfactual methods](https://interpret.ml/DiCE/notebooks/DiCE_model_agnostic_CFs.html): tham khảo các phương pháp tìm CF; thuật toán hiện tại là prototype + grouped restore riêng, không phải DiCE.
- **[R4]** [RandomForestClassifier, sklearn 1.6](https://scikit-learn.org/1.6/modules/generated/sklearn.ensemble.RandomForestClassifier.html): capacity, class/sample weights, bootstrap và input conversion.
- **[R5]** [DecisionTreeClassifier, sklearn 1.6](https://scikit-learn.org/1.6/modules/generated/sklearn.tree.DecisionTreeClassifier.html): depth/leaf/pruning và input representation.
- **[R6]** [XGBoost parameters](https://xgboost.readthedocs.io/en/stable/parameter.html): multiclass objective, child weight, sampling và regularization. Triển khai phải kiểm tra API đúng version baseline 3.4.1.
- **[R7]** [sklearn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html), [cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html): chống leakage, preprocessing trong split và group evaluation.
- **[R8]** [sklearn permutation importance](https://scikit-learn.org/stable/modules/permutation_importance.html): ý nghĩa và giới hạn với correlated features; plan mở rộng theo nhóm phải mô tả thuật toán riêng.
- **[R9]** [sklearn probability calibration](https://scikit-learn.org/stable/modules/calibration.html): phân biệt prediction score và xác suất được hiệu chuẩn.
- **[R10]** [Toward Enhanced Attack Detection and Explanation in Intrusion Detection System-Based IoT Environment Data](https://doi.org/10.1109/ACCESS.2023.3336678), IEEE Access 2023; bản PDF trong `docs/`. Tham khảo hướng case analysis bằng LIME + counterfactual; không lấy metric hoặc số ca minh họa của paper làm bảo đảm hiệu năng trên split/model hiện tại.
