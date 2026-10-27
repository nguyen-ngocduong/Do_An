## mau_031 — dòng CSV 30

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +3.549452 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83343856 | +0.27770421 | +27.770421 |
| Magnitue | 10.392304 | +0.02416340 | +2.416340 |
| Protocol Type | 6 | +0.01685037 | +1.685037 |
| Min | 54 | +0.01084579 | +1.084579 |
| Max | 54 | +0.00985672 | +0.985672 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu thuộc lớp DDoS với xác suất áp đảo nhờ sự hỗ trợ mạnh mẽ từ đặc trưng IAT. Cạnh tranh giữa hai lớp đứng đầu không quá gay gắt khi lớp đứng thứ hai là DoS có xác suất rất thấp.

**So sánh hai lớp:** Lớp đứng thứ hai là DoS với khoảng cách chênh lệch lớn và cờ khoảng cách nhỏ đang tắt, tuy nhiên việc chênh lệch lớn không coi là bảo đảm dự đoán đúng và không kết luận đã biết nhãn thật.

**Tổng hợp SHAP:** Trong nhóm năm đặc trưng hàng đầu, IAT đóng vai trò hỗ trợ mạnh nhất đẩy giá trị đầu ra tăng, trong khi không ghi nhận yếu tố nào có tác động phản đối trong top năm.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, đóng góp lớn vào việc tăng đầu ra của lớp được dự đoán.
- **Magnitue**: Tác động này cùng chiều nhưng nhỏ hơn yếu tố dẫn đầu, đóng vai trò hỗ trợ bổ sung cho mô hình.
- **Protocol Type**: Đặc trưng này thể hiện một hướng tác động đồng thuận tương tự nhưng với mức độ thấp hơn.
- **Min**: Sự góp mặt của yếu tố này tiếp tục củng cố đầu ra theo chiều hướng tăng với mức đóng góp khiêm tốn.
- **Max**: Đây là đặc trưng có tác động nhỏ hơn cả trong nhóm năm yếu tố hàng đầu xét về mức độ thay đổi.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu có địa chỉ và thời gian. Mục đích: Đối chiếu hành vi lưu lượng để tìm bằng chứng liên quan đến mẫu đang xem xét.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ, không tự đặt ngưỡng. Mục đích: Xác thực trạng thái hệ thống nhằm hỗ trợ việc phân tích ngữ cảnh của dữ liệu.

### Giới hạn do Gemini nêu

- Đây là giải thích đầu ra model, không chứng minh cuộc tấn công thực tế hoặc quan hệ nhân quả.
- Xác suất dự đoán chưa được xác minh là đã hiệu chỉnh và tổng top 5 chưa phải toàn bộ mức thay đổi.
- Giá trị SHAP chỉ phản ánh mức đóng góp so với nền tham chiếu, không đại diện cho nhãn thực tế.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
