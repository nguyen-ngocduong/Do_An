## mau_028 — dòng CSV 27

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DoS**, xác suất **99.9953%**.
- Lớp đứng thứ hai: **DDoS**, xác suất **0.0034%**.
- Chênh lệch hai lớp: **99.9918 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 21.878189%.
- Tổng SHAP: +78.117067 điểm phần trăm; ngoài top 5: +1.681811 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 82977024 | +0.72261263 | +72.261263 |
| Weight | 141.55 | +0.01225674 | +1.225674 |
| Protocol Type | 6 | +0.01047777 | +1.047777 |
| Number | 9.5 | +0.01020363 | +1.020363 |
| AVG | 54 | +0.00880178 | +0.880178 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu dữ liệu được phân loại là DoS với sự đóng góp mạnh mẽ từ đặc trưng IAT trong top năm đặc trưng. Khoảng cách giữa lớp DoS và lớp đứng thứ hai là rất lớn, cho thấy mức độ tập trung cao của mô hình vào dự đoán này.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt do chênh lệch xác suất giữa lớp DoS và lớp DDoS khá lớn. Tuy nhiên, việc không có khoảng cách nhỏ không bảo đảm dự đoán chắc chắn đúng, vì đây chỉ là kết quả suy luận từ mô hình.

**Tổng hợp SHAP:** Trong nhóm năm đặc trưng hàng đầu, IAT là yếu tố hỗ trợ mạnh mẽ nhất làm tăng đầu ra của lớp dự đoán. Không có đặc trưng nào trong top năm mang lại tác động âm để phản đối kết quả này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần đẩy mạnh đầu ra của lớp được giải thích.
- **Weight**: Tác động này cùng chiều nhưng nhỏ hơn yếu tố dẫn đầu trong nhóm.
- **Protocol Type**: Đóng vai trò hỗ trợ bổ sung với mức ảnh hưởng dương vừa phải.
- **Number**: Ghi nhận thêm một đóng góp dương nhỏ nhằm củng cố kết quả dự đoán.
- **AVG**: Đặc trưng này mang lại tác động dương ở mức thấp nhất trong top năm đặc trưng.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký kết nối**: Kiểm tra kết nối lặp đến dịch vụ đích và nguồn liên quan nếu có metadata. Mục đích: Đối chiếu xem có hiện tượng kết nối bất thường hay lặp lại trên hệ thống hay không nếu log này tồn tại.
- **Nhật ký tài nguyên dịch vụ**: Tìm lỗi, gián đoạn hoặc thay đổi tài nguyên cùng thời điểm để xác minh thêm. Mục đích: Xác định xem hệ thống có ghi nhận sự cố tài nguyên tương ứng với thời điểm của mẫu hay không nếu log này tồn tại.

### Giới hạn do Gemini nêu

- Các giá trị SHAP chỉ giải thích đầu ra của mô hình đối với mẫu hiện tại và không chứng minh được quan hệ nhân quả hay sự tồn tại của một cuộc tấn công thực tế.
- Xác suất dự đoán chưa được hiệu chỉnh chính thức và không phản ánh độ tin cậy tuyệt đối của nhãn.
- Phạm vi giải thích chỉ giới hạn ở top năm đặc trưng và phần còn lại ngoài top, chưa bao hàm toàn bộ không gian dữ liệu.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
