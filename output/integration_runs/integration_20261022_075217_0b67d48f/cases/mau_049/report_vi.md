## mau_049 — dòng CSV 48

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DoS**, xác suất **99.9953%**.
- Lớp đứng thứ hai: **DDoS**, xác suất **0.0034%**.
- Chênh lệch hai lớp: **99.9918 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 21.878189%.
- Tổng SHAP: +78.117067 điểm phần trăm; ngoài top 5: +2.383467 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 82925800 | +0.71359732 | +71.359732 |
| Protocol Type | 6 | +0.01652637 | +1.652637 |
| Number | 9.5 | +0.00957996 | +0.957996 |
| Magnitue | 10.392304 | +0.00927431 | +0.927431 |
| Weight | 141.55 | +0.00835804 | +0.835804 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu dữ liệu được mô hình dự đoán là lớp DoS với sự hỗ trợ mạnh mẽ từ đặc trưng IAT trong nhóm top năm. Trong khi đó, lớp DDoS xếp ở vị trí thứ hai nhưng có khoảng cách rất lớn về xác suất đầu ra so với lớp dẫn đầu.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt, cho thấy sự chênh lệch giữa lớp DoS đứng đầu và lớp DDoS đứng thứ hai là khá lớn nhưng không được xem là bảo đảm tuyệt đối cho độ chính xác của dự đoán.

**Tổng hợp SHAP:** Yếu tố IAT đóng góp mức hỗ trợ dương lớn nhất đẩy mạnh đầu ra của lớp dự đoán trong top năm, trong khi không ghi nhận tác động phản đối nào từ nhóm đặc trưng này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, mang lại mức tác động dương đáng kể làm tăng giá trị đầu ra của lớp được giải thích.
- **Protocol Type**: Đặc trưng này đóng vai trò hỗ trợ bổ sung cùng chiều với yếu tố dẫn đầu nhưng có độ lớn thấp hơn.
- **Number**: Sự hiện diện của đặc trưng này tiếp tục củng cố kết quả dự đoán thông qua một khoảng đóng góp dương nhỏ.
- **Magnitue**: Đặc trưng này tham gia hỗ trợ dự đoán với mức gia tăng điểm phần trăm ở mức trung bình trong nhóm.
- **Weight**: Đóng góp nhỏ nhất trong top năm nhưng vẫn duy trì xu hướng tác động cùng chiều để đẩy giá trị đầu ra lên.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký kết nối**: Kiểm tra kết nối lặp đến dịch vụ đích và nguồn liên quan nếu có metadata. Mục đích: Đối chiếu tần suất và đặc điểm kết nối mạng nhằm tìm kiếm các dấu hiệu liên quan đến lưu lượng bất thường.
- **Nhật ký tài nguyên dịch vụ**: Tìm lỗi, gián đoạn hoặc thay đổi tài nguyên cùng thời điểm để xác minh thêm. Mục đích: Xác định xem hệ thống có chịu ảnh hưởng về hiệu năng hay ghi nhận sự cố phần cứng/phần mềm nào tương ứng hay không.

### Giới hạn do Gemini nêu

- Các giá trị SHAP chỉ thể hiện mức độ đóng góp của đặc trưng đối với đầu ra của mô hình, không phải bằng chứng xác thực về mặt nhân quả hay sự tồn tại của một cuộc tấn công thực tế.
- Phạm vi phân tích chỉ giới hạn trong top năm đặc trưng của lớp được dự đoán và chưa phản ánh toàn bộ tác động từ các yếu tố còn lại.
- Xác suất dự đoán và các giá trị đầu ra chưa qua quá trình hiệu chỉnh chính thức nên chỉ mang tính tham khảo từ mô hình.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
