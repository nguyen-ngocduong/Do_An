## mau_025 — dòng CSV 24

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DoS**, xác suất **99.9953%**.
- Lớp đứng thứ hai: **DDoS**, xác suất **0.0034%**.
- Chênh lệch hai lớp: **99.9919 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 21.878189%.
- Tổng SHAP: +78.117079 điểm phần trăm; ngoài top 5: +1.400963 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 82972640 | +0.73266740 | +73.266740 |
| Weight | 141.55 | +0.01095809 | +1.095809 |
| Variance | 0.19 | +0.00958675 | +0.958675 |
| syn_flag_number | 1 | +0.00790169 | +0.790169 |
| Number | 9.5 | +0.00604725 | +0.604725 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu được mô hình XGB_d4_n200 phân loại vào lớp DoS với mức độ tự tin rất cao. Đặc trưng IAT đóng vai trò hỗ trợ mạnh mẽ nhất, trong khi lớp đứng thứ hai là DDoS có khoảng cách xác suất rất lớn.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt cho thấy chênh lệch giữa hai lớp rất lớn, nhưng điều này không được coi là bảo đảm tuyệt đối rằng dự đoán đã chính xác.

**Tổng hợp SHAP:** IAT là yếu tố hỗ trợ mạnh nhất trong top 5, không có đặc trưng nào trong top 5 mang giá trị phản đối âm.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần đáng kể vào đầu ra của mô hình.
- **Weight**: Tác động này cùng chiều nhưng nhỏ hơn yếu tố dẫn đầu.
- **Variance**: Đặc trưng này mang lại một mức hỗ trợ bổ sung với biên độ thấp hơn.
- **syn_flag_number**: Sự hiện diện của đặc trưng này đóng góp thêm một lực đẩy nhẹ cho dự đoán.
- **Number**: Đây là tác động có quy mô nhỏ nhất trong nhóm năm đặc trưng được xem xét.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký kết nối**: Kiểm tra kết nối lặp đến dịch vụ đích và nguồn liên quan nếu có metadata. Mục đích: Đối chiếu tần suất và đặc điểm kết nối mạng thực tế.
- **Nhật ký tài nguyên dịch vụ**: Tìm lỗi, gián đoạn hoặc thay đổi tài nguyên cùng thời điểm để xác minh thêm. Mục đích: Kiểm tra xem hệ thống có chịu áp lực hoặc biểu hiện gián đoạn tương ứng hay không.

### Giới hạn do Gemini nêu

- Kết quả giải thích chỉ phản ánh đầu ra của mô hình đối với mẫu này, không chứng minh quan hệ nhân quả hay hành vi tấn công thực tế.
- Giá trị SHAP chỉ đại diện cho top 5 đặc trưng của lớp dự đoán và không bao gồm toàn bộ mọi yếu tố trong hệ thống.
- Xác suất dự đoán từ mô hình chưa qua bước kiểm định hiệu chỉnh xác suất thực tế.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
