## mau_039 — dòng CSV 38

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DoS**, xác suất **99.9953%**.
- Lớp đứng thứ hai: **DDoS**, xác suất **0.0034%**.
- Chênh lệch hai lớp: **99.9918 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 21.878189%.
- Tổng SHAP: +78.117067 điểm phần trăm; ngoài top 5: +1.329150 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83015488 | +0.73381875 | +73.381875 |
| Number | 9.5 | +0.01071900 | +1.071900 |
| Variance | 0.13 | +0.00881427 | +0.881427 |
| Weight | 141.55 | +0.00772426 | +0.772426 |
| Magnitue | 10.085241 | +0.00680288 | +0.680288 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu dữ liệu được mô hình dự đoán thuộc lớp DoS với mức độ tập trung xác suất rất cao, trong khi lớp DDoS đứng thứ hai có khoảng cách chênh lệch cực lớn. Yếu tố IAT đóng vai trò hỗ trợ mạnh mẽ nhất, đẩy giá trị đầu ra của mô hình tăng cao so với nền tham chiếu.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt do chênh lệch giữa hai lớp đứng đầu là rất lớn. Tuy nhiên, việc không có khoảng cách nhỏ không bảo đảm dự đoán chính xác tuyệt đối vì đây chỉ là kết quả phân tích đầu ra của mô hình.

**Tổng hợp SHAP:** Trong nhóm năm đặc trưng hàng đầu, đặc trưng IAT tạo ra tác động dương mạnh nhất giúp tăng đầu ra của lớp dự đoán, trong khi không ghi nhận tác động âm nào trong top năm này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, đóng góp lượng lớn điểm phần trăm làm tăng đầu ra cho lớp dự đoán.
- **Number**: Tác động này cùng chiều với đặc trưng dẫn đầu nhưng có quy mô nhỏ hơn nhiều trong nhóm.
- **Variance**: Đóng góp dương mang tính hỗ trợ bổ sung cho mô hình khi xem xét các đặc trưng tiếp theo.
- **Weight**: Ghi nhận mức tác động tăng nhẹ, tiếp tục góp phần đẩy giá trị đầu ra lệch khỏi nền tham chiếu.
- **Magnitue**: Mang lại tác động dương nhỏ nhất trong top năm đặc trưng được liệt kê.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký kết nối**: Kiểm tra kết nối lặp đến dịch vụ đích và nguồn liên quan nếu có metadata. Mục đích: Đối chiếu tần suất và đặc điểm kết nối thực tế phát sinh trong hệ thống.
- **Nhật ký tài nguyên dịch vụ**: Tìm lỗi, gián đoạn hoặc thay đổi tài nguyên cùng thời điểm để xác minh thêm. Mục đích: Xác thực xem có dấu hiệu ảnh hưởng tài nguyên hệ thống tương ứng hay không.

### Giới hạn do Gemini nêu

- Giá trị SHAP chỉ giải thích cách mô hình đưa ra quyết định dựa trên nền tham chiếu chứ không chứng minh quan hệ nhân quả hay sự tồn tại của cuộc tấn công thực tế.
- Tổng giá trị SHAP chỉ giới hạn trong nhóm năm đặc trưng hàng đầu và phần còn lại ngoài top năm chưa phản ánh toàn bộ không gian dữ liệu.
- Xác suất của mô hình chưa được kiểm chứng hay hiệu chỉnh độ tin cậy thực tế.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
