# Tạ Trung Kiên — 04: Kiểm thử tích hợp và tổng hợp đánh giá

- **Phụ trách:** Tạ Trung Kiên.
- **Phụ thuộc:** Kiên 03; model/XAI cuối từ Dương/Hải.
- **Trạng thái ngày 08/10/2026:** chưa có bằng chứng hoàn thành.
- **Phạm vi:** phân loại có giám sát 8 lớp; dữ liệu và huấn luyện chạy trên Kaggle.

## Công việc

- [ ] Lập và chạy bộ ca CSV hợp lệ/lỗi, schema/dtype/NaN/Inf, cột nhãn, file lớn, artifact thiếu hoặc sai phiên bản.
- [ ] Đối chiếu script/notebook/app trên mẫu chuẩn: dự đoán, class order, sample ID và giải thích khớp cấu hình/dung sai.
- [ ] Kiểm thử thay model/dữ liệu/lớp/cấu hình XAI để phát hiện cache cũ, lệch mẫu hoặc lệch nhãn.
- [ ] Chạy từ hướng dẫn trên môi trường sạch, kiểm tra demo offline nếu thuộc thiết kế; lưu lỗi và cách sửa.
- [ ] Đo thời gian end-to-end và tài nguyên của hệ thống; tách load/preprocessing/predict/explain/UI, không gộp nhầm thời gian model và XAI.
- [ ] Tổng hợp bảng metric/huấn luyện/suy luận do Dương cung cấp và bảng thời gian/phân tích XAI do Hải cung cấp; giữ đúng run và điều kiện đo.
- [ ] Lập báo cáo nghiệm thu tích hợp, giới hạn hệ thống và kết quả kiểm thử; phối hợp hoàn thiện 4.1/4.4.

## Đầu ra và nghiệm thu

Kịch bản/log kiểm thử, kết quả đánh giá tích hợp, bảng tổng hợp truy vết tới artifact của từng người.

## Bằng chứng và giới hạn

Chưa có kết quả tích hợp để tick; Kiên tổng hợp đánh giá, Dương sở hữu thực nghiệm mô hình và Hải sở hữu thực nghiệm XAI.

## Bước tiếp theo

Kiên 05 sau khi các lỗi nghiệm thu đã được xử lý.
