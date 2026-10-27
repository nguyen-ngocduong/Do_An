## mau_033 — dòng CSV 32

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +4.287097 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83330856 | +0.26278616 | +26.278616 |
| Magnitue | 10.392304 | +0.02045924 | +2.045924 |
| Protocol Type | 6 | +0.01890975 | +1.890975 |
| TCP | 1 | +0.01585590 | +1.585590 |
| Tot size | 54 | +0.01403300 | +1.403300 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mô hình dự đoán mẫu dữ liệu này thuộc lớp DDoS với xác suất rất cao, trong đó đặc trưng IAT đóng vai trò hỗ trợ nổi bật nhất làm tăng mạnh đầu ra so với nền tham chiếu. Lớp đứng thứ hai là DoS nhưng có khoảng cách xác suất rất lớn, cho thấy sự cạnh tranh không đáng kể giữa hai lớp dẫn đầu trong trường hợp này.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt vì chênh lệch xác suất giữa hai lớp đứng đầu rất lớn. Tuy nhiên, việc không có khoảng cách nhỏ không đồng nghĩa với việc đảm bảo dự đoán hoàn toàn chính xác mà chỉ phản ánh khoảng cách giá trị đầu ra tại thời điểm khảo sát.

**Tổng hợp SHAP:** Trong top năm đặc trưng, IAT là yếu tố hỗ trợ mạnh nhất đẩy giá trị dự đoán tăng lên. Không ghi nhận yếu tố nào có tác động phản đối mang giá trị âm trong nhóm này.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, góp phần đáng kể làm tăng giá trị đầu ra của lớp dự đoán.
- **Magnitue**: Tác động này cùng chiều nhưng có độ lớn nhỏ hơn rõ rệt so với yếu tố dẫn đầu.
- **Protocol Type**: Đóng góp mang chiều hướng bổ sung nhằm củng cố thêm cho kết quả phân loại của mô hình.
- **TCP**: Mang lại một mức tác động dương nhỏ hơn các đặc trưng phía trên trong nhóm năm phần tử.
- **Tot size**: Là yếu tố đóng góp theo chiều tăng có quy mô nhỏ nhất trong top năm đặc trưng được tổng hợp.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu hệ thống có ghi nhận địa chỉ và thời gian. Mục đích: Đối chiếu đặc tính lưu lượng thực tế với kết quả phân tích của mô hình.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ của hệ thống. Mục đích: Xác minh các biến động tài nguyên đi kèm với hành vi mạng được ghi nhận.

### Giới hạn do Gemini nêu

- Các giá trị SHAP chỉ thể hiện mức độ đóng góp của đặc trưng vào đầu ra của mô hình đối với mẫu hiện tại chứ không chứng minh quan hệ nhân quả ngoài thực tế.
- Xác suất dự đoán của mô hình chưa được kiểm chứng về độ hiệu chỉnh và không đại diện cho nhãn thực tế của dữ liệu.
- Phạm vi giải thích chỉ giới hạn trong top năm đặc trưng và phần dư còn lại, chưa phản ánh toàn bộ cấu trúc phức tạp bên trong mô hình.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
