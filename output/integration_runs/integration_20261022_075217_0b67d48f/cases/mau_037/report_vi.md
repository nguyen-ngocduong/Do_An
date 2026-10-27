## mau_037 — dòng CSV 36

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +2.493733 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83128120 | +0.28778067 | +28.778067 |
| Protocol Type | 1 | +0.02825649 | +2.825649 |
| Tot size | 42 | +0.01165286 | +1.165286 |
| Number | 9.5 | +0.01137287 | +1.137287 |
| Magnitue | 9.1651516 | +0.01091479 | +1.091479 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu được mô hình dự đoán là lớp DDoS với các yếu tố hỗ trợ chủ yếu từ đặc trưng IAT và Protocol Type. Sự chênh lệch giữa lớp đứng đầu và lớp đứng thứ hai là rất lớn.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt, cho thấy sự chênh lệch lớn giữa hai đầu ra. Tuy nhiên, điều này không bảo đảm dự đoán là đúng hoàn toàn mà cần tiếp tục đối chiếu.

**Tổng hợp SHAP:** Trong năm đặc trưng hàng đầu, IAT đóng vai trò hỗ trợ mạnh nhất đẩy giá trị đầu ra lên, trong khi không ghi nhận tác động phản đối nào từ nhóm này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, đóng góp tích cực lớn vào đầu ra của lớp.
- **Protocol Type**: Tác động này cùng chiều nhưng nhỏ hơn yếu tố dẫn đầu, đóng vai trò hỗ trợ bổ sung.
- **Tot size**: Ghi nhận mức tác động dương nhỏ hơn, tiếp tục củng cố kết quả dự đoán của mô hình.
- **Number**: Đặc trưng này mang lại một lực đẩy dương nhỏ trong nhóm năm yếu tố quan trọng.
- **Magnitue**: Đóng góp tác động dương thấp nhất trong top năm, kết hợp cùng các yếu tố khác để tạo ra kết quả.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu hệ thống có ghi nhận địa chỉ và thời gian. Mục đích: Đối chiếu hành vi lưu lượng thực tế để hỗ trợ việc phân tích.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ. Mục đích: Xác minh khả năng đáp ứng hệ thống và kiểm tra ngữ cảnh vận hành.

### Giới hạn do Gemini nêu

- Giải thích này phản ánh đầu ra của mô hình và không chứng minh quan hệ nhân quả hay sự tồn tại của cuộc tấn công thực tế.
- Giá trị SHAP chỉ thể hiện sự đóng góp tương đối trong top năm đặc trưng, không đại diện cho toàn bộ các yếu tố của hệ thống.
- Xác suất của mô hình chưa được xác minh là đã hiệu chỉnh và không thể coi là độ chắc chắn tuyệt đối.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
