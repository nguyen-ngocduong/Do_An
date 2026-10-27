## mau_019 — dòng CSV 18

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **Mirai**, xác suất **99.9931%**.
- Lớp đứng thứ hai: **DDoS**, xác suất **0.0040%**.
- Chênh lệch hai lớp: **99.9891 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 9.376009%.
- Tổng SHAP: +90.617053 điểm phần trăm; ngoài top 5: +11.292613 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **Protocol Type**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| Protocol Type | 47 | +0.25783366 | +25.783366 |
| IAT | 83650864 | +0.25061510 | +25.061510 |
| Magnitue | 34 | +0.18706486 | +18.706486 |
| Tot size | 578 | +0.06384029 | +6.384029 |
| Min | 578 | +0.03389049 | +3.389049 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu thuộc lớp Mirai với sự đóng góp tích cực từ toàn bộ các yếu tố trong top năm. Lớp đứng thứ hai là DDoS nhưng có khoảng cách rất lớn về đầu ra so với lớp dẫn đầu.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt, cho thấy sự chênh lệch lớn giữa lớp Mirai và lớp DDoS. Tuy nhiên, chênh lệch lớn không bảo đảm dự đoán này hoàn toàn chính xác mà vẫn cần đối chiếu thêm.

**Tổng hợp SHAP:** Yếu tố Protocol Type mang lại tác động hỗ trợ mạnh nhất trong top năm, trong khi không có yếu tố nào đóng vai trò phản đối trong nhóm này. Các tác động còn lại cùng phần ngoài top năm kết hợp tạo nên đầu ra cuối.

- **Protocol Type**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, làm tăng đáng kể giá trị đầu ra của lớp được giải thích so với nền tham chiếu.
- **IAT**: Đặc trưng này đóng vai trò hỗ trợ bổ sung với mức độ tác động lớn đứng thứ hai trong nhóm.
- **Magnitue**: Sự hiện diện của đặc trưng này tiếp tục củng cố đầu ra dự đoán theo chiều hướng tăng.
- **Tot size**: Đặc trưng này mang lại mức đóng góp dương ở mức độ nhỏ hơn các yếu tố dẫn đầu.
- **Min**: Đây là yếu tố có tác động dương nhỏ nhất trong top năm đặc trưng đang xem xét.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký kết nối thiết bị**: Đối chiếu đích kết nối và hoạt động lặp với hành vi được phép của thiết bị IoT Mục đích: Nhằm xác định xem thiết bị có đang thực hiện các kết nối bất thường hay không nếu hệ thống lưu trữ log này.
- **Nhật ký tiến trình thiết bị**: Nếu truy cập được thiết bị, tìm tiến trình hoặc cảnh báo liên quan; chưa kết luận đã nhiễm mã độc Mục đích: Nhằm kiểm tra các tiến trình đang chạy bên trong thiết bị khi có quyền truy cập nhật ký.

### Giới hạn do Gemini nêu

- Giải thích này phản ánh đầu ra của mô hình máy học và không chứng minh cuộc tấn công thực tế hay quan hệ nhân quả.
- Các giá trị SHAP chỉ thể hiện sự thay đổi so với nền tham chiếu trong phạm vi top năm đặc trưng được cung cấp.
- Xác suất của mô hình chưa được xác minh là đã hiệu chỉnh và không thể coi là độ chắc chắn tuyệt đối.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
