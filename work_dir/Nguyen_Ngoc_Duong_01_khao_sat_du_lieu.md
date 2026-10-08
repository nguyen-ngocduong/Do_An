# Nguyễn Ngọc Dương — 01: Khảo sát dữ liệu và xác định bài toán

- **Phụ trách:** Nguyễn Ngọc Dương.
- **Phụ thuộc:** đề cương và bản CICIoT2023 đang sử dụng.
- **Trạng thái ngày 08/10/2026:** đã khảo sát; còn nội dung báo cáo.
- **Phạm vi:** phân loại có giám sát 8 lớp; dữ liệu và huấn luyện chạy trên Kaggle.

## Công việc

- [x] Khảo sát bản CICIoT2023 trên Kaggle, kiểm kê split, số dòng, cột và nhãn; phân biệt bản đang dùng với toàn bộ dữ liệu gốc.
- [x] Thực hiện EDA và lưu 7 ảnh khảo sát trong `output/plots/`.
- [x] Chốt 8 lớp và mã: Normal=0, BruteForce=1, DDoS=2, DoS=3, Mirai=4, Recon=5, Spoofing=6, Web-Based=7; nhãn gốc chỉ dùng ánh xạ/truy vết.
- [x] Khảo sát NaN/Inf, trùng, giao nhau giữa split, nhãn mâu thuẫn, cột hằng và tương quan; ghi phương án xử lý.
- [x] Rà các lỗi EDA về mục tiêu bài toán, nhãn dẫn xuất trong feature và cấu hình lấy mẫu; áp dụng các sửa đổi trong pipeline preprocessing.
- [ ] Hoàn thiện mô tả nguồn, phiên bản, cách sinh đặc trưng, ý nghĩa/đơn vị feature và giới hạn bản Kaggle; đối chiếu tài liệu đã đọc.
- [ ] Viết nháp Chương I và mục 2.1; chú thích hình EDA theo đúng dữ liệu và cỡ mẫu.

## Đầu ra và nghiệm thu

Notebook khảo sát, hình/bảng EDA 8 lớp, mô tả nguồn và mapping, bản viết phần dữ liệu. Chỉ nghiệm thu phần báo cáo khi có bản thảo.

## Bằng chứng và giới hạn

[Notebook EDA](../notebook/ciciot2023-do-an.ipynb), [ảnh khảo sát](../output/plots/), [support sau xử lý](../output/processed_data/20261007_164739_35f682b9/class_support_final.csv). Các tick đọc tài liệu/đo tài nguyên tổng quát ở kế hoạch cũ không thay cho tài liệu tổng quan hoặc benchmark mô hình; các đầu ra này vẫn cần hoàn thiện.

## Bước tiếp theo

Tiếp tục task 02; phần báo cáo viết song song, không cần đợi huấn luyện.
