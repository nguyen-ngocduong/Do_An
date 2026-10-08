# Nguyễn Ngọc Dương — 02: Pipeline tiền xử lý và tổ chức tập thực nghiệm

- **Phụ trách:** Nguyễn Ngọc Dương.
- **Phụ thuộc:** Dương 01.
- **Trạng thái ngày 08/10/2026:** đã hoàn thành preprocessing và tạo pilot; còn tái lập độc lập/tài liệu cuối.
- **Phạm vi:** phân loại có giám sát 8 lớp; dữ liệu và huấn luyện chạy trên Kaggle.

## Công việc

- [x] Xây notebook Kaggle có cấu hình; xác thực schema/dtype, mapping 8 lớp và loại mọi nhãn/metadata khỏi X.
- [x] Xử lý NaN/Inf, trùng, nhãn mâu thuẫn và giao nhau; lưu audit và chính sách purge_eval train → validation → test.
- [x] Fit điền thiếu/chọn cột/log/scale trên train; validation/test chỉ transform. Lưu hai transformer tree/scaled.
- [x] Lưu dữ liệu nguồn sau xử lý: train 5.357.406, validation 862.150, test 830.443 dòng, mỗi ma trận 44 feature; đủ 8 lớp.
- [x] Lưu schema, class mapping, feature order, metadata, cấu hình và run ID; phân tích cột hằng/tương quan trên train.
- [x] Tạo pilot 100k/500k/1M lồng nhau, seed 42, không lấy lặp ID; giữ toàn bộ 1.488 BruteForce và 2.768 Web-Based.
- [x] Xuất X raw/scaled, y, index và metadata cho từng budget; công bố phân bố trước/sau và giữ validation/test nguồn.
- [x] Lưu hướng dẫn tái tạo/sử dụng pilot; đối chiếu checksum 30 file tải về, header/kích thước 6 ma trận và hash config/nhãn nguồn.
- [ ] Chạy tái lập độc lập trên Kaggle từ môi trường sạch; lưu log đối chiếu schema/support/checksum, giải thích sai khác nếu có.
- [ ] Chuẩn bị CSV feature hợp lệ và các mẫu sai schema cho Kiên; xác nhận Hải/Kiên đọc được artifact cần dùng.
- [ ] Viết mục 2.2/3.2 và phần dữ liệu của 4.1, kèm nguồn sinh các bảng/hình.

## Đầu ra và nghiệm thu

Pipeline tái lập được, bộ processed và ba pilot có manifest, hướng dẫn và CSV mẫu. Tạo pilot đã xong; lựa chọn budget train chính thuộc task 03.

## Bằng chứng và giới hạn

[Processing complete](../output/processed_data/20261007_164739_35f682b9/run_status.json), [cấu hình](../output/processed_data/20261007_164739_35f682b9/preprocessing_config.json), [pilot complete](../output/pilot_data/pilot_20261008_022915_ea9a88b0/run_status.json), [manifest](../output/pilot_data/pilot_20261008_022915_ea9a88b0/pilot_manifest.json), [hướng dẫn](../output/pilot_data/pilot_20261008_022915_ea9a88b0/README_HANDOFF.md). Pilot hoàn tất trong 238,782 giây. Kiểm tra index lồng nhau/X-y-metadata ghi đạt trong run Kaggle; kiểm tra tải về không phải tái chạy pipeline. Validation/test giảm 26,74%/29,44% sau lọc; chưa chứng minh độc lập theo phiên/thiết bị. Preprocessing pilot dùng chung bộ đã fit trên toàn train nguồn.

## Bước tiếp theo

Ưu tiên ngay: Dương 03 — huấn luyện baseline và đo tài nguyên để chốt quy mô.
