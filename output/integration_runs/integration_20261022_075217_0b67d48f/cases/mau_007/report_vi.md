## mau_007 — dòng CSV 6

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DoS**, xác suất **99.9953%**.
- Lớp đứng thứ hai: **DDoS**, xác suất **0.0034%**.
- Chênh lệch hai lớp: **99.9918 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 21.878189%.
- Tổng SHAP: +78.117067 điểm phần trăm; ngoài top 5: +1.786710 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 82985616 | +0.72209427 | +72.209427 |
| Number | 9.5 | +0.01299066 | +1.299066 |
| Protocol Type | 6 | +0.01053786 | +1.053786 |
| Magnitue | 10.39527 | +0.01037405 | +1.037405 |
| Weight | 141.55 | +0.00730674 | +0.730674 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu dữ liệu được mô hình dự đoán là lớp DoS với sự hỗ trợ áp đảo từ đặc trưng IAT trong top năm đặc trưng hàng đầu. Khoảng cách giữa lớp DoS và lớp đứng thứ hai là rất lớn, cho thấy mô hình phân loại rõ rệt mà không có sự cạnh tranh đáng kể từ các lớp khác.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt, cho thấy sự chênh lệch lớn giữa lớp đứng đầu và lớp đứng thứ hai không có nghĩa là sự đảm bảo tuyệt đối về nhãn thật do chưa có thông tin xác thực.

**Tổng hợp SHAP:** Trong nhóm năm đặc trưng đang xét, IAT đóng vai trò hỗ trợ mạnh nhất cho lựa chọn của mô hình, trong khi không có yếu tố nào trong top năm mang lại tác động phản đối.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, đóng góp lớn nhất vào đầu ra của mô hình.
- **Number**: Tác động này cùng chiều nhưng nhỏ hơn đáng kể so với yếu tố dẫn đầu.
- **Protocol Type**: Đóng góp bổ sung một lượng nhỏ theo chiều làm tăng giá trị đầu ra.
- **Magnitue**: Ghi nhận mức hỗ trợ theo chiều dương với quy mô tương đương nhóm đóng góp phụ.
- **Weight**: Đây là tác động có độ lớn thấp nhất trong số năm đặc trưng hàng đầu.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký kết nối**: Kiểm tra kết nối lặp đến dịch vụ đích và nguồn liên quan nếu có metadata. Mục đích: Đối chiếu sự xuất hiện của các kết nối lặp nhằm làm rõ bối cảnh mạng.
- **Nhật ký tài nguyên dịch vụ**: Tìm lỗi, gián đoạn hoặc thay đổi tài nguyên cùng thời điểm để xác minh thêm. Mục đích: Xác định tình trạng hệ thống có khớp với các dấu hiệu bất thường hay không.

### Giới hạn do Gemini nêu

- Giá trị SHAP chỉ phản ánh cách mô hình đưa ra quyết định dựa trên mẫu hiện tại, không chứng minh mối quan hệ nhân quả hay hành vi tấn công thực tế.
- Xác suất dự đoán từ mô hình chưa được kiểm chứng hay hiệu chỉnh để đảm bảo độ chính xác tuyệt đối.
- Phần giá trị SHAP nằm ngoài top năm tuy nhỏ nhưng vẫn góp phần cấu thành đầu ra cuối cùng của mô hình.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
