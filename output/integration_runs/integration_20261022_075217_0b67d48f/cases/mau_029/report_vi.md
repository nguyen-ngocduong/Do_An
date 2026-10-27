## mau_029 — dòng CSV 28

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +2.302940 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83097808 | +0.28328723 | +28.328723 |
| Min | 50 | +0.03357089 | +3.357089 |
| Magnitue | 10.015085 | +0.01722805 | +1.722805 |
| Tot sum | 526.59998 | +0.00951553 | +0.951553 |
| AVG | 50.15144 | +0.00828391 | +0.828391 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Hệ thống dự đoán mẫu thuộc lớp DDoS với sự hỗ trợ nổi bật từ đặc trưng IAT trong top năm đặc trưng quan trọng. Khoảng cách giữa lớp dẫn đầu và lớp đứng thứ hai là rất lớn, cho thấy mô hình phân loại nghiêng hẳn về một hướng duy nhất.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt, thể hiện sự chênh lệch lớn giữa hai lớp đứng đầu; tuy nhiên, điều này không được coi là sự bảo đảm tuyệt đối về độ chính xác của dự đoán.

**Tổng hợp SHAP:** Đặc trưng IAT đóng vai trò hỗ trợ mạnh mẽ nhất trong nhóm năm đặc trưng hàng đầu, trong khi không có yếu tố nào mang lại tác động phản đối trong nhóm này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, đẩy mạnh giá trị đầu ra của lớp được giải thích.
- **Min**: Tác động này cùng chiều nhưng có mức độ nhỏ hơn yếu tố dẫn đầu.
- **Magnitue**: Đóng góp bổ sung làm tăng thêm giá trị đầu ra nhưng ở mức thấp hơn.
- **Tot sum**: Yếu tố này mang lại sự hỗ trợ ở mức độ nhẹ đối với lớp dự đoán.
- **AVG**: Đóng góp cuối cùng trong nhóm top năm có tác động nhỏ nhất nhưng vẫn cùng chiều tăng.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu hệ thống có ghi nhận địa chỉ và thời gian. Mục đích: Đối chiếu sự gia tăng lưu lượng từ các nguồn khác nhau với kết quả dự đoán.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ của hệ thống. Mục đích: Xem xét ảnh hưởng của lưu lượng đến trạng thái hoạt động thực tế.

### Giới hạn do Gemini nêu

- Các giá trị SHAP chỉ giải thích đầu ra của mô hình đối với mẫu hiện tại, không chứng minh cuộc tấn công thực tế hay quan hệ nhân quả.
- Tổng các giá trị SHAP trong top năm chưa phải là toàn bộ mức thay đổi của toàn hệ thống đặc trưng.
- Xác suất dự đoán từ mô hình chưa được xác minh là đã hiệu chỉnh hoàn toàn.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
