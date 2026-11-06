# Task FE cho Antigravity

## Mục tiêu

Màn hình/component cần sửa và hành vi người dùng mong muốn.

## Phạm vi ghi

- Liệt kê chính xác file/thư mục FE; truyền cùng phạm vi bằng --allow-write.
- File bắt buộc thay đổi: truyền bằng --expect.
- Không sửa BE, hợp đồng API, model, runtime, credentials hoặc cấu hình agent.

## Bằng chứng và thiết kế

- Source/component hiện tại và ảnh tham chiếu có thể đọc.
- Quy tắc áp dụng từ FE/design/DESIGN.md, FE/design/SURFACE.md.
- Contract thiết kế do Codex chuẩn bị; giữ thương hiệu và các phần ngoài scope.

## Hợp đồng API

- Hàm typed trong FE/src/lib/api và kiểu dữ liệu thực tế.
- Trường được dùng, trạng thái lỗi, không bịa số liệu hoặc tính năng BE chưa có.

## Hành vi và trạng thái

- Luồng chính, chờ/trống/lỗi/thành công, focus/bàn phím.
- Desktop/tablet/mobile và nền tối.
- Thao tác đọc không tự tạo yêu cầu SHAP/Gemini hoặc ghi dữ liệu.

## Tiêu chí hoàn thành

- Mô tả cụ thể cách Codex kiểm chứng kết quả.
- Giữ code đơn giản, tiếng Việt, đúng kiến trúc hiện tại.
- AGY chỉ dùng công cụ file; Codex chạy lint/typecheck/test/build và browser.

## Kết quả bàn giao

Danh sách file đã sửa, hành vi mới, hạn chế/việc còn lại và kiểm tra thực sự đã chạy.
Không báo đã chạy test/build nếu chưa chạy.
