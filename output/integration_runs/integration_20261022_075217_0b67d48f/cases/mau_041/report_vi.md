## mau_041 — dòng CSV 40

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +3.404568 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83089968 | +0.27383188 | +27.383188 |
| Protocol Type | 6 | +0.02199357 | +2.199357 |
| Magnitue | 10.392304 | +0.02098387 | +2.098387 |
| Tot size | 54 | +0.01489447 | +1.489447 |
| Min | 54 | +0.00916554 | +0.916554 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu này thuộc lớp DDoS với mức xác suất rất cao, trong khi lớp đứng thứ hai là DoS có khoảng cách chênh lệch cực lớn. Đặc trưng IAT đóng vai trò hỗ trợ mạnh mẽ nhất, đẩy giá trị đầu ra tăng lên đáng kể so với nền tham chiếu.

**So sánh hai lớp:** Lớp đứng thứ hai là DoS có xác suất vô cùng nhỏ so với lớp DDoS. Cờ khoảng cách nhỏ đang tắt, cho thấy sự chênh lệch lớn giữa hai đầu ra nhưng điều này không được coi là bảo đảm tuyệt đối về nhãn thật.

**Tổng hợp SHAP:** Trong nhóm năm đặc trưng hàng đầu, tất cả đều tác động theo chiều hướng tăng và không có yếu tố nào mang giá trị âm trong phạm vi này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, đóng góp mức tăng lớn nhất vào đầu ra của lớp.
- **Protocol Type**: Tác động này cùng chiều nhưng nhỏ hơn yếu tố dẫn đầu, đóng vai trò hỗ trợ bổ sung cho mô hình.
- **Magnitue**: Đặc trưng này tiếp tục thúc đẩy kết quả dự đoán tăng lên với một mức đóng góp dương đáng chú ý.
- **Tot size**: Sự hiện diện của đặc trưng này tạo thêm một khoảng tăng nhỏ giúp củng cố đầu ra của lớp.
- **Min**: Đây là yếu tố có tác động nhỏ hơn trong nhóm năm đặc trưng, góp phần đẩy giá trị đầu ra dịch chuyển tăng.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu có địa chỉ và thời gian. Mục đích: Đối chiếu xem lưu lượng thực tế có dấu hiệu phân tán từ nhiều nguồn hướng về mục tiêu hay không.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ, không tự đặt ngưỡng. Mục đích: Đánh giá mức độ ảnh hưởng của tải mạng đối với hệ thống dịch vụ dựa trên dữ liệu ghi nhận.

### Giới hạn do Gemini nêu

- Kết quả SHAP chỉ giải thích đầu ra của mô hình phân loại và không chứng minh được quan hệ nhân quả hay cuộc tấn công thực tế.
- Giá trị xác suất của mô hình chưa được kiểm chứng là đã hiệu chỉnh hoàn toàn.
- Phạm vi phân tích chỉ giới hạn trong top năm đặc trưng được cung cấp và chưa bao gồm toàn bộ mọi thành phần ngoài nhóm.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
