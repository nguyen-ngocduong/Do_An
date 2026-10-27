## mau_017 — dòng CSV 16

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +3.273012 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83089232 | +0.27088547 | +27.088547 |
| Protocol Type | 6 | +0.02846786 | +2.846786 |
| Magnitue | 10.450931 | +0.02104908 | +2.104908 |
| Tot size | 54.240002 | +0.01093869 | +1.093869 |
| Number | 9.5 | +0.01084379 | +1.084379 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu thuộc lớp DDoS với mức độ tin cậy áp đảo, trong đó yếu tố IAT dẫn đầu nhóm hỗ trợ mạnh mẽ. Lớp đứng thứ hai là DoS nhưng có khoảng cách xác suất rất lớn so với lớp dẫn đầu.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt, cho thấy sự chênh lệch lớn giữa lớp DDoS và lớp DoS; tuy nhiên, điều này không được xem là bảo đảm dự đoán chính xác vì chưa có nhãn thật.

**Tổng hợp SHAP:** Trong top năm đặc trưng, IAT đóng vai trò hỗ trợ mạnh nhất đẩy giá trị đầu ra của lớp dự đoán tăng lên so với nền tham chiếu, trong khi không ghi nhận yếu tố nào mang tác động phản đối trong nhóm này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần đáng kể vào kết quả phân loại của mô hình.
- **Protocol Type**: Tác động này cùng chiều nhưng nhỏ hơn yếu tố dẫn đầu, đóng vai trò hỗ trợ bổ sung cho dự đoán.
- **Magnitue**: Sự đóng góp theo chiều dương tiếp tục củng cố kết quả đầu ra với mức độ thấp hơn các đặc trưng trước đó.
- **Tot size**: Đặc trưng này thể hiện một lực đẩy dương nhỏ nhằm duy trì xu hướng nghiêng về lớp dự đoán.
- **Number**: Đây là yếu tố có tác động dương nhỏ nhất trong nhóm top năm được phân tích.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu có địa chỉ và thời gian. Mục đích: Đối chiếu xem có dấu hiệu lưu lượng bất thường từ các nguồn hay không.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ, không tự đặt ngưỡng. Mục đích: Kiểm tra tác động thực tế của lưu lượng lên hệ thống.

### Giới hạn do Gemini nêu

- Các giá trị SHAP chỉ giải thích đầu ra của mô hình đối với mẫu hiện tại và không chứng minh quan hệ nhân quả hay cuộc tấn công thực tế.
- Tổng giá trị SHAP trong top năm chưa phải là toàn bộ mức thay đổi, phần còn lại đến từ các đặc trưng ngoài nhóm.
- Xác suất dự đoán của mô hình chưa được xác minh là đã hiệu chỉnh hoàn toàn.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
