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

[Xuất test thành CSV upload NIDR](notebook/ciciot2023-do-an-test-upload-csv.ipynb): chạy trên Kaggle với output processing `20261021_052521_96f61f19`; chỉ lấy test đã chuẩn bị, giữ 46 đặc trưng thang đo gốc để BE tự transform. Mỗi CSV tối đa 1.000 dòng / 10 MiB, có thể kèm `label`, có kiểm checksum nguồn và đọc lại CSV. Notebook chưa được thực thi với tập test thật trên Kaggle; các kiểm tra local chỉ dùng dữ liệu tổng hợp.

Processing và training chạy trên Kaggle. Dùng đúng phiên bản thư viện và thứ tự đặc trưng/lớp ghi trong protocol của run được chọn. Không lưu API key trong notebook; sử dụng Kaggle Secrets hoặc biến môi trường khi chuyển sang local.

Backend local đã được tách trong [BE/](BE/README.md): REST API FastAPI, Swagger, CSV batch/phát lại, SHAP và module Gemini. Model/background nạp một lần và có đối chiếu CSV golden khi khởi động. [Frontend NIDR](FE/README.md) nằm riêng trong `FE/`, gọi REST API trên cùng server; đánh giá thủ công từng mẫu có thể lưu, mở lại và tải về. Xem [kiểm chứng BE](BE/VERIFICATION.md) và [kiểm chứng FE](FE/VERIFICATION.md).

BE chạy từ repo root bằng `.venv/bin/python -m BE`; Swagger ở `http://127.0.0.1:8000/docs`. FE dùng **Next.js App Router + React + TypeScript**, cấu trúc theo P-150: từ `FE/` chạy Node.js 22, `npm ci`, rồi `npm run dev -- --hostname 127.0.0.1 --port 3000`. Mở `http://127.0.0.1:3000/login`, dùng tài khoản BE hiện có (BE 1.4.0); phiên cookie tối đa tám giờ, có nút Đăng xuất. Tài khoản và Gemini key chỉ cấu hình ở `BE/.env`. [Hướng dẫn FE](FE/README.md) và [gateway HTTPS một server](FE/deploy/README.md) ghi cách chạy production.

## Chạy bằng Docker

Bộ Docker NIDR gồm backend có sẵn model, Next.js production và Nginx; chạy CPU trên Windows/Linux amd64. Xem [hướng dẫn bàn giao](deploy/docker/README.md), [kế hoạch đã chốt](docs-md/PLAN_DOCKER_NIDR.md) và [kiểm chứng Docker](deploy/docker/VERIFICATION.md). Người nhận dùng archive image và Compose, không cần source/model rời. Producer dựng gói mới bằng `python scripts/package_docker.py --version 1.0.0`; archive nằm trong `dist/` (không commit). Không đưa .env, Gemini key hoặc BE/runtime vào image.

Tùy chọn [Kafka local + Langfuse Cloud + Netdata local](deploy/observability/README.md) dùng overlay `docker-compose.observability.yml`. Producer phát CSV từ `upload/`, consumer staging bền vững và gọi BE với khóa chống trùng; kết quả vẫn hiện trong NIDR. Không bật Grafana/Prometheus; Airflow để sau. Xem [kế hoạch triển khai](deploy/observability/PLAN.md).
