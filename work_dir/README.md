# Kế hoạch đồ án tốt nghiệp — phân công chính thức

Cập nhật **08/10/2026** theo phân công người dùng xác nhận. Đề tài: nghiên cứu, xây dựng hệ thống phát hiện tấn công mạng IoT dựa trên kỹ thuật XAI.

## Phạm vi và trách nhiệm

Chỉ thực hiện **phân loại có giám sát 8 lớp**: Normal, BruteForce, DDoS, DoS, Mirai, Recon, Spoofing, Web-Based (mã 0–7). Nhãn gốc chỉ dùng ánh xạ và truy vết.

| Thành viên | Trách nhiệm chính | Sản phẩm chịu trách nhiệm |
| --- | --- | --- |
| **Nguyễn Ngọc Dương** | Dữ liệu **và mô hình phát hiện**: khảo sát CICIoT2023; pipeline tiền xử lý; tập huấn luyện/kiểm thử; triển khai và đối sánh mô hình | Pipeline dữ liệu tái lập; model/config; precision/recall/F1/macro-F1, confusion matrix; thời gian huấn luyện/suy luận |
| **Hà Minh Hải** | Mô-đun **XAI và phân tích**: SHAP/LIME; giải thích toàn cục/cục bộ; phân tích ca đúng/sai và nhóm tấn công | Mã XAI, biểu đồ/đầu ra giải thích; thời gian giải thích; phân tích feature và ca điển hình |
| **Tạ Trung Kiên** | **Tích hợp hệ thống và đánh giá**: kiến trúc; kết nối detection/XAI; giao diện; kiểm thử và tổng hợp đánh giá | Hệ thống end-to-end, giao diện/đầu ra minh họa, kịch bản kiểm thử, đánh giá tích hợp và hướng dẫn chạy |

Dương chịu trách nhiệm thực nghiệm mô hình; Hải chịu trách nhiệm thực nghiệm XAI; Kiên tổng hợp và đánh giá hệ thống tích hợp. Cả nhóm cùng viết tổng quan, kết luận và rà báo cáo.

## Cách thực hiện

Tên file là `Ho_Ten_01_...md` đến `Ho_Ten_05_...md`; số nhỏ ưu tiên trước **trong công việc của từng người**. Ba người làm song song theo phụ thuộc bàn giao, không phải chờ cả nhóm hoàn thành cùng một số. Báo cáo viết dần trong quá trình thực hiện.

Dấu `[x]` áp dụng cho đầu việc có kết quả xác nhận, không tự nghiệm thu cả task. `[ ]` là chưa hoàn thành hoặc chưa có bằng chứng. Tạo kế hoạch/module mẫu không đồng nghĩa đã chạy thực nghiệm. Những phần khảo sát đã xác nhận được giữ; phần tài liệu và benchmark chưa có đầu ra được tách rõ.

## Danh sách theo ưu tiên

| Ưu tiên | Nguyễn Ngọc Dương | Hà Minh Hải | Tạ Trung Kiên |
| --- | --- | --- | --- |
| 01 | [Khảo sát dữ liệu và xác định bài toán](Nguyen_Ngoc_Duong_01_khao_sat_du_lieu.md) | [Thiết kế mô-đun XAI](Ha_Minh_Hai_01_thiet_ke_xai.md) | [Kiến trúc hệ thống và hợp đồng tích hợp](Ta_Trung_Kien_01_kien_truc_he_thong.md) |
| 02 | [Pipeline tiền xử lý và tổ chức tập thực nghiệm](Nguyen_Ngoc_Duong_02_pipeline_va_pilot.md) | [Triển khai SHAP và LIME](Ha_Minh_Hai_02_trien_khai_shap_lime.md) | [Giao diện và tích hợp pipeline phát hiện](Ta_Trung_Kien_02_giao_dien_pipeline_phat_hien.md) |
| 03 | [Huấn luyện baseline và chốt quy mô train](Nguyen_Ngoc_Duong_03_baseline_va_quy_mo_train.md) | [Giải thích toàn cục, cục bộ và ca điển hình](Ha_Minh_Hai_03_phan_tich_toan_cuc_cuc_bo.md) | [Tích hợp XAI và luồng end-to-end](Ta_Trung_Kien_03_tich_hop_xai_end_to_end.md) |
| 04 | [Tinh chỉnh mô hình và đánh giá cuối](Nguyen_Ngoc_Duong_04_chon_model_va_danh_gia.md) | [Kiểm chứng và đo thời gian giải thích](Ha_Minh_Hai_04_kiem_chung_danh_gia_xai.md) | [Kiểm thử tích hợp và tổng hợp đánh giá](Ta_Trung_Kien_04_kiem_thu_danh_gia_tich_hop.md) |
| 05 | [Báo cáo và bàn giao dữ liệu, mô hình](Nguyen_Ngoc_Duong_05_bao_cao_ban_giao.md) | [Báo cáo và bàn giao mô-đun XAI](Ha_Minh_Hai_05_bao_cao_ban_giao.md) | [Đóng gói hệ thống, hướng dẫn và demo](Ta_Trung_Kien_05_dong_goi_huong_dan_demo.md) |

