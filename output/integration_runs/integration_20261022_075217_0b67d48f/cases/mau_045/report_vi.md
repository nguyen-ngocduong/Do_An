## mau_045 — dòng CSV 44

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +3.000884 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83124696 | +0.29193434 | +29.193434 |
| Magnitue | 9.1651516 | +0.02246774 | +2.246774 |
| Protocol Type | 1 | +0.01263095 | +1.263095 |
| Tot size | 42 | +0.00946906 | +0.946906 |
| Min | 42 | +0.00840407 | +0.840407 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu này thuộc lớp DDoS với xác suất rất cao, trong đó đặc trưng IAT đóng vai trò hỗ trợ mạnh mẽ nhất còn các đặc trưng còn lại trong top năm đều góp phần củng cố xu hướng tăng. Lớp đứng thứ hai là DoS nhưng có khoảng cách xác suất rất lớn so với lớp dẫn đầu, cho thấy mô hình phân loại cực kỳ tập trung vào quyết định này.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt vì chênh lệch giữa hai lớp rất lớn. Việc này không đảm bảo dự đoán hoàn toàn chính xác mà chỉ phản ánh đầu ra của lớp thứ hai thấp hơn nhiều so với lớp dẫn đầu.

**Tổng hợp SHAP:** Đặc trưng IAT là yếu tố hỗ trợ mạnh nhất trong nhóm top năm, trong khi không có đặc trưng nào trong nhóm mang lại tác động phản đối. Phần thay đổi còn lại đến từ các yếu tố bên ngoài top năm và giá trị nền tham chiếu.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần nâng cao đầu ra của lớp được dự đoán so với nền tham chiếu.
- **Magnitue**: Tác động này cùng chiều tăng nhưng có mức độ đóng góp nhỏ hơn đáng kể so với yếu tố dẫn đầu.
- **Protocol Type**: Đặc trưng này cung cấp thêm một lực đẩy dương bổ sung vào xu hướng chung của mô hình.
- **Tot size**: Sự hiện diện của giá trị này tạo ra một đóng góp hỗ trợ nhỏ hơn trong nhóm.
- **Min**: Đây là tác động dương cuối cùng trong top năm với mức ảnh hưởng hạn chế nhất.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu hệ thống ghi nhận địa chỉ và thời gian. Mục đích: Đối chiếu mô hình với dữ liệu thực tế phát sinh trên mạng.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ của hệ thống. Mục đích: Kiểm tra xem các biến động có phản ánh đúng trạng thái tải thực tế hay không.

### Giới hạn do Gemini nêu

- Kết quả SHAP chỉ giải thích đầu ra của mô hình phân loại đối với mẫu hiện tại, không chứng minh cuộc tấn công thực tế hoặc quan hệ nhân quả.
- Xác suất dự đoán từ mô hình chưa được xác minh là đã hiệu chỉnh và không thể xem là độ tin cậy tuyệt đối.
- Giá trị SHAP trong top năm chỉ phản ánh một phần sự thay đổi so với nền tham chiếu, không đại diện cho toàn bộ các đặc trưng của hệ thống.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
