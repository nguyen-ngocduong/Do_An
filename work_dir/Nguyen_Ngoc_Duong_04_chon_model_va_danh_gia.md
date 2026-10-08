# Nguyễn Ngọc Dương — 04: Tinh chỉnh mô hình và đánh giá cuối

- **Phụ trách:** Nguyễn Ngọc Dương.
- **Phụ thuộc:** Dương 03; protocol và quy mô train chính.
- **Trạng thái ngày 08/10/2026:** chưa có bằng chứng hoàn thành.
- **Phạm vi:** phân loại có giám sát 8 lớp; dữ liệu và huấn luyện chạy trên Kaggle.

## Công việc

- [ ] Huấn luyện đối sánh cả 3 thuật toán trên cùng train chính; ghi rõ pilot và thí nghiệm chính.
- [ ] Tìm kiếm cấu hình có giới hạn, ghi ngân sách từng model; chọn bằng validation macro-F1 và recall/F1 lớp hiếm/Normal.
- [ ] Đánh giá 3 seed nếu tài nguyên cho phép; công bố số lần thực chạy, trung bình/độ lệch và các giới hạn.
- [ ] Đối chiếu feature đầy đủ/rút gọn nếu đủ thời gian; selection chỉ fit trên train và quyết định trên validation (tùy chọn).
- [ ] Chốt model demo/XAI và giải thích nếu khác model có điểm cao nhất; xác nhận tương thích với Hải và Kiên.
- [ ] Đóng băng pipeline/model/config trước khi đánh giá các cấu hình đã chọn trên cùng test.
- [ ] Xuất precision/recall/F1/support 8 lớp, macro-F1, confusion matrix 8×8 và dự đoán test có sample ID/class order; phân tích các cặp lớp nhầm.
- [ ] Đo thời gian huấn luyện/suy luận trên cùng phần cứng, warm-up và batch công bố; tách load, preprocessing và prediction; báo median/p95 khi đủ lần đo.
- [ ] Giao dự đoán đúng/sai và model cuối cho Hải phân tích; giao pipeline/config/bảng hiệu năng cho Kiên tổng hợp tích hợp.
- [ ] Ghi giới hạn, run bị hủy/lý do nếu có; không dùng test để tinh chỉnh lại mô hình.

## Đầu ra và nghiệm thu

Model cuối và cấu hình đóng băng; bảng metric/confusion matrix và thời gian huấn luyện/suy luận, log và dự đoán truy vết được.

## Bằng chứng và giới hạn

Pilot hiện chỉ xác nhận chuẩn bị dữ liệu. Chưa có artifact huấn luyện/test để tick các mục này.

## Bước tiếp theo

Dương 05; hỗ trợ Hải phân tích XAI và Kiên kiểm thử bản tích hợp cuối.
