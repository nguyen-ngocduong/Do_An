## mau_001 — dòng CSV 0

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491513 điểm phần trăm; ngoài top 5: +3.934622 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83034072 | +0.27957829 | +27.957829 |
| Protocol Type | 5.9400001 | +0.02736563 | +2.736563 |
| Magnitue | 10.39565 | +0.01470310 | +1.470310 |
| Min | 54 | +0.00721162 | +0.721162 |
| Number | 9.5 | +0.00671026 | +0.671026 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Hệ thống phân loại mô hình đã dự đoán mẫu thuộc lớp DDoS với mức xác suất cao và vượt trội hoàn toàn so với lớp đứng thứ hai là DoS. Các đặc trưng trong top năm đều đóng vai trò hỗ trợ nâng cao đầu ra của lớp này so với giá trị nền tham chiếu.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt vì chênh lệch giữa hai đầu ra lớn, nhưng việc này không bảo đảm dự đoán chắc chắn đúng do chưa có nhãn thật.

**Tổng hợp SHAP:** Đặc trưng IAT là yếu tố hỗ trợ mạnh nhất đẩy đầu ra tăng lên, trong khi không có yếu tố nào trong top năm tạo ra tác động phản đối mang giá trị âm.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, đóng góp mức tăng lớn nhất vào điểm số của lớp dự đoán.
- **Protocol Type**: Đặc trưng này cung cấp sự hỗ trợ bổ sung cùng chiều với mức tác động nhỏ hơn vị trí dẫn đầu.
- **Magnitue**: Sự đóng góp dương tiếp tục xuất hiện với biên độ thấp hơn để đẩy giá trị đầu ra lên.
- **Min**: Đặc trưng này mang lại một mức tác động dương nhỏ trong nhóm năm yếu tố hàng đầu.
- **Number**: Đây là yếu tố có đóng góp dương nhỏ nhất trong top năm đặc trưng được liệt kê.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu có địa chỉ và thời gian Mục đích: Đối chiếu đặc trưng lưu lượng với diễn biến thực tế trên hệ thống mạng nếu hệ thống có lưu trữ nhật ký này.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ, không tự đặt ngưỡng Mục đích: Kiểm tra khả năng chịu tải và phản ứng của hệ thống nhằm bổ sung bằng chứng đối chiếu nếu có log tài nguyên.

### Giới hạn do Gemini nêu

- Giá trị SHAP chỉ giải thích đầu ra của mô hình đối với mẫu này và không chứng minh được quan hệ nhân quả hay hành vi tấn công thực tế.
- Xác suất dự đoán chưa được kiểm chứng hay hiệu chỉnh độ tin cậy tuyệt đối.
- Tổng các giá trị SHAP trong top năm chưa phải toàn bộ sự thay đổi vì vẫn còn phần đóng góp từ các đặc trưng nằm ngoài nhóm.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
