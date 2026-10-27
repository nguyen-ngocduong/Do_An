## mau_032 — dòng CSV 31

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **Mirai**, xác suất **99.9931%**.
- Lớp đứng thứ hai: **DDoS**, xác suất **0.0040%**.
- Chênh lệch hai lớp: **99.9891 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 9.376009%.
- Tổng SHAP: +90.617053 điểm phần trăm; ngoài top 5: +10.711901 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **Min**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| Min | 554 | +0.28804681 | +28.804681 |
| Magnitue | 33.286633 | +0.20763133 | +20.763133 |
| Tot size | 554 | +0.13327400 | +13.327400 |
| IAT | 83789160 | +0.12965397 | +12.965397 |
| flow_duration | 1.6335063 | +0.04044540 | +4.044540 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu dữ liệu thuộc lớp Mirai với mức độ tự tin rất cao, vượt xa các lớp khác trong hệ thống. Các đặc trưng trong top năm đều đóng vai trò đẩy mạnh đầu ra của lớp được chọn. Sự cạnh tranh giữa lớp Mirai đứng đầu và lớp DDoS đứng thứ hai có khoảng cách rất lớn.

**So sánh hai lớp:** Lớp đứng thứ hai là DDoS có xác suất rất nhỏ so với lớp dẫn đầu. Cờ khoảng cách nhỏ đang tắt và chênh lệch điểm phần trăm giữa hai lớp rất lớn, tuy nhiên điều này không coi là bảo đảm tuyệt đối dự đoán là đúng.

**Tổng hợp SHAP:** Trong top năm đặc trưng xét đến, Min là yếu tố hỗ trợ mạnh nhất đẩy đầu ra tăng lên, trong khi không có đặc trưng nào nằm trong nhóm này tạo tác động phản đối. Các đóng góp dương khác cùng phần ngoài top năm tạo nên kết quả cuối cùng.

- **Min**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần đáng kể làm tăng giá trị đầu ra của lớp được dự đoán.
- **Magnitue**: Tác động này cùng chiều nhưng có phần đóng góp nhỏ hơn yếu tố dẫn đầu trong nhóm.
- **Tot size**: Đặc trưng này mang lại một mức hỗ trợ bổ sung đáng chú ý để củng cố thêm cho kết quả phân loại.
- **IAT**: Sự hiện diện của yếu tố này tiếp tục đóng góp một lực đẩy dương với mức độ vừa phải vào tổng giá trị SHAP.
- **flow_duration**: Đây là tác động có chiều hướng đồng thuận nhưng mang lại mức thay đổi nhỏ nhất trong nhóm năm đặc trưng.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký kết nối thiết bị**: Đối chiếu đích kết nối và hoạt động lặp với hành vi được phép của thiết bị IoT. Mục đích: Xem xét xem hệ thống có ghi nhận các kết nối mạng bất thường hay không nếu có dữ liệu nhật ký này.
- **Nhật ký tiến trình thiết bị**: Nếu truy cập được thiết bị, tìm tiến trình hoặc cảnh báo liên quan; chưa kết luận đã nhiễm mã độc. Mục đích: Kiểm tra tình trạng hoạt động thực tế bên trong thiết bị nếu hệ thống lưu trữ các bản ghi này.

### Giới hạn do Gemini nêu

- Kết quả này chỉ là giải thích đầu ra của mô hình máy học, không phải là bằng chứng chứng minh một cuộc tấn công thực tế hay quan hệ nhân quả.
- Giá trị SHAP phản ánh mức độ đóng góp so với nền tham chiếu của mô hình chứ không suy ra thay đổi giá trị đặc trưng sẽ sửa đổi được dự đoán.
- Xác suất dự đoán hiện tại chưa được xác minh là đã hiệu chỉnh và tổng top năm chưa bao trùm toàn bộ các yếu tố của mô hình.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
