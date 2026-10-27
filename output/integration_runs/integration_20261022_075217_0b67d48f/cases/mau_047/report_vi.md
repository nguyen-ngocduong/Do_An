## mau_047 — dòng CSV 46

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DoS**, xác suất **99.9953%**.
- Lớp đứng thứ hai: **DDoS**, xác suất **0.0034%**.
- Chênh lệch hai lớp: **99.9918 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 21.878189%.
- Tổng SHAP: +78.117067 điểm phần trăm; ngoài top 5: +1.196529 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 82951088 | +0.73616025 | +73.616025 |
| Weight | 141.55 | +0.01110684 | +1.110684 |
| Number | 9.5 | +0.00755435 | +0.755435 |
| Tot size | 54 | +0.00731982 | +0.731982 |
| Min | 54 | +0.00706413 | +0.706413 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu dữ liệu được mô hình dự đoán thuộc lớp DoS với sự hỗ trợ mạnh mẽ từ đặc trưng IAT trong nhóm năm yếu tố dẫn đầu. Sự cạnh tranh giữa lớp đứng đầu và lớp đứng thứ hai có khoảng cách lớn, trong đó lớp DDoS đứng ở vị trí tiếp theo nhưng có xác suất vô cùng nhỏ.

**So sánh hai lớp:** Lớp đứng thứ hai là DDoS có chênh lệch rất lớn so với lớp được dự đoán và cờ khoảng cách nhỏ đang tắt, tuy nhiên chênh lệch lớn này không phải là sự bảo đảm tuyệt đối rằng dự đoán là chính xác.

**Tổng hợp SHAP:** Trong top năm đặc trưng, IAT đóng vai trò hỗ trợ mạnh nhất đẩy giá trị đầu ra tăng cao, trong khi không ghi nhận tác động phản đối nào từ nhóm này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm với mức đóng góp lớn nhất vào đầu ra của lớp được dự đoán.
- **Weight**: Tác động này cùng chiều với yếu tố dẫn đầu nhưng có độ lớn nhỏ hơn đáng kể, đóng vai trò hỗ trợ bổ sung.
- **Number**: Đặc trưng này mang lại mức gia tăng dương nhỏ, tiếp tục củng cố thêm cho kết quả phân loại.
- **Tot size**: Sự hiện diện của đặc trưng này tạo ra một tác động dương thấp hơn, góp phần nhỏ vào tổng điểm SHAP.
- **Min**: Đây là yếu tố có đóng góp dương nhỏ nhất trong nhóm năm đặc trưng hàng đầu đang được xem xét.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký kết nối**: Kiểm tra kết nối lặp đến dịch vụ đích và nguồn liên quan nếu hệ thống có ghi nhận metadata này. Mục đích: Đối chiếu hành vi lưu lượng mạng thực tế với kết quả phân loại của mô hình.
- **Nhật ký tài nguyên dịch vụ**: Tìm các dấu hiệu lỗi, gián đoạn hoặc biến động tài nguyên diễn ra cùng thời điểm. Mục đích: Xác minh xem có sự cố hệ thống tương ứng đi kèm hay không.

### Giới hạn do Gemini nêu

- Giá trị SHAP chỉ phản ánh mức độ đóng góp của đặc trưng đối với đầu ra của mô hình ở mẫu hiện tại chứ không chứng minh quan hệ nhân quả trong thực tế.
- Xác suất dự đoán của mô hình chưa qua bước kiểm định hiệu chỉnh xác suất chính thức.
- Phạm vi giải thích chỉ giới hạn ở top năm đặc trưng và phần còn lại ngoài top năm chưa được phân tích chi tiết từng yếu tố riêng lẻ.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
