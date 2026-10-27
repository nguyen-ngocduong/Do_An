## mau_009 — dòng CSV 8

**Trạng thái Gemini: accepted**

Đạt kiểm tra bằng chứng có cấu trúc và quy tắc văn bản; chưa đánh giá ngữ nghĩa thủ công.

### Dự đoán và số liệu do chương trình dựng

- Model: `XGB_d4_n200`; dự đoán: **DDoS**, xác suất **99.9981%**.
- Lớp đứng thứ hai: **DoS**, xác suất **0.0011%**.
- Chênh lệch hai lớp: **99.9971 điểm phần trăm**.
- Quy tắc khoảng cách nhỏ: không quá 5 điểm phần trăm, chỉ để trình bày.
- Xác suất nền SHAP: 62.506627%.
- Tổng SHAP: +37.491501 điểm phần trăm; ngoài top 5: +3.192733 điểm phần trăm.
- Hỗ trợ mạnh nhất trong top 5: **IAT**.
- Phản đối mạnh nhất trong top 5: **Không có tác động âm trong top 5**.

| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |
|---|---:|---:|---:|
| IAT | 83089304 | +0.26644841 | +26.644841 |
| Protocol Type | 6 | +0.02782970 | +2.782970 |
| Magnitue | 10.392304 | +0.02663752 | +2.663752 |
| Min | 54 | +0.01170307 | +1.170307 |
| Number | 9.5 | +0.01036899 | +1.036899 |

![Biểu đồ SHAP](waterfall.png)

### Diễn giải Gemini

Mẫu được mô hình dự đoán là DDoS với xác suất rất cao vượt trội so với lớp đứng thứ hai là DoS. Đặc trưng IAT đóng vai trò hỗ trợ mạnh mẽ nhất, trong khi tất cả các đặc trưng trong top năm đều có chiều hướng tăng giá trị đầu ra.

**So sánh hai lớp:** Cờ khoảng cách nhỏ đang tắt do khoảng cách giữa hai lớp lớn, cho thấy mô hình phân định rõ ràng nhưng không coi đây là sự bảo đảm tuyệt đối về nhãn thật.

**Tổng hợp SHAP:** Trong top năm đặc trưng, IAT là yếu tố hỗ trợ mạnh nhất đẩy giá trị dự đoán lên cao, không có yếu tố nào mang chiều phản đối.

- **IAT**: Đây là yếu tố hỗ trợ nổi bật nhất trong top năm, đóng góp lớn nhất vào việc nâng cao giá trị đầu ra.
- **Protocol Type**: Tác động này cùng chiều nhưng có quy mô nhỏ hơn yếu tố dẫn đầu trong nhóm.
- **Magnitue**: Đóng góp dương mang tính bổ sung, góp phần củng cố thêm xu hướng dự đoán.
- **Min**: Yếu tố này mang lại mức tác động dương ở mức độ thấp hơn.
- **Number**: Đây là đóng góp dương nhỏ nhất trong nhóm top năm đặc trưng đang xem xét.

### Gợi ý kiểm tra có điều kiện

- **Nhật ký lưu lượng mạng**: Kiểm tra sự đồng thời của nhiều nguồn đến cùng dịch vụ nếu có địa chỉ và thời gian Mục đích: Đối chiếu hành vi lưu lượng thực tế phát sinh trong hệ thống.
- **Nhật ký tài nguyên dịch vụ**: Đối chiếu lưu lượng với tình trạng tài nguyên và khả năng phục vụ Mục đích: Đánh giá mức độ ảnh hưởng đến hạ tầng ứng dụng.

### Giới hạn do Gemini nêu

- Giá trị SHAP chỉ phản ánh mức độ đóng góp của đặc trưng đối với đầu ra của mô hình, không chứng minh quan hệ nhân quả.
- Xác suất dự đoán chưa được hiệu chỉnh chính thức và không thể coi là độ chính xác tuyệt đối.
- Phạm vi giải thích chỉ giới hạn trong top năm đặc trưng, chưa bao gồm toàn bộ tác động ngoại vi.

SHAP giải thích đầu ra model, chưa chứng minh hành vi tấn công hoặc quan hệ nhân quả. Đánh giá con người tạm hoãn.
