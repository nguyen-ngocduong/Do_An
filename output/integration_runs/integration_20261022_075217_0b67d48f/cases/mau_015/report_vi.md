## mau_015 — dòng CSV 14

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9969 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491430 điểm phần trăm; ngoài top 5: +2.092131 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83123680 | +0.29237648 | +29.237648 |
| Magnitue | 10 | +0.02341188 | +2.341188 |
| Min | 50 | +0.02087632 | +2.087632 |
| Number | 9.5 | +0.00881280 | +0.881280 |
| Tot size | 50 | +0.00851550 | +0.851550 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu dữ liệu thuộc lớp DDoS với sự hỗ trợ mạnh mẽ từ đặc trưng IAT trong top năm, trong khi các đặc trưng còn lại đều theo chiều hướng tăng. Lớp đứng thứ hai là DoS có xác suất rất nhỏ, tạo khoảng cách lớn với lớp dẫn đầu và không có cờ khoảng cách nhỏ bật.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt và chênh lệch xác suất rất lớn, cho thấy mô hình ưu tiên mạnh cho lớp đứng đầu, tuy nhiên điều này không bảo đảm đây là nhãn thật hay khẳng định tính đúng đắn của dự đoán.

**Tổng hợp SHAP:** Trong nhóm top năm, IAT đóng vai trò hỗ trợ mạnh nhất đẩy giá trị đầu ra lên cao, trong khi không có đặc trưng nào trong nhóm này tạo ra tác động phản đối mang giá trị âm.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần đáng kể làm tăng giá trị đầu ra của lớp được giải thích so với nền tham chiếu.
- **Magnitue**: Đóng góp này mang chiều hướng tăng nhưng có mức độ ảnh hưởng nhỏ hơn rõ rệt so với yếu tố dẫn đầu ở trên.
- **Min**: Tác động này tiếp tục hỗ trợ tăng đầu ra của mô hình với một mức đóng góp bổ sung trong nhóm đặc trưng.
- **Number**: Đây là một thành phần hỗ trợ bổ sung với mức tác động thấp hơn các đặc trưng đứng trước.
- **Tot size**: Đặc trưng này mang lại tác động dương nhỏ nhất trong top năm, bổ sung vào tổng lượng thay đổi đầu ra.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu hệ thống có ghi nhận địa chỉ và thời gian. Mục đích: Đối chiếu mô hình với dữ liệu thực tế để xem xét bối cảnh lưu lượng mạng.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ của hệ thống. Mục đích: Kiểm tra sự biến động tài nguyên nhằm hỗ trợ việc xem xét ngữ cảnh hoạt động.

### Giới hạn do Gemini nêu

- Các giá trị SHAP chỉ giải thích đầu ra của mô hình đối với mẫu hiện tại, không chứng minh quan hệ nhân quả hay xác nhận cuộc tấn công thực tế.
- Tổng các giá trị SHAP trong top năm chưa bao gồm toàn bộ phần thay đổi ngoài nhóm, và xác suất của mô hình chưa được kiểm chứng là đã hiệu chỉnh.
- Phân tích này không đại diện cho nhãn thực tế của dữ liệu và không dùng để đưa ra các hành động tự động như chặn IP hay thay đổi cấu hình.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
