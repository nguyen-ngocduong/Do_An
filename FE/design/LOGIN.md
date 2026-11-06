# Đăng nhập NIDR

Mode: Operate. Người vận hành dùng tài khoản quản trị BE hiện có để vào dashboard; không đăng ký công khai hay thêm vai trò mới.

## Direction contract

THESIS: một form tập trung vào đăng nhập, lỗi và khôi phục phiên; giữ nhận diện dashboard đã chọn.

OWN-WORLD: nền radial tím/xanh nhẹ trên nền trung tính, Inter, tím cho nhận diện/focus và CTA đăng nhập; card bóng mềm, khoảng cách theo FE/design/DESIGN.md. Có nền tối.

STORY: nhận ra NIDR, nhập tài khoản và mật khẩu, vào đúng trang cần xem; có thể hiện mật khẩu, sửa lỗi và đăng xuất.

FIRST VIEWPORT: thương hiệu trong card rộng tối đa 460 px, công tắc nền ở góc trang; tiêu đề Đăng nhập, hai trường có nhãn/placeholder, Ghi nhớ phiên và Quên mật khẩu?, nút tím toàn hàng. Nền radial tím/xanh nhẹ, footer gọn. Mobile giữ thứ tự và cuộn khi cần.

FORM: mở rộng giao diện hiện có, không thay visual world; không dùng ảnh minh họa hoặc số liệu giả.

FINISH: kiểm tra form, sai/đúng mật khẩu, refresh/deep link, đăng xuất, phiên hết hạn; xem ảnh desktop/mobile/sáng/tối và ghi bằng chứng.

## Cơ chế đã chốt

Người dùng chọn đăng nhập/đăng xuất hoạt động đầy đủ. BE cấp cookie HttpOnly SameSite=Strict, Secure khi HTTPS; phiên tối đa tám giờ, giữ trong process BE và hết hiệu lực khi restart. Password chỉ ở state tạm lúc nhập, không lưu storage. HTTP Basic tiếp tục phục vụ Swagger/CLI. Trang đăng nhập và bundle tĩnh công khai; dữ liệu/API cần xác thực. Không tự huấn luyện hoặc gọi Gemini từ luồng đăng nhập.

API 1.4.0 nhận remember=false mặc định: cookie theo phiên trình duyệt. Khi chọn Ghi nhớ phiên, đặt Max-Age tám giờ; thời hạn tại BE không tăng. Browser session restore có thể khôi phục session cookie theo thiết lập riêng. Phản hồi trước CTA có chỗ dành sẵn cho lỗi, spinner khi gửi; hỗ trợ là hướng dẫn liên hệ quản trị viên.

## Ghi nhận triển khai — 01/11/2026

Form dùng tài khoản BE hiện có qua `POST /api/auth/login`; trình duyệt gửi cookie cùng origin cho các yêu cầu tiếp theo. Đăng nhập thành công xóa mật khẩu khỏi state và thay URL bằng trang đích; mở `/login` khi còn phiên cũng chuyển tới trang đích. Phiên hết hạn đưa về đăng nhập, giữ đường dẫn và query hiện tại. Đăng xuất gọi `POST /api/auth/logout` để thu hồi phiên, xóa cookie rồi về `/login`. Kích thước, nền tối/mobile và trạng thái hiện/ẩn mật khẩu, đang gửi, lỗi theo [quy tắc giao diện](DESIGN.md#đăng-nhập--01112026).

Với trang riêng tư chưa xác thực, Nginx chuyển nguyên URI qua header nội bộ sang Next.js; Next mã hóa toàn bộ đích vào một tham số `next`, giữ các tham số sau dấu `&` và ký tự đã escape. Sau đăng nhập chỉ quay về `/dashboard`, `/runs`, `/runs/...` hoặc `/alerts` cùng query; không có đích hoặc đích không hợp lệ về `/dashboard`.
