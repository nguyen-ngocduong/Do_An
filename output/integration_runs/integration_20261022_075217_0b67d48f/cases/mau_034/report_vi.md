## mau_034 — dòng CSV 33

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +3.475949 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83072248 | +0.27685068 | +27.685068 |
| Protocol Type | 6 | +0.02322738 | +2.322738 |
| Magnitue | 10.392304 | +0.01956912 | +1.956912 |
| Number | 9.5 | +0.01192749 | +1.192749 |
| Min | 54 | +0.00858085 | +0.858085 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu này thuộc lớp DDoS với xác suất rất cao, trong đó đặc trưng IAT là yếu tố hỗ trợ mạnh nhất giúp đẩy điểm số lên rõ rệt. Lớp đứng thứ hai là DoS nhưng có khoảng cách rất xa về mặt xác suất, cho thấy sự chênh lệch rõ ràng trong quyết định của mô hình.

**So sánh hai lớp:** Có ký hiệu DoS là lớp đứng thứ hai trong bảng chứng tổng hợp. Vì có khoảng cách lớn và cờ tắt, chênh lệch lớn này không được coi là bảo đảm dự đoán đúng vì chúng ta chưa biết nhãn thật và xác suất chưa được xác minh đã hiệu chỉnh.

**Tổng hợp SHAP:** Trong top năm đặc trưng được xét, IAT là yếu tố hỗ trợ mạnh nhất đẩy đầu ra của lớp dự đoán tăng lên so với nền tham chiếu, trong khi không có yếu tố nào trong top này mang lại tác động âm.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm và có đóng góp lớn nhất vào đầu ra của lớp dự đoán.
- **Protocol Type**: Tác động này cùng chiều nhưng nhỏ hơn đáng kể so với yếu tố dẫn đầu trong danh sách.
- **Magnitue**: Đặc trưng này mang lại sự hỗ trợ bổ sung ở mức độ thấp hơn để thúc đẩy kết quả phân loại.
- **Number**: Sự đóng góp dương từ đặc trưng này tiếp tục củng cố đầu ra nhưng có giá trị nhỏ.
- **Min**: Đây là tác động nhỏ nhất trong top năm đặc trưng được liệt kê đối với lớp dự đoán.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu hệ thống có lưu trữ địa chỉ và thời gian. Mục đích: Đối chiếu biểu hiện lưu lượng để hỗ trợ việc xem xét nguồn gốc kết nối.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ hiện tại của hệ thống. Mục đích: Đánh giá thêm khả năng đáp ứng và trạng thái tài nguyên thực tế khi xử lý.

### Giới hạn do Gemini nêu

- Đây là giải thích đầu ra model, không chứng minh cuộc tấn công thực tế hoặc quan hệ nhân quả.
- Các giá trị SHAP và xác suất chỉ phản ánh trạng thái của mô hình tại thời điểm tính toán và chưa được xác minh là đã hiệu chỉnh.
- Tổng hợp chỉ giới hạn trong năm đặc trưng hàng đầu và không đại diện cho toàn bộ đặc trưng hoặc toàn bộ hệ thống.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
