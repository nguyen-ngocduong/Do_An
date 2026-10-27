## mau_006 — dòng CSV 5

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491513 điểm phần trăm; ngoài top 5: +2.746824 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83076176 | +0.26778991 | +26.778991 |
| Magnitue | 10.392304 | +0.02972431 | +2.972431 |
| Tot size | 54 | +0.02012855 | +2.012855 |
| Protocol Type | 6 | +0.01855630 | +1.855630 |
| Min | 54 | +0.01124783 | +1.124783 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu dữ liệu thuộc lớp DDoS với xác suất rất cao, trong đó đặc trưng IAT đóng vai trò hỗ trợ nổi bật nhất. Khoảng cách giữa lớp DDoS và lớp đứng thứ hai là DoS rất lớn, cho thấy không có sự cạnh tranh đáng kể trong trường hợp này.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt, thể hiện chênh lệch lớn giữa hai đầu ra nhưng không coi đây là bảo đảm tuyệt đối cho dự đoán đúng.

**Tổng hợp SHAP:** Trong top năm đặc trưng, IAT là yếu tố hỗ trợ mạnh nhất đẩy giá trị đầu ra lên, trong khi không có yếu tố nào mang giá trị âm trong nhóm này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm đối với lớp được dự đoán.
- **Magnitue**: Tác động này cùng chiều nhưng có mức đóng góp nhỏ hơn yếu tố dẫn đầu.
- **Tot size**: Đặc trưng này duy trì xu hướng hỗ trợ bổ sung cho kết quả phân loại.
- **Protocol Type**: Sự góp mặt của đặc trưng này mang lại thêm một phần tác động dương nhỏ hơn.
- **Min**: Đây là yếu tố có đóng góp dương thấp nhất trong số năm đặc trưng hàng đầu.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu có địa chỉ và thời gian Mục đích: Đối chiếu sự xuất hiện đồng thời của các nguồn lưu lượng.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ, không tự đặt ngưỡng Mục đích: Kiểm tra tương quan giữa lưu lượng và trạng thái tài nguyên hệ thống.

### Giới hạn do Gemini nêu

- Giải thích SHAP chỉ phản ánh đầu ra của mô hình đối với mẫu hiện tại, không chứng minh quan hệ nhân quả hay sự tồn tại của tấn công thực tế.
- Xác suất của mô hình chưa được kiểm chứng hiệu chuẩn và không thể coi là độ chắc chắn tuyệt đối.
- Tổng giá trị SHAP trong top năm chưa bao trùm toàn bộ các thành phần thay đổi từ giá trị nền tham chiếu.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
