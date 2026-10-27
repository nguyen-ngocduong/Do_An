# CICIoT2023: Stacking, SHAP và Gemini

Bộ kết quả hiện tại dùng Decision Tree, Random Forest và HistGradientBoosting làm base models; XGBoost `XGB_d4_n200` làm meta-model. SHAP giải thích dự đoán của toàn bộ pipeline, sau đó Gemini tạo diễn giải bằng tiếng Việt.

Kết quả chốt để bàn giao cho Kiên là **`integration_20261022_075217_0b67d48f`**: đã dự đoán, tính SHAP và tạo diễn giải đạt kiểm tra tự động cho 50/50 mẫu. Xem [bộ kết quả và cách lấy model](output/README.md).

Các notebook theo thứ tự sử dụng:

1. [EDA](notebook/ciciot2023-do-an.ipynb).
2. [Processing](notebook/ciciot2023-do-an-processing.ipynb): giữ phân chia train/validation/test có sẵn, xử lý trùng và cố định 5 fold trong train.
3. [Stacking](notebook/ciciot2023-do-an-stacking.ipynb): tạo OOF và huấn luyện base models.
4. [XGBoost meta-model](notebook/ciciot2023-do-an-stacking-xgboost-meta.ipynb): tái sử dụng OOF/base models, chọn cấu hình theo validation.
5. [SHAP](notebook/ciciot2023-do-an-shap.ipynb): giải thích 16 ca và lưu background dùng lại.
6. [SHAP → Gemini](notebook/ciciot2023-do-an-shap-gemini.ipynb): xây dựng diễn giải tiếng Việt và kiểm tra phản hồi.
7. [Tích hợp CSV → dự đoán → SHAP → Gemini](notebook/ciciot2023-do-an-integration.ipynb): đã chạy thử 50 mẫu trên Kaggle.

Processing và training chạy trên Kaggle. Dùng đúng phiên bản thư viện và thứ tự đặc trưng/lớp ghi trong protocol của run được chọn. Không lưu API key trong notebook; sử dụng Kaggle Secrets hoặc biến môi trường khi chuyển sang local.

Công việc tiếp theo của Kiên là tách pipeline đã kiểm chứng thành các module Python trên local, nạp model/background một lần và đối chiếu CSV golden trước khi xây dựng API/giao diện. Phần này chưa được triển khai trong bộ kết quả hiện tại; human review đang được tạm hoãn theo phạm vi đã chốt.
