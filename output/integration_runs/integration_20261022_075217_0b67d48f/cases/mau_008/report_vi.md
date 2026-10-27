## mau_008 — dòng CSV 7

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +3.551705 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83150040 | +0.28293688 | +28.293688 |
| Min | 42 | +0.02066006 | +2.066006 |
| Protocol Type | 1 | +0.01209792 | +1.209792 |
| Tot size | 42 | +0.01192357 | +1.192357 |
| Magnitue | 9.1651516 | +0.01177952 | +1.177952 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu được dự đoán là lớp DDoS với xác suất rất cao, trong đó đặc trưng IAT đóng vai trò hỗ trợ mạnh mẽ nhất và không có yếu tố phản đối nào trong nhóm hàng đầu. Khoảng cách với lớp đứng thứ hai là DoS rất lớn, cho thấy sự áp đảo rõ rệt của lớp dự đoán trong lần phân loại này.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt, cho thấy sự chênh lệch lớn giữa hai đầu ra. Tuy nhiên, điều này không được coi là bảo đảm dự đoán chính xác và không xác định nhãn thật.

**Tổng hợp SHAP:** Đặc trưng IAT là yếu tố hỗ trợ mạnh nhất làm tăng đầu ra của lớp DDoS, trong khi không có yếu tố nào trong top năm mang giá trị âm để phản đối kết quả này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, đóng góp lớn nhất vào việc đẩy giá trị đầu ra của lớp được giải thích.
- **Min**: Tác động này mang chiều hướng hỗ trợ bổ sung cho lớp dự đoán nhưng ở mức nhỏ hơn nhiều so với yếu tố dẫn đầu.
- **Protocol Type**: Đặc trưng này cung cấp thêm một đóng góp dương nhằm củng cố kết quả phân loại hiện tại.
- **Tot size**: Sự hiện diện của giá trị này tiếp tục đẩy nhẹ điểm số đầu ra của mô hình về phía lớp DDoS.
- **Magnitue**: Đây là tác động có độ lớn thấp nhất trong nhóm năm đặc trưng hàng đầu nhưng vẫn duy trì xu hướng hỗ trợ.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu có địa chỉ và thời gian. Mục đích: Đối chiếu sự xuất hiện đồng thời từ nhiều nguồn nhằm phục vụ công tác phân tích lưu lượng.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ, không tự đặt ngưỡng. Mục đích: Đánh giá mức độ ảnh hưởng của lưu lượng đối với hệ thống mà không đưa ra kết luận về hành vi tấn công thực tế.

### Giới hạn do Gemini nêu

- Đây là giải thích đầu ra mô hình, không chứng minh cuộc tấn công thực tế hoặc quan hệ nhân quả.
- Giá trị SHAP chỉ phản ánh tác động đến lớp được dự đoán và chưa bao gồm toàn bộ phần còn lại ngoài top năm.
- Xác suất dự đoán từ mô hình chưa được xác minh là đã hiệu chỉnh và không bảo đảm tuyệt đối.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
