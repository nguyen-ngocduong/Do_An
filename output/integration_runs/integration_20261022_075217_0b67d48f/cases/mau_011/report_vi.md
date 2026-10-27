## mau_011 — dòng CSV 10

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +2.395018 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83487480 | +0.29570100 | +29.570100 |
| Protocol Type | 5.9400001 | +0.02213594 | +2.213594 |
| Magnitue | 10.392912 | +0.01487454 | +1.487454 |
| Number | 9.5 | +0.00958054 | +0.958054 |
| Min | 54 | +0.00867281 | +0.867281 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu được mô hình dự đoán là lớp DDoS với độ tự tin áp đảo, trong khi lớp đứng thứ hai là DoS có khoảng cách chênh lệch cực lớn. Yếu tố IAT đóng góp hỗ trợ mạnh mẽ nhất, và không có đặc trưng nào trong top năm mang lại tác động phản đối.

**So sánh hai lớp:** Cờ khoảng cách nhỏ tắt cho thấy hai đầu ra có khoảng cách lớn, tuy nhiên mức chênh lệch cao này không được xem là bảo đảm dự đoán đúng hay thay thế nhãn thật.

**Tổng hợp SHAP:** Đặc trưng IAT là yếu tố hỗ trợ mạnh nhất trong nhóm top năm làm tăng giá trị đầu ra, trong khi không ghi nhận yếu tố nào có tác động phản đối dương hoặc âm trong nhóm này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần đẩy mạnh đầu ra của lớp dự đoán so với nền tham chiếu.
- **Protocol Type**: Tác động này cùng chiều nhưng nhỏ hơn yếu tố dẫn đầu, đóng vai trò hỗ trợ bổ sung cho mô hình.
- **Magnitue**: Đặc trưng này mang lại mức đóng góp dương ở mức vừa phải, tiếp tục củng cố thêm xu hướng dự đoán.
- **Number**: Sự hiện diện của yếu tố này tạo ra một lực đẩy nhỏ cùng chiều với đầu ra được giải thích.
- **Min**: Đóng góp dương nhỏ nhất trong nhóm top năm, thể hiện tác động bổ trợ thấp hơn các đặc trưng phía trên.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu có địa chỉ và thời gian. Mục đích: Đối chiếu với các biểu hiện thực tế từ nguồn lưu lượng để xem xét bối cảnh gói tin.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ, không tự đặt ngưỡng. Mục đích: Đánh giá mức độ đáp ứng của hệ thống dựa trên thông tin tài nguyên ghi nhận được.

### Giới hạn do Gemini nêu

- Giải thích này phản ánh đầu ra của mô hình tại thời điểm phân tích, không chứng minh quan hệ nhân quả hay cuộc tấn công thực tế.
- Các giá trị SHAP chỉ thể hiện sự thay đổi so với nền tham chiếu của riêng mô hình và chưa được hiệu chỉnh xác suất tuyệt đối.
- Phạm vi phân tích chỉ giới hạn trong top năm đặc trưng và phần dư còn lại, chưa phản ánh toàn bộ các yếu tố có thể có trong hệ thống.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
