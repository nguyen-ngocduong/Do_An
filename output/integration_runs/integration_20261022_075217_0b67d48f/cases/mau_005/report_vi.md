## mau_005 — dòng CSV 4

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **Normal**, xác suất **99.2367%**.
- Lớp đứng thứ hai: **Spoofing**, xác suất **0.3880%**.
- Chênh lệch hai lớp: **98.8487 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 5.920577%.
- Tổng SHAP: +93.316132 điểm phần trăm; ngoài top 5: +21.095353 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **urg_count**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| urg_count | 90 | +0.23424347 | +23.424347 |
| rst_count | 2126.5 | +0.18010461 | +18.010461 |
| IAT | 0.0049007894 | +0.13012446 | +13.012446 |
| Number | 5.5 | +0.10711341 | +10.711341 |
| flow_duration | 53.269356 | +0.07062183 | +7.062183 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu được dự đoán là lớp Normal với xác suất cao, trong đó đặc trưng urg_count đóng vai trò hỗ trợ mạnh nhất và không ghi nhận yếu tố phản đối nào trong top năm. Lớp đứng thứ hai là Spoofing có khoảng cách chênh lệch lớn so với lớp dẫn đầu và cờ khoảng cách nhỏ không bật.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt và chênh lệch giữa hai đầu ra lớn. Tuy nhiên, việc không bật cờ này không bảo đảm dự đoán chắc chắn là đúng nhãn thật.

**Tổng hợp SHAP:** Trong nhóm năm đặc trưng hàng đầu, urg_count là yếu tố hỗ trợ mạnh nhất đẩy giá trị đầu ra lên cao, trong khi không có yếu tố nào mang giá trị âm để phản đối trong nhóm này.

- **urg_count**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, đóng góp tích cực vào đầu ra của lớp được dự đoán.
- **rst_count**: Tác động này cùng chiều nhưng có độ lớn nhỏ hơn yếu tố dẫn đầu trong nhóm.
- **IAT**: Đặc trưng này cung cấp thêm một mức hỗ trợ dương với mức đóng góp ở ngưỡng trung bình.
- **Number**: Sự hiện diện của đặc trưng này tiếp tục củng cố đầu ra theo chiều hướng tăng.
- **flow_duration**: Đây là yếu tố có mức tác động nhỏ nhất trong top năm nhưng vẫn duy trì chiều hướng đóng góp dương.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký kết nối**: Đối chiếu đích kết nối, dịch vụ và thời điểm với hoạt động được phép Mục đích: Xác định xem lưu lượng có tuân thủ các quy tắc truy cập chuẩn hay không nếu hệ thống có lưu trữ log này.
- **Nhật ký thiết bị**: Kiểm tra lỗi hoặc cảnh báo đồng thời; dự đoán Normal không bảo đảm an toàn Mục đích: Kiểm tra các dấu hiệu bất thường tiềm ẩn ở tầng thiết bị nếu hệ thống ghi nhận.

### Giới hạn do Gemini nêu

- Giá trị SHAP chỉ giải thích đầu ra của mô hình đối với mẫu hiện tại, không chứng minh quan hệ nhân quả hay hành vi tấn công thực tế.
- Dự đoán lớp Normal không bảo đảm hệ thống hoàn toàn an toàn hay không có rủi ro tiềm ẩn.
- Tổng giá trị SHAP của top năm chưa bao trùm toàn bộ các đặc trưng và xác suất chưa được hiệu chỉnh chính thức.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
