## mau_020 — dòng CSV 19

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +2.364424 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83102336 | +0.26599439 | +26.599439 |
| Min | 50 | +0.03373025 | +3.373025 |
| Magnitue | 10 | +0.02820080 | +2.820080 |
| Tot sum | 525 | +0.01643970 | +1.643970 |
| Number | 9.5 | +0.00690562 | +0.690562 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu dữ liệu thuộc lớp DDoS dựa trên các đặc trưng lưu lượng mạng nổi bật. Yếu tố IAT đóng vai trò hỗ trợ mạnh nhất, trong khi các đặc trưng khác trong top năm đều góp phần củng cố cùng chiều hướng này mà không ghi nhận yếu tố phản đối. Sự chênh lệch giữa lớp đứng đầu và lớp DoS đứng thứ hai rất lớn.

**So sánh hai lớp:** Cờ khoảng cách nhỏ tắt, cho thấy khoảng cách giữa lớp DDoS đứng đầu và lớp DoS đứng thứ hai là khá lớn theo quy tắc trình bày. Tuy nhiên, việc chênh lệch lớn không bảo đảm dự đoán hoàn toàn chính xác do chưa có nhãn thật.

**Tổng hợp SHAP:** Trong năm đặc trưng hàng đầu, IAT là yếu tố hỗ trợ mạnh mẽ nhất làm tăng giá trị đầu ra của lớp dự đoán so với nền tham chiếu, hoàn toàn không có yếu tố nào mang giá trị SHAP âm trong nhóm này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, đóng góp lớn nhất vào việc đẩy giá trị đầu ra của lớp dự đoán lên cao hơn so với tham chiếu.
- **Min**: Tác động này cùng chiều nhưng nhỏ hơn yếu tố dẫn đầu, đóng vai trò hỗ trợ bổ sung cho kết quả phân loại.
- **Magnitue**: Đóng góp theo chiều hướng tăng với mức ảnh hưởng tiếp theo trong nhóm năm đặc trưng quan trọng.
- **Tot sum**: Mang lại thêm một lực đẩy cùng chiều với mức tác động nhỏ hơn các đặc trưng đứng trước.
- **Number**: Thể hiện tác động dương ở mức nhỏ nhất trong top năm đặc trưng được tổng hợp.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu có địa chỉ và thời gian Mục đích: Đối chiếu hành vi lưu lượng thực tế được ghi nhận trong hệ thống.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ Mục đích: Kiểm tra xem hệ thống có chịu áp lực tương ứng từ các đặc trưng đã phân tích hay không.

### Giới hạn do Gemini nêu

- Kết quả này chỉ là giải thích đầu ra của mô hình, không chứng minh cuộc tấn công thực tế hay quan hệ nhân quả.
- Giá trị xác suất chưa được kiểm chứng về độ hiệu chỉnh và chỉ phản ánh xu hướng học được từ dữ liệu.
- Phạm vi giải thích chỉ giới hạn trong các đặc trưng top năm và không đại diện cho toàn bộ hệ thống hay mọi biến động ngoài mô hình.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
