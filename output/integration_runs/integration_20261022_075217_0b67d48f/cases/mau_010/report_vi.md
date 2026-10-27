## mau_010 — dòng CSV 9

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +3.555466 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83124056 | +0.28903767 | +28.903767 |
| Magnitue | 9.1651516 | +0.02434608 | +2.434608 |
| Protocol Type | 1 | +0.01057661 | +1.057661 |
| ICMP | 1 | +0.00882845 | +0.882845 |
| Min | 42 | +0.00657154 | +0.657154 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Hệ thống dự đoán mẫu này thuộc lớp DDoS với xác suất rất cao, trong đó yếu tố IAT đóng vai trò hỗ trợ mạnh mẽ nhất còn không có yếu tố nào phản đối trong top năm đặc trưng. Khoảng cách với lớp đứng thứ hai DoS rất lớn nên sự cạnh tranh giữa hai lớp này không đáng kể.

**So sánh hai lớp:** Lớp đứng thứ hai là DoS nhưng có khoảng cách rất lớn so với lớp dự đoán và cờ khoảng cách nhỏ đang tắt. Điều này không có nghĩa là chênh lệch lớn bảo đảm tuyệt đối dự đoán là đúng, đồng thời đây chỉ là kết quả phân tích đầu ra model chứ không phải nhãn thật.

**Tổng hợp SHAP:** Trong top năm đặc trưng được xét, IAT là yếu tố hỗ trợ mạnh nhất đẩy giá trị đầu ra tăng cao, trong khi không ghi nhận bất kỳ yếu tố phản đối nào có tác động âm. Phần thay đổi còn lại được đóng góp bởi các đặc trưng ngoài top năm và giá trị nền tham chiếu.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần đẩy mạnh đầu ra của lớp được dự đoán.
- **Magnitue**: Tác động này cùng chiều hướng tăng nhưng có mức đóng góp nhỏ hơn yếu tố dẫn đầu.
- **Protocol Type**: Đặc trưng này cung cấp thêm một lực hỗ trợ bổ sung theo chiều hướng làm tăng điểm số dự đoán.
- **ICMP**: Sự hiện diện của đặc trưng này tiếp tục duy trì xu hướng đồng thuận với lớp được chọn.
- **Min**: Đây là thành phần có tác động nhỏ hơn trong nhóm, đóng góp một phần khiêm tốn vào đầu ra tổng thể.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu có địa chỉ và thời gian Mục đích: Đối chiếu sự biến động lưu lượng thực tế theo thời gian với mô hình giải thích.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ, không tự đặt ngưỡng Mục đích: Kiểm tra xem hệ thống có chịu áp lực tương ứng hay không trước khi đưa ra nhận định.

### Giới hạn do Gemini nêu

- Giá trị SHAP chỉ phản ánh mức độ đóng góp của đặc trưng đối với đầu ra của mô hình tại thời điểm này, không phải là bằng chứng nhân quả về một cuộc tấn công thực tế.
- Xác suất của mô hình chưa được kiểm chứng hay hiệu chỉnh độ tin cậy thực tế.
- Phạm vi giải thích chỉ giới hạn trong top năm đặc trưng và giá trị nền tham chiếu, chưa bao quát toàn bộ không gian dữ liệu.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
