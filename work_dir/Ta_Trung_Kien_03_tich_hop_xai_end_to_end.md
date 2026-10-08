# Tạ Trung Kiên — 03: Tích hợp XAI và luồng end-to-end

- **Phụ trách:** Tạ Trung Kiên.
- **Phụ thuộc:** Kiên 02 và module XAI Hải 02.
- **Trạng thái ngày 08/10/2026:** chưa có bằng chứng hoàn thành.
- **Phạm vi:** phân loại có giám sát 8 lớp; dữ liệu và huấn luyện chạy trên Kaggle.

## Công việc

- [ ] Kết nối module XAI của Hải với model/pipeline của Dương bằng contract; kiểm tra run/feature/class order.
- [ ] Cho chọn sample ID và lớp giải thích, hiển thị toàn cục/cục bộ và feature values có đơn vị/không gian rõ ràng.
- [ ] Giữ sample ID xuyên suốt lọc/hiển thị; hiển thị đúng true/predicted label và output space XAI.
- [ ] Giới hạn số mẫu giải thích, xử lý chờ/lỗi và cache theo model/dataset/sample/class/config để tránh trả nhầm.
- [ ] Xuất dự đoán và giải thích kèm metadata; hiển thị bảng đánh giá từ artifact thực nghiệm.
- [ ] Chạy luồng thật CSV → dự đoán → giải thích → xuất kết quả; so sánh với module riêng cùng Dương/Hải.

## Đầu ra và nghiệm thu

Hệ thống thử nghiệm chạy end-to-end bằng model và XAI thật; kết quả truy vết được.

## Bằng chứng và giới hạn

Chưa có bằng chứng luồng tích hợp hoạt động.

## Bước tiếp theo

Kiên 04 — kiểm thử tích hợp và tổng hợp đánh giá.