## Tiến độ hiện tại

- [x] Dương: khảo sát dữ liệu, EDA và lưu hình.
- [x] Dương: preprocessing 8 lớp trên Kaggle, schema/mapping và hai transformer.
- [x] Dương: tổ chức processed train/validation/test và pilot 100k/500k/1M có index/seed, giữ toàn bộ hai lớp hiếm.
- [x] Dương: có hướng dẫn pilot, bảng phân bố và kiểm tra tính toàn vẹn các artifact tải về.
- [ ] Dương: baseline, benchmark và quyết định quy mô train chính; tinh chỉnh, test và model/config cuối.
- [ ] Hải: triển khai SHAP/LIME, phân tích và benchmark giải thích.
- [ ] Kiên: kiến trúc, giao diện, tích hợp, kiểm thử và tổng hợp đánh giá.
- [ ] Cả nhóm: tái lập độc lập, báo cáo hoàn chỉnh và nghiệm thu bàn giao.

**Việc tiếp theo của Dương là task 03: huấn luyện baseline trên Kaggle.** Bắt đầu LR/DT/RF ở 100k, tiếp tục 500k/1M theo tài nguyên, so macro-F1/recall lớp hiếm và thời gian/RAM trên cùng validation để chốt budget. Công việc này thuộc Dương, không chuyển sang Hải hay Kiên.

Hải có thể bắt đầu thiết kế XAI; Kiên có thể bắt đầu kiến trúc và interface. Model cây baseline đầu tiên sẽ được Dương bàn giao cho cả hai.

## Bằng chứng tiến độ

| Kết quả | Artifact | Ghi nhận |
| --- | --- | --- |
| Khảo sát | [Notebook EDA](../notebook/ciciot2023-do-an.ipynb), [plots](../output/plots/) | Đã có khảo sát và 7 ảnh; báo cáo cần hoàn thiện |
| Processing `20261007_164739_35f682b9` | [Trạng thái](../output/processed_data/20261007_164739_35f682b9/run_status.json), [config](../output/processed_data/20261007_164739_35f682b9/preprocessing_config.json), [support](../output/processed_data/20261007_164739_35f682b9/class_support_final.csv) | Train 5.357.406, validation 862.150, test 830.443 dòng × 44 feature; đủ 8 lớp |
| Pilot `pilot_20261008_022915_ea9a88b0` | [Manifest](../output/pilot_data/pilot_20261008_022915_ea9a88b0/pilot_manifest.json), [phân bố](../output/pilot_data/pilot_20261008_022915_ea9a88b0/class_distribution_all_budgets.csv), [bàn giao](../output/pilot_data/pilot_20261008_022915_ea9a88b0/README_HANDOFF.md) | 100k/500k/1M lồng nhau, seed 42; mỗi tập giữ 1.488 BruteForce, 2.768 Web-Based |
| Kiểm tra tải về | Checksum trong manifest pilot và source_reference_manifest | Đã đối chiếu 30 file, header/kích thước 6 ma trận và hash config/nhãn nguồn; không chạy lại notebook local |
| Huấn luyện | [Bảng mẫu](../output/pilot_data/pilot_20261008_022915_ea9a88b0/benchmark_template.csv) | 9 thí nghiệm còn `not_run`, chưa có điểm mô hình |

Manifest Kaggle ghi đạt các kiểm tra index lồng nhau, đủ lớp, nhãn/metadata và feature khớp nguồn. Đối chiếu artifact tải về không phải một lần tái lập độc lập trên môi trường sạch.

## Quy tắc thực nghiệm và bàn giao

