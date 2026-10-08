# Tạ Trung Kiên — 02: Giao diện và tích hợp pipeline phát hiện

- **Phụ trách:** Tạ Trung Kiên.
- **Phụ thuộc:** Kiên 01; model baseline từ Dương để chạy dự đoán thật.
- **Trạng thái ngày 08/10/2026:** chưa có bằng chứng hoàn thành.
- **Phạm vi:** phân loại có giám sát 8 lớp; dữ liệu và huấn luyện chạy trên Kaggle.

## Công việc

- [ ] Dựng giao diện nhập CSV và xem kết quả; dữ liệu giả khi dựng mẫu phải được ghi rõ.
- [ ] Nạp model/preprocessing/schema từ cấu hình; xử lý đúng feature order, không fit lại trên CSV người dùng.
- [ ] Kiểm tra CSV thiếu/thừa cột, sai dtype, NaN/Inf, nhãn đi kèm và file quá giới hạn; áp dụng chính sách đã thống nhất.
- [ ] Hiển thị dự đoán thuộc 8 lớp và xác suất đúng class order; tách nhãn thật nếu có khỏi ma trận feature.
- [ ] Đối chiếu các mẫu chuẩn với dự đoán notebook của Dương, trước/sau lưu nạp.
- [ ] Hiển thị model/run ID, giới hạn cỡ dữ liệu, thông báo lỗi và chức năng xuất dự đoán.

## Đầu ra và nghiệm thu

Giao diện/module dự đoán dùng pipeline thật và kết quả khớp mẫu chuẩn.

## Bằng chứng và giới hạn

Chưa có app hoặc kết quả chạy tích hợp. Dữ liệu pilot hoàn tất không đồng nghĩa giao diện hoàn tất.

## Bước tiếp theo

Kiên 03 khi Hải bàn giao module XAI chạy được.
