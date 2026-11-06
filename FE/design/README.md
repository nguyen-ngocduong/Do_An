# Tham chiếu thiết kế NIDR

FE ứng dụng Next.js/React nằm trong [src/](../src/), với giao diện Adminator được người dùng chọn ngày 03/11/2026. Token giữ trong [globals.css](../src/app/globals.css); các trang đọc REST API FastAPI. Cấu trúc tác vụ Predict → SHAP → Gemini tiếp tục theo Miro và nghiệp vụ NIDR.

- [Adminator — tham chiếu giao diện hiện tại](https://preview.colorlib.com/theme/adminator/index.html).
- [Ảnh tham chiếu Adminator](reference/adminator-reference.png): chụp trực tiếp bằng Chrome ở 1440 × 1000 ngày 03/11/2026. Dữ liệu kinh doanh trong ảnh thuộc demo Adminator; không dùng trong ứng dụng NIDR.
- Bố cục áp dụng: sidebar/header trắng, canvas xám xanh, điểm nhấn xanh dương và card trắng bo mềm. Thực hiện trong source Next.js hiện có; ảnh tham chiếu chỉ nằm trong tài liệu.

Ngày 04/11/2026: người dùng cung cấp [ảnh dashboard tổng quan](reference/dashboard-user-overview.png) và [ảnh phần dưới](reference/dashboard-user-lower.png), yêu cầu tinh chỉnh dashboard và thêm footer Dark Navy. Hai tệp `.png.json` cùng tên ghi nguồn và SHA256; đây là ảnh người dùng, không phải kết quả ứng dụng. Dashboard giữ dữ liệu API thật, không lấy số 49/48/1 hoặc thông điệp “Normal an toàn” trong ảnh làm kết quả. Footer lấy tên đề tài, ngành/hệ đào tạo và thông tin Nhóm số 07 từ `Đề cương đồ án tốt nghiệp.docx`; dùng logo NIDR sẵn có.

Điều chỉnh tiếp ngày 04/11/2026: người dùng bác bỏ footer dạng thẻ đề cương và yêu cầu **footer toàn website** theo cách tổ chức thông tin của [PTIT](https://ptit.edu.vn/). Đã xem trang/HTML và [chụp footer PTIT](reference/ptit-footer.png) bằng Chrome 1440×1000; nguồn ở sidecar cùng tên. Thiết kế hiện tại là dải navy phẳng, bốn cột nhận diện/đơn vị đào tạo/nhóm/liên kết, dùng chung ở shell và public pages; footer dạng thẻ, badge và avatar cũ không còn áp dụng. Chỉ tham khảo bố cục PTIT, không trình bày địa chỉ/email hỗ trợ của Học viện thành thông tin vận hành NIDR.

Các nguồn Miro sau ghi lại cơ sở tổ chức tác vụ trước đợt đổi diện mạo:

- [Bảng dự đoán trên Miro](https://miro.com/app/board/uXjVEU3YmTc=/?moveToWidget=3458764688660488795).
- [Giải thích một mẫu](https://miro.com/app/board/uXjVEU3YmTc=/?moveToWidget=3458764688660488796).
- [Cảnh báo](https://miro.com/app/board/uXjVEU3YmTc=/?moveToWidget=3458764688669949786).
- [Ảnh Miro tham chiếu: bảng dự đoán](reference/predictions-miro.png), [chi tiết mẫu](reference/explanation-miro.png).
- [DESIGN.md](DESIGN.md): token, bố cục, component, trạng thái.
- [SURFACE.md](SURFACE.md): tác vụ và tiêu chí màn hình.
- [DEBUG_DATA_CONTRACT.md](DEBUG_DATA_CONTRACT.md): nguồn dữ liệu cho từng bước.

Hai ảnh tham chiếu chứa dữ liệu prototype đã lưu, gồm mẫu Web-Based dòng 14 của tập 16 mẫu nguồn; tổng quan 720/1.000 là minh họa. FE ứng dụng chỉ hiển thị số liệu đọc từ BE, không ghép cố định mẫu này vào run được upload.

Ngày 29/10/2026: người dùng dừng khảo sát Stitch và yêu cầu triển khai theo Miro. Bộ brief/script Stitch, 19 HTML prototype, CSS ghi đè và ảnh/metadata kiểm tra cũ đã được dọn. Bản thiết kế trên Miro được giữ nguyên. Không có kết quả nào được gắn nhãn Stitch sinh.

Hướng dẫn chạy và kiểm thử tại [FE/README.md](../README.md). Bằng chứng ứng dụng thực tế tại [FE/VERIFICATION.md](../VERIFICATION.md).
