## mau_044 — dòng CSV 43

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DoS**, xác suất **99.9953%**.
- Lớp đứng thứ hai: **DDoS**, xác suất **0.0034%**.
- Chênh lệch hai lớp: **99.9918 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 21.878189%.
- Tổng SHAP: +78.117067 điểm phần trăm; ngoài top 5: +1.566404 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83011848 | +0.72878078 | +72.878078 |
| Magnitue | 10 | +0.01423209 | +1.423209 |
| Number | 9.5 | +0.01121373 | +1.121373 |
| Max | 50 | +0.00571902 | +0.571902 |
| Tot sum | 525 | +0.00556102 | +0.556102 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu được dự đoán là lớp DoS với mức độ ưu tiên vượt trội so với các lớp còn lại. Đặc trưng IAT đóng vai trò hỗ trợ mạnh nhất, trong khi không có yếu tố nào trong top năm phản đối kết quả này. Khoảng cách với lớp đứng thứ hai là rất lớn.

**So sánh hai lớp:** Cờ khoảng cách nhỏ tắt, thể hiện khoảng cách lớn giữa hai đầu ra. Tuy nhiên, điều này không bảo đảm dự đoán hoàn toàn chính xác do thiếu nhãn thực tế.

**Tổng hợp SHAP:** IAT là yếu tố hỗ trợ mạnh nhất trong nhóm, đồng thời không ghi nhận yếu tố phản đối nào trong top năm đặc trưng.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần đáng kể vào đầu ra của mô hình.
- **Magnitue**: Tác động này cùng chiều nhưng có độ lớn nhỏ hơn nhiều so với yếu tố dẫn đầu.
- **Number**: Đóng góp bổ sung tiếp theo theo chiều dương cho lớp được dự đoán.
- **Max**: Mang lại một mức hỗ trợ dương nhỏ hơn trong nhóm đặc trưng đang xét.
- **Tot sum**: Tác động dương cuối cùng trong top năm với mức đóng góp thấp nhất.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký kết nối**: Kiểm tra kết nối lặp đến dịch vụ đích và nguồn liên quan nếu có metadata. Mục đích: Đối chiếu sự xuất hiện của các kết nối lặp trong hệ thống.
- **Nhật ký tài nguyên dịch vụ**: Tìm lỗi, gián đoạn hoặc thay đổi tài nguyên cùng thời điểm để xác minh thêm. Mục đích: Xác minh các dấu hiệu bất thường về tài nguyên nếu có log.

### Giới hạn do Gemini nêu

- Kết quả giải thích chỉ phản ánh đầu ra của mô hình đối với mẫu dữ liệu hiện tại, không chứng minh quan hệ nhân quả.
- Giá trị SHAP chỉ đại diện cho một phần thay đổi và chưa bao gồm toàn bộ không gian đặc trưng.
- Xác suất dự đoán chưa qua bước hiệu chỉnh xác suất thực tế.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
