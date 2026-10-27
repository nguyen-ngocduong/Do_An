## mau_014 — dòng CSV 13

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +4.200794 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83149320 | +0.26549649 | +26.549649 |
| Protocol Type | 1 | +0.02288696 | +2.288696 |
| Magnitue | 9.1651516 | +0.01776957 | +1.776957 |
| Max | 42 | +0.01606101 | +1.606101 |
| Min | 42 | +0.01069304 | +1.069304 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán lớp DDoS với sự hỗ trợ mạnh mẽ từ đặc trưng IAT trong top năm đặc trưng quan trọng. Trong khi đó, lớp DoS đứng ở vị trí thứ hai nhưng có khoảng cách rất xa so với đầu ra hàng đầu.

**So sánh hai lớp:** Lớp đứng thứ hai là DoS. Cờ khoảng cách nhỏ đang tắt cho thấy chênh lệch giữa hai đầu ra lớn, tuy nhiên điều này không được coi là bảo đảm dự đoán chính xác tuyệt đối.

**Tổng hợp SHAP:** Yếu tố hỗ trợ mạnh nhất trong top năm đặc trưng là IAT, trong khi không có tác động phản đối nào xuất hiện trong nhóm này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm của mẫu này.
- **Protocol Type**: Tác động này cùng chiều nhưng đóng góp ở mức hỗ trợ bổ sung nhỏ hơn.
- **Magnitue**: Đặc trưng này thể hiện một sự thúc đẩy bổ sung có giá trị thấp hơn các yếu tố trước.
- **Max**: Sự đóng góp theo chiều tăng tiếp tục xuất hiện với mức độ thu hẹp dần.
- **Min**: Đây là tác động có xu hướng cùng chiều nhỏ nhất trong nhóm năm đặc trưng.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu có địa chỉ và thời gian. Mục đích: Đối chiếu thông tin lưu lượng thực tế phát sinh trong hệ thống.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ, không tự đặt ngưỡng. Mục đích: Xác thực khả năng đáp ứng và tải hiện tại của dịch vụ.

### Giới hạn do Gemini nêu

- Kết quả giải thích chỉ phản ánh đầu ra của mô hình đối với mẫu hiện tại, không chứng minh quan hệ nhân quả hay cuộc tấn công thực tế.
- Giá trị SHAP và xác suất chưa được hiệu chỉnh chính thức để đảm bảo độ tin cậy tuyệt đối.
- Tổng các đặc trưng trong top năm chưa bao trùm toàn bộ mức thay đổi của toàn bộ tập đặc trưng.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
