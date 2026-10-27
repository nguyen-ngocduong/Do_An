## mau_046 — dòng CSV 45

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +2.642092 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83107448 | +0.28266464 | +28.266464 |
| Min | 50 | +0.02393627 | +2.393627 |
| Magnitue | 10 | +0.01864661 | +1.864661 |
| Max | 50 | +0.01342327 | +1.342327 |
| Tot size | 50 | +0.00982331 | +0.982331 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu dữ liệu thuộc lớp DDoS với sự hỗ trợ mạnh mẽ từ đặc trưng IAT trong top năm. Lớp đứng thứ hai là DoS nhưng có khoảng cách xác suất rất lớn so với lớp dẫn đầu.

**So sánh hai lớp:** Cờ khoảng cách nhỏ tắt do chênh lệch xác suất giữa DDoS và DoS rất lớn, tuy nhiên mức chênh lệch cao không được coi là bảo đảm tuyệt đối cho dự đoán.

**Tổng hợp SHAP:** Trong top năm đặc trưng, IAT đóng vai trò hỗ trợ mạnh nhất cho lớp dự đoán trong khi không ghi nhận tác động phản đối nào từ nhóm này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần đáng kể vào đầu ra của lớp dự đoán.
- **Min**: Tác động này cùng chiều nhưng có quy mô nhỏ hơn yếu tố dẫn đầu.
- **Magnitue**: Sự đóng góp dương tiếp tục bổ sung bằng chứng củng cố cho đầu ra mô hình.
- **Max**: Thành phần này mang lại một mức tác động dương bổ trợ ở mức độ thấp hơn.
- **Tot size**: Đóng góp dương ở vị trí này có ảnh hưởng nhỏ nhất trong top năm đặc trưng.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu hệ thống ghi nhận địa chỉ và thời gian. Mục đích: Đối chiếu tính chất lưu lượng mạng thực tế với kết quả phân tích của mô hình.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ của hệ thống. Mục đích: Kiểm tra ảnh hưởng của tải công việc lên hệ thống dịch vụ dựa trên dữ liệu nhật ký.

### Giới hạn do Gemini nêu

- Các giá trị SHAP chỉ phản ánh mức đóng góp vào đầu ra của mô hình đối với mẫu hiện tại, không chứng minh quan hệ nhân quả hay xác nhận cuộc tấn công thực tế.
- Xác suất dự đoán chưa được hiệu chỉnh chính thức và không đại diện cho độ chính xác tuyệt đối của nhãn.
- Tổng hợp SHAP chỉ giới hạn trong top năm đặc trưng và phần còn lại ngoài nhóm, không đại diện cho toàn bộ không gian dữ liệu.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
