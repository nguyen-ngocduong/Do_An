# Tạ Trung Kiên — 01: Kiến trúc hệ thống và hợp đồng tích hợp

- **Phụ trách:** Tạ Trung Kiên.
- **Phụ thuộc:** đề cương; schema Dương và thiết kế XAI của Hải.
- **Trạng thái ngày 08/10/2026:** chưa có bằng chứng hoàn thành.
- **Phạm vi:** phân loại có giám sát 8 lớp; dữ liệu và huấn luyện chạy trên Kaggle.

## Công việc

- [ ] Thiết kế kiến trúc CSV → kiểm tra schema → pipeline phát hiện → dự đoán 8 lớp → chọn mẫu/lớp → XAI → hiển thị/xuất kết quả.
- [ ] Chốt giao diện hoặc module trình bày kết quả; xác định yêu cầu, giới hạn dữ liệu và môi trường chạy demo.
- [ ] Thống nhất contract với Dương/Hải: model/run ID, feature/class order, sample ID, xác suất, output XAI và lỗi.
- [ ] Thiết kế cấu trúc artifact/config và cơ chế kiểm tra phiên bản tương thích khi nạp model/XAI.
- [ ] Lập tiêu chí nghiệm thu end-to-end, các kịch bản kiểm thử và phân công đo thời gian từng thành phần.
- [ ] Viết yêu cầu/kiến trúc mục 3.1 và sơ đồ hệ thống.

## Đầu ra và nghiệm thu

Sơ đồ kiến trúc, đặc tả interface và kịch bản kiểm thử ban đầu.

## Bằng chứng và giới hạn

Schema dữ liệu đã có từ Dương; chưa có bằng chứng kiến trúc hoặc interface tích hợp đã hoàn tất.

## Bước tiếp theo

Kiên 02; phối hợp Dương 03 và Hải 01 để chốt định dạng bàn giao.
