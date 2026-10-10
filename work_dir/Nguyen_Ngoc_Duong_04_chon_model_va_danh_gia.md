# Nguyễn Ngọc Dương — 04: Cải thiện recall và đánh giá mô hình

- **Phụ trách:** Nguyễn Ngọc Dương.
- **Phụ thuộc:** Dương 03; processing, pilot và model baseline.
- **Trạng thái ngày 08/10/2026:** đã tạo notebook vòng cải thiện, chưa chạy thực nghiệm vòng này.
- **Phạm vi:** 8 lớp, DT/RF/XGBoost; xử lý và huấn luyện chỉ trên Kaggle.

## Công việc

- [x] Có đối sánh baseline trên train chính 1M, bảng metric/confusion matrix, model/config và thời gian chạy.
- [x] Chuẩn bị [notebook Kaggle cải thiện recall](../notebook/ciciot2023-do-an-recall-improvement.ipynb), có checkpoint, ngân sách và pipeline suy luận kèm quy tắc quyết định.
- [ ] A: tìm hệ số quyết định BruteForce/Web-Based trên xác suất của 9 model baseline 1M; giữ precision từng lớp ≥30%.
- [ ] B: thử cap DDoS/DoS moderate/strong × DT/RF/XGBoost × none/sqrt/balanced; giữ nguyên toàn bộ rare train và validation mask.
- [ ] C: tuning có giới hạn, DT 6 cấu hình, RF/XGBoost mỗi loại 12 cấu hình.
- [ ] D nếu chưa đạt mục tiêu: SHAP trên train, thử top20/top30 cộng feature bảo vệ lớp hiếm; loại projection gây giao nhau train/validation hoặc tune/confirmation.
- [ ] Đo ổn định với seed 42/2026/3407; giữ hệ số seed42, báo số seed thực chạy và độ lệch.
- [ ] Khóa tối đa 2 ứng viên và primary từ tune trước khi mở xác nhận; không đổi primary theo confirmation/test.
- [ ] Báo precision/recall/F1/support 8 lớp, macro-F1, confusion matrix, CI recall, lỗi theo nhãn gốc và thời gian fit/suy luận của vòng cải thiện.
- [ ] Kiểm tra bundle pipeline/model/config và mẫu chuẩn; bàn giao cho Hải/Kiên và nhận xác nhận chạy được.
- [ ] Khảo sát dữ liệu bổ sung chưa dùng trong tối đa 3 ngày; chỉ gọi test mới khi có provenance và kiểm tra giao nhau với toàn bộ dữ liệu cũ. Nếu chưa có, ghi rõ giới hạn.

## Tiêu chí lựa chọn và ngân sách

Precision ≥30% ở **từng** lớp BruteForce và Web-Based. Trong các cấu hình đủ điều kiện, ưu tiên recall thấp hơn của hai lớp, rồi recall trung bình, macro-F1. Recall ≥85% mỗi lớp là mục tiêu, không phải kết quả bảo đảm. Báo tác động lên Normal và các lớp khác.

Tập validation baseline được chia tune/confirmation 50/50 theo nhóm fingerprint raw float32. Cả validation và test baseline đã từng được xem; confirmation chỉ được giữ lại cho vòng tìm kiếm mới, không chứng minh test hoàn toàn độc lập. Không purge khác nhau theo model để tăng điểm.

Ngân sách tìm kiếm cộng dồn 36 giờ công việc phiên CPU qua checkpoint. Một fit đang chạy có thể vượt phần còn lại; final reporting được ghi riêng và được phép hoàn tất. Khi đã freeze, resume không mở thêm tìm kiếm.

## Đầu vào và cách chạy

Add Input trên Kaggle gồm toàn bộ ba run:

- Processing `20261007_164739_35f682b9`.
- Pilot `pilot_20261008_022915_ea9a88b0`.
- Baseline `models_20261008_073827_d29a37c3`, cần cả model và probabilities.

Chọn CPU, dùng cùng phiên bản thư viện với baseline, Restart → Run All. Nếu tự định vị thấy nhiều nguồn, điền ba đường dẫn ở cell cấu hình. Để tiếp tục phiên bị ngắt, Add Input toàn bộ output cũ và đặt `RESUME_FROM` đến thư mục run.

## Đầu ra và nghiệm thu

`/kaggle/working/recall_experiments/<run_id>/`: protocol/environment, sampling/partition indices, trial model/config/metric, ablation, frozen candidates, confirmation/test cũ, inference module và bundle bàn giao. Chỉ tick các thí nghiệm khi có artifact Kaggle thực tế; notebook mới chỉ được kiểm tra cấu trúc và cú pháp ở local.

## Bước tiếp theo

Dương 05; Hải phân tích XAI trên estimator và giải thích riêng ảnh hưởng của quy tắc quyết định; Kiên dùng pipeline.predict để giữ đúng quyết định cuối khi tích hợp.
