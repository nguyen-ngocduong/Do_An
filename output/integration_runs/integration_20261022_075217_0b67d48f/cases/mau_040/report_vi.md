## mau_040 — dòng CSV 39

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +3.516746 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83128632 | +0.26946107 | +26.946107 |
| Protocol Type | 1 | +0.03109434 | +3.109434 |
| Magnitue | 9.1651516 | +0.02635457 | +2.635457 |
| Tot size | 42 | +0.00654827 | +0.654827 |
| Min | 42 | +0.00628931 | +0.628931 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu dữ liệu thuộc lớp DDoS với mức độ tin cậy rất cao nhờ sự hỗ trợ từ các đặc trưng nổi bật trong top năm. Lớp đứng thứ hai là DoS nhưng có khoảng cách rất lớn so với lớp dẫn đầu, cho thấy mô hình phân định rõ ràng giữa hai lớp này.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt, cho thấy sự chênh lệch lớn giữa lớp đứng đầu và lớp đứng thứ hai. Tuy nhiên, việc chênh lệch lớn không được coi là bảo đảm dự đoán chính xác vì đây chỉ là giá trị đầu ra của mô hình.

**Tổng hợp SHAP:** Đặc trưng IAT đóng vai trò hỗ trợ mạnh nhất trong nhóm top năm làm tăng giá trị đầu ra của lớp được dự đoán, trong khi không ghi nhận tác động phản đối nào trong nhóm này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần đáng kể vào việc đẩy giá trị đầu ra của lớp dự đoán.
- **Protocol Type**: Tác động này cùng chiều nhưng có độ lớn thấp hơn đáng kể so với yếu tố dẫn đầu trong nhóm.
- **Magnitue**: Đặc trưng này mang lại một mức đóng góp dương bổ sung giúp củng cố thêm kết quả phân loại.
- **Tot size**: Đóng góp này tiếp tục đẩy giá trị đầu ra tăng nhẹ theo cùng hướng với các đặc trưng trước đó.
- **Min**: Đây là thành phần có tác động dương nhỏ nhất trong năm đặc trưng đang được xem xét.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu có địa chỉ và thời gian. Mục đích: Đối chiếu sự xuất hiện đồng thời của các yêu cầu từ nhiều nguồn để làm rõ bối cảnh lưu lượng mạng.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ, không tự đặt ngưỡng. Mục đích: Xem xét ảnh hưởng của lưu lượng đến khả năng đáp ứng của hệ thống phục vụ.

### Giới hạn do Gemini nêu

- Kết quả SHAP chỉ phản ánh cách mô hình đưa ra quyết định dựa trên giá trị tham chiếu, không chứng minh mối quan hệ nhân quả hay cuộc tấn công thực tế.
- Xác suất dự đoán của mô hình chưa được hiệu chỉnh chính thức và không bảo đảm tuyệt đối về độ chính xác.
- Phạm vi giải thích chỉ giới hạn ở nhóm đặc trưng đang xét và chưa bao gồm toàn bộ sự thay đổi của toàn bộ tập dữ liệu.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