- Chạy dữ liệu và huấn luyện trên **Kaggle** theo yêu cầu hiện tại; local dùng đọc kết quả, chỉnh notebook/tài liệu, không tự chạy lại processing hay train.
- LR dùng scaled, DT/RF dùng raw đã xử lý; không transform thêm lần nữa. Preprocessing các pilot dùng chung bộ fit trên toàn train nguồn: đây là so sánh quy mô huấn luyện classifier với preprocessing cố định.
- Dùng cùng split, feature/class order và protocol để so sánh mô hình. Validation chọn budget/config/model; test chỉ đánh giá sau khi đóng băng.
- Macro-F1 là chỉ số chính; báo precision/recall/F1/support đủ 8 lớp và confusion matrix 8×8. Công bố cách xử lý chỉ số không xác định, class_weight, seed, cấu hình và môi trường.
- Giữ rõ thay đổi phân bố do lấy mẫu và purge_eval: validation/test giảm 26,74%/29,44%; không khẳng định độc lập theo phiên/thiết bị nếu chưa có metadata chứng minh.
- Tách thời gian training/inference (Dương), explanation (Hải), end-to-end và hiển thị (Kiên); ghi cùng điều kiện đo khi so sánh.
- XAI gắn đúng model/run/sample/class/output space. Không diễn giải đóng góp như xác suất hoặc quan hệ nhân quả nếu không có cơ sở.
- Mỗi người lưu mã, config, version, run ID và kết quả thực. Bàn giao chỉ nghiệm thu khi người nhận nạp/chạy được; thay đổi model/dataset cần cập nhật ID và kiểm tra tương thích.

| Bàn giao | Người tạo → nhận | Nội dung |
| --- | --- | --- |
| Dữ liệu/schema | Dương → Hải, Kiên | Mapping, feature order/đơn vị, sample ID, CSV mẫu, preprocessing/config và hướng dẫn |
| Model/prediction | Dương → Hải, Kiên | Model và transformer tương ứng, classes_, run/config, dự đoán có sample ID, mẫu chuẩn |
| XAI | Hải → Kiên; Dương đối chiếu feature | Module/API, cấu hình, biểu đồ/dữ liệu giải thích, output space, thời gian |
| Đánh giá | Dương + Hải → Kiên | Metrics mô hình, confusion matrix, thời gian từng thành phần, phân tích và giới hạn |
| Bản tích hợp | Kiên → cả nhóm | Hệ thống, kịch bản/log kiểm thử, hướng dẫn chạy và demo |

## Mốc đề xuất

| Thời gian | Dương | Hải | Kiên |
| --- | --- | --- | --- |
| 08–11/10 | Chốt protocol baseline, chuẩn bị runner | Thiết kế XAI | Kiến trúc/contract |
| 12–25/10 | Baseline, so budget, bàn giao model cây | SHAP/LIME thử nghiệm | Giao diện và pipeline dự đoán |
| 26/10–01/11 | Tinh chỉnh, chốt model | Phân tích toàn cục/cục bộ | Tích hợp XAI |
| 02–15/11 | Test và benchmark cuối | Kiểm chứng, ca cuối/thời gian | Kiểm thử và tổng hợp đánh giá |
| 16–22/11 | Hoàn thiện báo cáo dữ liệu/model | Hoàn thiện báo cáo XAI | Bản đầy đủ/hướng dẫn/demo |
| 23–29/11 | Rà số liệu, tái lập và sửa | Rà diễn giải, tái lập và sửa | Nghiệm thu/đóng gói |
| 30/11–05/12 | Cả nhóm rà bản nộp, sao lưu và diễn tập | Cùng nhóm | Cùng nhóm |

Hạn nộp quyển ghi trong đề cương: **06/12/2026**; lịch bảo vệ cần xác nhận riêng. Mốc là kế hoạch, không phải bằng chứng hoàn thành.

## Lưu lịch sử

Kế hoạch theo vai trò TV1/TV2/TV3 cũ đã được lưu trong [`_archive/ke_hoach_truoc_phan_cong_20261008_094844.zip`](_archive/ke_hoach_truoc_phan_cong_20261008_094844.zip) để truy vết. Các file mang tên thật ở thư mục này là kế hoạch hiện hành, thay thế phân công cũ. Nguồn yêu cầu: đề cương trong thư mục dự án và phân công ba người được người dùng xác nhận ngày 08/10/2026.
