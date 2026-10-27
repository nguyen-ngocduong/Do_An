## mau_043 — dòng CSV 42

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DoS**, xác suất **99.9953%**.
- Lớp đứng thứ hai: **DDoS**, xác suất **0.0034%**.
- Chênh lệch hai lớp: **99.9918 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 21.878189%.
- Tổng SHAP: +78.117067 điểm phần trăm; ngoài top 5: +1.746004 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 82946384 | +0.72220267 | +72.220267 |
| Number | 9.5 | +0.01363787 | +1.363787 |
| Tot size | 54.119999 | +0.01145372 | +1.145372 |
| Protocol Type | 6 | +0.00851704 | +0.851704 |
| Weight | 141.55 | +0.00789933 | +0.789933 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu dữ liệu được mô hình dự đoán thuộc lớp DoS với sự hỗ trợ mạnh mẽ từ đặc trưng IAT trong nhóm top năm. Khoảng cách chênh lệch lớn giữa lớp đứng đầu và lớp đứng thứ hai cho thấy sự phân tách rõ rệt trong kết quả phân loại hiện tại.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt, cho thấy sự chênh lệch lớn giữa hai đầu ra. Tuy nhiên, việc khoảng cách lớn không được coi là bảo đảm tuyệt đối rằng dự đoán là chính xác.

**Tổng hợp SHAP:** Trong nhóm top năm đặc trưng, IAT đóng vai trò hỗ trợ mạnh mẽ nhất cho lớp được dự đoán, trong khi không có yếu tố nào trong nhóm này tạo ra tác động phản đối.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần đáng kể đẩy giá trị đầu ra của lớp được dự đoán.
- **Number**: Tác động này mang chiều hướng hỗ trợ bổ sung cho lớp dự đoán nhưng ở mức độ nhỏ hơn nhiều so với yếu tố dẫn đầu.
- **Tot size**: Đóng góp tiếp theo cùng chiều gia tăng đầu ra, thể hiện vai trò hỗ trợ phụ trợ trong tập hợp đặc trưng.
- **Protocol Type**: Đặc trưng này duy trì xu hướng tác động tăng, bổ sung thêm một phần nhỏ vào tổng điểm của lớp dự đoán.
- **Weight**: Mang lại tác động dương nhỏ nhất trong nhóm top năm, góp phần hoàn thiện bức tranh giải thích của mô hình.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký kết nối**: Kiểm tra kết nối lặp đến dịch vụ đích và nguồn liên quan nếu có metadata. Mục đích: Đối chiếu hành vi kết nối thực tế trong hệ thống với kết quả phân loại của mô hình.
- **Nhật ký tài nguyên dịch vụ**: Tìm lỗi, gián đoạn hoặc thay đổi tài nguyên cùng thời điểm để xác minh thêm. Mục đích: Xác thực xem có dấu hiệu bất thường về tài nguyên tương ứng với dự đoán hiện tại hay không.

### Giới hạn do Gemini nêu

- Giải thích này chỉ phản ánh đầu ra của mô hình dựa trên tập đặc trưng và không chứng minh quan hệ nhân quả hay cuộc tấn công thực tế.
- Các giá trị SHAP chỉ thuộc về lớp được dự đoán và không giải thích tại sao các lớp khác nhận được điểm thấp hơn.
- Xác suất của mô hình chưa được kiểm chứng hiệu chuẩn và tập top năm chưa bao gồm toàn bộ mức thay đổi.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
