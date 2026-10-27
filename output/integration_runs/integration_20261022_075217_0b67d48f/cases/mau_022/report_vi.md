## mau_022 — dòng CSV 21

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +2.528496 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83332152 | +0.26354237 | +26.354237 |
| Magnitue | 10.392304 | +0.03308238 | +3.308238 |
| Protocol Type | 6 | +0.03014220 | +3.014220 |
| Min | 54 | +0.01330408 | +1.330408 |
| Max | 54 | +0.00955901 | +0.955901 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu dữ liệu được mô hình dự đoán thuộc lớp DDoS với xác suất áp đảo nhờ sự hỗ trợ mạnh mẽ từ các đặc trưng đầu bảng. Khoảng cách giữa lớp đứng đầu và lớp đứng thứ hai rất lớn, phản ánh mức độ phân hóa rõ rệt trong kết quả phân loại.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt, cho thấy chênh lệch giữa hai lớp rất lớn; tuy nhiên điều này không bảo đảm dự đoán chắc chắn là đúng nhãn thật.

**Tổng hợp SHAP:** Trong nhóm năm đặc trưng đang xét, IAT đóng vai trò hỗ trợ mạnh nhất đẩy giá trị đầu ra lên cao, trong khi không ghi nhận yếu tố nào mang giá trị phản đối trong top năm.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần đáng kể làm tăng đầu ra của lớp được dự đoán so với nền tham chiếu.
- **Magnitue**: Tác động này cùng chiều nhưng nhỏ hơn yếu tố dẫn đầu, đóng vai trò bổ sung cho quá trình phân loại.
- **Protocol Type**: Sự hiện diện của đặc trưng này tiếp tục củng cố thêm bằng chứng dương cho lớp dự đoán.
- **Min**: Đặc trưng này thể hiện một mức đóng góp dương nhỏ hơn trong nhóm năm yếu tố hàng đầu.
- **Max**: Đây là thành phần có tác động nhỏ nhất trong top năm, hoàn thiện bức tranh giải thích của mô hình cho mẫu này.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu hệ thống có ghi nhận địa chỉ và thời gian. Mục đích: Đối chiếu mô hình với phân phối thực tế của gói tin.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ của hệ thống. Mục đích: Kiểm tra sự biến động tải thực tế trên thiết bị mục tiêu.

### Giới hạn do Gemini nêu

- Giá trị SHAP chỉ giải thích đầu ra mô hình cho mẫu này và không chứng minh quan hệ nhân quả hay cuộc tấn công thực tế.
- Xác suất dự đoán từ mô hình chưa được kiểm chứng là đã hiệu chỉnh hoàn toàn.
- Tổng giá trị SHAP trong top năm chưa bao trùm toàn bộ các đặc trưng của mô hình.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
