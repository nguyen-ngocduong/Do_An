## mau_030 — dòng CSV 29

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +3.007368 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83345200 | +0.26947099 | +26.947099 |
| Magnitue | 10.392304 | +0.03663543 | +3.663543 |
| Min | 54 | +0.01714817 | +1.714817 |
| Protocol Type | 6 | +0.01187145 | +1.187145 |
| Tot size | 54 | +0.00971531 | +0.971531 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu dữ liệu thuộc lớp DDoS với xác suất rất cao, trong đó đặc trưng IAT đóng vai trò hỗ trợ nổi bật nhất. Khoảng cách với lớp đứng thứ hai là DoS rất lớn và cờ khoảng cách nhỏ tắt, cho thấy không có sự cạnh tranh đáng kể giữa hai lớp này trong trường hợp này.

**So sánh hai lớp:** Lớp đứng thứ hai là DoS có xác suất vô cùng nhỏ so với lớp dự đoán và cờ khoảng cách nhỏ tắt. Chênh lệch lớn này không bảo đảm dự đoán hoàn toàn đúng mà chỉ phản ánh đầu ra của mô hình đối với mẫu đang xét.

**Tổng hợp SHAP:** Trong top năm đặc trưng, IAT là yếu tố hỗ trợ mạnh nhất đẩy đầu ra tăng lên, trong khi không có đặc trưng nào trong nhóm này mang giá trị âm để tạo tác động phản đối.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần đáng kể làm tăng giá trị đầu ra của lớp được giải thích so với nền tham chiếu.
- **Magnitue**: Tác động này cùng chiều nhưng có độ lớn nhỏ hơn đáng kể so với yếu tố dẫn đầu, đóng vai trò hỗ trợ bổ sung cho kết quả dự đoán.
- **Min**: Đặc trưng này thể hiện một mức đóng góp dương ở mức độ vừa phải trong nhóm năm đặc trưng hàng đầu.
- **Protocol Type**: Sự hiện diện của đặc trưng này mang lại một lực đẩy nhỏ cùng chiều với xu hướng chung của mô hình.
- **Tot size**: Đây là đóng góp dương có giá trị nhỏ nhất trong top năm đặc trưng, bổ sung một phần tác động vào đầu ra.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu có địa chỉ và thời gian. Mục đích: Đối chiếu sự xuất hiện đồng thời từ nhiều nguồn trên hệ thống để có thêm thông tin ngữ cảnh.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ, không tự đặt ngưỡng. Mục đích: So sánh mức độ sử dụng tài nguyên thực tế của dịch vụ nhằm hỗ trợ quá trình phân tích.

### Giới hạn do Gemini nêu

- Các giá trị SHAP chỉ giải thích đầu ra của mô hình phân loại cho mẫu này và không chứng minh quan hệ nhân quả hay sự tồn tại của tấn công thực tế.
- Tổng giá trị SHAP trong top năm chưa phải là toàn bộ mức thay đổi vì vẫn còn phần đóng góp từ các đặc trưng nằm ngoài nhóm này.
- Xác suất dự đoán của mô hình chưa được kiểm chứng là đã hiệu chỉnh và không đại diện cho nhãn thật của dữ liệu.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
