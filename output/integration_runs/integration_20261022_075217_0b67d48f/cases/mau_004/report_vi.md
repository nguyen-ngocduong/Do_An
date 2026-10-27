## mau_004 — dòng CSV 3

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491513 điểm phần trăm; ngoài top 5: +2.355845 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83094080 | +0.28494729 | +28.494729 |
| Protocol Type | 6 | +0.02960885 | +2.960885 |
| Min | 54 | +0.01661683 | +1.661683 |
| Number | 9.5 | +0.01101139 | +1.101139 |
| Tot size | 54 | +0.00917232 | +0.917232 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu dữ liệu được mô hình dự đoán là lớp DDoS với xác suất rất cao, trong đó đặc trưng IAT đóng vai trò hỗ trợ mạnh mẽ nhất. Khoảng cách giữa lớp đứng đầu và lớp đứng thứ hai là rất lớn, cho thấy sự áp đảo rõ rệt của lớp dự đoán trong trường hợp này.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt, thể hiện sự chênh lệch lớn giữa lớp DDoS và lớp đứng thứ hai là DoS. Tuy nhiên, mức chênh lệch cao này không được xem là sự bảo đảm tuyệt đối về tính chính xác của dự đoán.

**Tổng hợp SHAP:** Trong top năm đặc trưng, IAT là yếu tố hỗ trợ mạnh nhất làm tăng đầu ra của lớp dự đoán, trong khi không ghi nhận bất kỳ tác động phản đối nào từ các đặc trưng còn lại.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, đóng góp lớn vào việc đẩy giá trị đầu ra của lớp được giải thích.
- **Protocol Type**: Tác động này cùng chiều với yếu tố dẫn đầu nhưng mang lại mức hỗ trợ bổ sung ở quy mô nhỏ hơn.
- **Min**: Đặc trưng này thể hiện một hướng đóng góp dương tiếp theo nhằm củng cố kết quả phân loại của mô hình.
- **Number**: Sự hiện diện của đặc trưng này tiếp tục tạo ra một lực đẩy dương nhỏ hơn để nâng cao đầu ra.
- **Tot size**: Đây là yếu tố có tác động nhỏ nhất trong nhóm năm đặc trưng hàng đầu nhưng vẫn duy trì xu hướng hỗ trợ.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu hệ thống có ghi nhận địa chỉ và thời gian. Mục đích: Đối chiếu sự biến động lưu lượng để xác thực thêm bối cảnh ghi nhận của mẫu.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ của hệ thống. Mục đích: Kiểm tra mức độ đáp ứng và trạng thái hoạt động thực tế nhằm phục vụ việc phân tích đối chiếu.

### Giới hạn do Gemini nêu

- Kết quả SHAP chỉ giải thích giá trị đầu ra của mô hình cho mẫu hiện tại và không thể dùng để chứng minh quan hệ nhân quả hay sự tồn tại của một cuộc tấn công thực tế.
- Xác suất dự đoán của mô hình chưa được kiểm chứng hay hiệu chỉnh để đảm bảo độ tin cậy tuyệt đối.
- Phạm vi phân tích chỉ giới hạn trong top năm đặc trưng được cung cấp và không đại diện cho toàn bộ các yếu tố bên ngoài.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
