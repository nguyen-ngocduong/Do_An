# Hà Minh Hải — 03: Giải thích toàn cục, cục bộ và ca điển hình

- **Phụ trách:** Hà Minh Hải.
- **Phụ thuộc:** Hải 02; model và dự đoán validation của Dương.
- **Trạng thái ngày 08/10/2026:** chưa có bằng chứng hoàn thành.
- **Phạm vi:** phân loại có giám sát 8 lớp; dữ liệu và huấn luyện chạy trên Kaggle.

## Công việc

- [ ] Cố định mẫu giải thích, background từ train nếu cần, sample ID/seed và support; công bố phương pháp lấy mẫu.
- [ ] Sinh biểu đồ mean absolute SHAP theo từng lớp và tổng hợp; giải thích cách gộp lớp và giới hạn mẫu đại diện.
- [ ] Chọn khoảng 12–20 ca đúng/sai thực tế: Normal, lớp hiếm, các nhóm tấn công và cặp lớp hay nhầm; không dựng lỗi giả.
- [ ] Mỗi ca lưu true/predicted label, xác suất, lớp giải thích, feature values, baseline và đóng góp gắn đúng model/run.
- [ ] Đối chiếu SHAP/LIME trên cùng mẫu/lớp; phân tích khác biệt và fidelity, không yêu cầu thứ hạng giống nhau.
- [ ] Diễn giải feature quan trọng dựa trên định nghĩa/đơn vị phối hợp Dương; ghi giới hạn tương quan, không suy ra quan hệ nhân quả.
- [ ] Viết phân tích ca điển hình và phần phương pháp 3.4; bàn giao hình/dữ liệu giải thích cho Kiên.

## Đầu ra và nghiệm thu

Biểu đồ toàn cục/cục bộ, bộ ca đúng/sai có truy vết và phân tích đặc trưng có ảnh hưởng.

## Bằng chứng và giới hạn

Chưa có dự đoán mô hình hoặc kết quả XAI để tick.

## Bước tiếp theo

Hải 04 sau khi model và quy tắc chọn ca cuối được đóng băng.
