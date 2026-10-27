## mau_050 — dòng CSV 49

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +3.614196 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83124880 | +0.26923641 | +26.923641 |
| Protocol Type | 1 | +0.02222695 | +2.222695 |
| Magnitue | 9.1651516 | +0.02213061 | +2.213061 |
| Min | 42 | +0.01435591 | +1.435591 |
| AVG | 42 | +0.01082316 | +1.082316 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu này được dự đoán là lớp DDoS với xác suất rất cao, vượt trội hoàn toàn so với lớp đứng thứ hai là DoS. Đặc trưng IAT đóng vai trò hỗ trợ mạnh nhất đẩy giá trị đầu ra lên cao, trong khi không có yếu tố nào trong top năm mang tính phản đối.

**So sánh hai lớp:** Cờ khoảng cách nhỏ tắt vì khoảng cách giữa hai lớp rất lớn. Tuy nhiên, sự chênh lệch lớn này không được coi là bảo đảm dự đoán chính xác tuyệt đối mà cần tiếp tục đối chiếu.

**Tổng hợp SHAP:** Trong top năm đặc trưng, IAT là yếu tố hỗ trợ mạnh nhất làm tăng giá trị đầu ra của lớp DDoS, trong khi không ghi nhận tác động phản đối nào từ nhóm này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, đóng góp lớn nhất vào việc nâng cao giá trị đầu ra cho lớp dự đoán.
- **Protocol Type**: Tác động này cùng chiều nhưng nhỏ hơn yếu tố dẫn đầu, đóng vai trò hỗ trợ bổ sung cho mô hình.
- **Magnitue**: Đặc trưng này mang lại mức đóng góp dương tương tự, củng cố thêm cho kết quả phân loại.
- **Min**: Sự hiện diện của giá trị này tiếp tục góp phần đẩy đầu ra tăng lên ở mức độ thấp hơn.
- **AVG**: Đây là đóng góp có tác động nhỏ nhất trong nhóm top năm, nhưng vẫn giữ xu hướng tăng cho lớp được giải thích.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu có địa chỉ và thời gian. Mục đích: Đối chiếu xem có hiện tượng lưu lượng dồn dập từ nhiều hướng hay không.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ, không tự đặt ngưỡng. Mục đích: Xem xét mức độ ảnh hưởng thực tế lên hệ thống trong điều kiện vận hành.

### Giới hạn do Gemini nêu

- Giá trị SHAP chỉ thể hiện mức độ đóng góp của đặc trưng vào đầu ra của mô hình đối với mẫu này, không chứng minh quan hệ nhân quả hay cuộc tấn công thực tế.
- Tổng các giá trị SHAP trong top năm chưa phải là toàn bộ mức thay đổi, phần còn lại đến từ các đặc trưng ngoài top năm.
- Xác suất dự đoán từ mô hình chưa được xác minh là đã hiệu chỉnh và không đại diện cho nhãn thật.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
