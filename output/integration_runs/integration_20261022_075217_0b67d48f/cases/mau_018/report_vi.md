## mau_018 — dòng CSV 17

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +3.216975 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83349160 | +0.28058629 | +28.058629 |
| Magnitue | 10.392304 | +0.02463178 | +2.463178 |
| Protocol Type | 6 | +0.01632291 | +1.632291 |
| Tot size | 54 | +0.01083319 | +1.083319 |
| Number | 9.5 | +0.01037110 | +1.037110 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu dữ liệu thuộc lớp DDoS với sự hỗ trợ nổi bật từ đặc trưng IAT trong top năm đặc trưng quan trọng. Khoảng cách giữa lớp đứng đầu và lớp đứng thứ hai khá lớn, thể hiện sự chênh lệch rõ rệt trong kết quả phân loại.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt, cho thấy sự chênh lệch lớn giữa lớp đứng đầu và lớp đứng thứ hai. Tuy nhiên, mức chênh lệch lớn này không được coi là sự bảo đảm tuyệt đối cho độ chính xác của dự đoán.

**Tổng hợp SHAP:** Trong top năm đặc trưng được phân tích, IAT đóng vai trò hỗ trợ mạnh mẽ nhất làm tăng giá trị đầu ra của lớp DDoS, trong khi không có đặc trưng nào trong nhóm này tạo ra tác động phản đối mang giá trị âm.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần đáng kể làm tăng đầu ra của lớp dự đoán.
- **Magnitue**: Tác động này cùng chiều nhưng nhỏ hơn yếu tố dẫn đầu, đóng vai trò hỗ trợ bổ sung cho kết quả phân loại.
- **Protocol Type**: Đặc trưng này thể hiện xu hướng đóng góp dương, tiếp tục củng cố thêm cho đầu ra của mô hình.
- **Tot size**: Sự hiện diện của đặc trưng này mang lại một mức tác động dương nhỏ hơn trong nhóm.
- **Number**: Đây là thành phần có đóng góp dương ở mức độ thấp nhất trong số năm đặc trưng hàng đầu được xem xét.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu hệ thống có ghi nhận địa chỉ và thời gian. Mục đích: Đối chiếu hành vi lưu lượng thực tế với kết quả dự đoán của mô hình.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ của hệ thống dựa trên dữ liệu nhật ký sẵn có. Mục đích: Kiểm tra mức độ ảnh hưởng đến tài nguyên hệ thống nhằm phục vụ công tác rà soát.

### Giới hạn do Gemini nêu

- Kết quả giải thích này chỉ phản ánh đầu ra của mô hình đối với mẫu dữ liệu hiện tại và không chứng minh được quan hệ nhân quả hay sự tồn tại của một cuộc tấn công thực tế.
- Giá trị xác suất từ mô hình chưa được kiểm chứng về độ hiệu chỉnh và các giá trị SHAP chỉ thuộc về lớp được dự đoán.
- Tổng các đặc trưng trong top năm chưa bao trùm toàn bộ sự thay đổi, phần còn lại được đóng góp bởi các đặc trưng ngoài top.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
