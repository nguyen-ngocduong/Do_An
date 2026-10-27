## mau_042 — dòng CSV 41

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +3.392034 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83149632 | +0.27610052 | +27.610052 |
| Protocol Type | 1 | +0.02689099 | +2.689099 |
| Magnitue | 9.1651516 | +0.02457124 | +2.457124 |
| Max | 42 | +0.00729816 | +0.729816 |
| Min | 42 | +0.00613375 | +0.613375 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu dữ liệu được mô hình dự đoán thuộc lớp DDoS với xác suất áp đảo so với các lớp còn lại. Yếu tố IAT đóng vai trò hỗ trợ mạnh nhất, trong khi không ghi nhận yếu tố phản đối nào trong nhóm năm đặc trưng hàng đầu. Khoảng cách với lớp đứng thứ hai DoS rất lớn, thể hiện sự phân tách rõ rệt trong kết quả phân loại của mô hình.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt, cho thấy không có sự cạnh tranh sát sao giữa lớp đứng đầu và lớp đứng thứ hai là DoS. Tuy nhiên, sự chênh lệch lớn này không phải là bảo đảm tuyệt đối rằng dự đoán là chính xác.

**Tổng hợp SHAP:** Đặc trưng IAT là yếu tố hỗ trợ mạnh nhất đẩy đầu ra về phía lớp DDoS, và không có yếu tố nào trong top năm mang giá trị âm để tạo ra tác động phản đối.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, đóng góp lớn vào giá trị đầu ra của lớp được dự đoán.
- **Protocol Type**: Tác động này cùng chiều nhưng có mức độ đóng góp nhỏ hơn đáng kể so với yếu tố dẫn đầu.
- **Magnitue**: Đặc trưng này tiếp tục bổ trợ cho xu hướng tăng điểm đầu ra với một mức đóng góp dương ở nhóm giữa.
- **Max**: Đóng góp này duy trì chiều hướng hỗ trợ nhưng có giá trị tác động nhỏ hơn các đặc trưng trước đó.
- **Min**: Đây là thành phần có tác động dương nhỏ nhất trong nhóm năm đặc trưng được phân tích.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu có địa chỉ và thời gian. Mục đích: Đối chiếu xem lưu lượng có biểu hiện tập trung từ nhiều nguồn hay không nếu hệ thống có ghi nhận log này.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ, không tự đặt ngưỡng. Mục đích: Kiểm tra trạng thái hệ thống để tham khảo thêm bối cảnh vận hành nếu hạ tầng cung cấp thông tin này.

### Giới hạn do Gemini nêu

- Giá trị SHAP chỉ phản ánh mức độ đóng góp của đặc trưng vào đầu ra của mô hình đối với mẫu này, không chứng minh quan hệ nhân quả hay mô tả một cuộc tấn công thực tế.
- Xác suất dự đoán chưa qua kiểm định hiệu chỉnh và không đại diện cho độ chính xác tuyệt đối.
- Phạm vi giải thích chỉ giới hạn trong top năm đặc trưng được chọn và phần còn lại ngoài nhóm, không đại diện cho toàn bộ cấu trúc dữ liệu.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
