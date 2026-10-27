## mau_035 — dòng CSV 34

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DoS**, xác suất **99.9952%**.
- Lớp đứng thứ hai: **DDoS**, xác suất **0.0034%**.
- Chênh lệch hai lớp: **99.9918 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 21.878189%.
- Tổng SHAP: +78.117043 điểm phần trăm; ngoài top 5: +2.014164 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83006904 | +0.70583542 | +70.583542 |
| Tot size | 42 | +0.01654549 | +1.654549 |
| Number | 9.5 | +0.01460634 | +1.460634 |
| Magnitue | 9.1651516 | +0.01324965 | +1.324965 |
| Min | 42 | +0.01079189 | +1.079189 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu thuộc lớp DoS với xác suất rất cao, trong đó đặc trưng IAT đóng vai trò hỗ trợ mạnh nhất đẩy giá trị đầu ra tăng. Lớp đứng thứ hai là DDoS nhưng có khoảng cách xác suất rất lớn so với lớp dẫn đầu.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt, cho thấy sự chênh lệch giữa hai lớp đứng đầu là lớn; tuy nhiên, điều này không được coi là bảo đảm tuyệt đối cho dự đoán.

**Tổng hợp SHAP:** Trong top năm đặc trưng, IAT đóng vai trò hỗ trợ mạnh nhất làm tăng đầu ra, trong khi không có đặc trưng nào trong nhóm này tạo ra tác động phản đối.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, đóng góp lớn vào giá trị đầu ra của lớp được dự đoán.
- **Tot size**: Tác động này cùng chiều nhưng nhỏ hơn yếu tố dẫn đầu, đóng vai trò hỗ trợ bổ sung cho mô hình.
- **Number**: Đặc trưng này thể hiện mức đóng góp dương ở mức độ thấp hơn so với đặc trưng đứng trước.
- **Magnitue**: Sự gia tăng từ đặc trưng này mang lại một phần hỗ trợ nhỏ cho lớp được giải thích.
- **Min**: Đây là yếu tố có tác động dương nhỏ nhất trong nhóm năm đặc trưng được phân tích.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký kết nối**: Kiểm tra kết nối lặp đến dịch vụ đích và nguồn liên quan nếu có metadata. Mục đích: Đối chiếu xem có các lượt kết nối lặp lại phù hợp với dữ liệu ghi nhận hay không.
- **Nhật ký tài nguyên dịch vụ**: Tìm lỗi, gián đoạn hoặc thay đổi tài nguyên cùng thời điểm để xác minh thêm. Mục đích: Xác thực xem hệ thống có chịu ảnh hưởng hoặc biến động tài nguyên tương ứng hay không.

### Giới hạn do Gemini nêu

- Giải thích SHAP chỉ phản ánh đầu ra của mô hình đối với mẫu hiện tại và không chứng minh quan hệ nhân quả hay tấn công thực tế.
- Giá trị nền tham chiếu không đại diện cho xác suất riêng của thuật toán hay tỷ lệ phân bố lớp thực tế.
- Tổng giá trị SHAP của top năm chưa bao trùm toàn bộ các thành phần thay đổi đầu ra.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
