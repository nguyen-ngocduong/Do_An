## mau_021 — dòng CSV 20

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +4.111914 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83128768 | +0.26616482 | +26.616482 |
| Protocol Type | 1 | +0.02080413 | +2.080413 |
| Magnitue | 9.1651516 | +0.01868376 | +1.868376 |
| Header_Length | 0 | +0.01544382 | +1.544382 |
| Tot size | 42 | +0.01269934 | +1.269934 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu dữ liệu thuộc lớp DDoS với sự hỗ trợ mạnh mẽ từ đặc trưng IAT trong top năm đặc trưng quan trọng. Khoảng cách giữa lớp đứng đầu và lớp đứng thứ hai là rất lớn và cờ khoảng cách nhỏ đang tắt, cho thấy sự chênh lệch rõ rệt nhưng chưa khẳng định nhãn thật.

**So sánh hai lớp:** Lớp đứng thứ hai là DoS có xác suất rất thấp so với lớp dự đoán. Cờ khoảng cách nhỏ đang tắt và chênh lệch lớn không phải là bảo đảm dự đoán chính xác, do đó cần tiếp tục đối chiếu thêm các nguồn dữ liệu khác.

**Tổng hợp SHAP:** Trong top năm đặc trưng, IAT đóng vai trò hỗ trợ mạnh nhất đẩy giá trị đầu ra tăng cao, trong khi không ghi nhận yếu tố nào có tác động phản đối rõ rệt trong nhóm này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần đáng kể làm tăng giá trị đầu ra của lớp được giải thích.
- **Protocol Type**: Tác động này cùng chiều nhưng nhỏ hơn yếu tố dẫn đầu, đóng vai trò hỗ trợ bổ sung cho mô hình.
- **Magnitue**: Đặc trưng này thể hiện mức đóng góp dương ở mức độ vừa phải trong nhóm các yếu tố hàng đầu.
- **Header_Length**: Ghi nhận sự gia tăng đầu ra với mức độ tác động nhỏ hơn các đặc trưng đứng trước.
- **Tot size**: Mang lại tác động dương thấp nhất trong top năm, hoàn thiện nhóm năm đặc trưng có chiều hướng tăng.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu có địa chỉ và thời gian. Mục đích: Đối chiếu sự biến động của lưu lượng mạng thực tế với kết quả phân tích của mô hình.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ, không tự đặt ngưỡng. Mục đích: Xác minh khả năng chịu tải và phản ứng của hệ thống dưới các mẫu dữ liệu tương tự.

### Giới hạn do Gemini nêu

- Giải thích SHAP chỉ phản ánh đầu ra của mô hình đối với mẫu hiện tại và không chứng minh quan hệ nhân quả hay tấn công thực tế.
- Xác suất dự đoán từ mô hình chưa được kiểm chứng là đã hiệu chỉnh hoàn toàn.
- Tổng giá trị SHAP của top năm chưa bao gồm toàn bộ các đặc trưng khác ngoài nhóm.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
