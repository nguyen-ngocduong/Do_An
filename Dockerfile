# syntax=docker/dockerfile:1
# Một Dockerfile tạo ba image bằng --target backend, frontend hoặc gateway.
# Build tại thư mục gốc repo để COPY tìm được BE/, FE/ và output/.

# 1. Backend: Python cùng major/minor với môi trường tạo bundle đã đóng băng.
FROM python:3.13-slim-bookworm AS backend
# Không ghi __pycache__; xuất log ngay để docker compose logs đọc được.
# Cache biểu đồ/JIT ở /tmp, không ghi vào artifact model nguồn.
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MPLCONFIGDIR=/tmp/matplotlib NUMBA_CACHE_DIR=/tmp/numba
WORKDIR /app
# Thư viện hệ thống cho OpenMP/C++, HTTPS và font biểu đồ.
# Xóa danh sách apt sau cài đặt để giảm dung lượng layer.
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 libstdc++6 ca-certificates fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
# COPY lock trước source: sửa code không buộc cài lại toàn bộ dependencies.
# Giữ đúng phiên bản để giải tuần tự hóa model sklearn/XGBoost và đối chiếu golden.
COPY BE/requirements-lock.txt /tmp/requirements-lock.txt
RUN pip install --no-cache-dir -r /tmp/requirements-lock.txt
# Chỉ đưa module BE vào image; không mang .env, tests hoặc runtime máy cá nhân.
COPY BE/*.py /app/BE/
# Nhóm model: metadata/checksum, helper suy luận và bundle XGB_d4_n200.
# Bundle chứa cả tiền xử lý, base models DT/RF/HGB và meta-model XGBoost.
# Các run ID cố định giúp giữ đúng nguồn artifact đã nghiệm thu.
COPY output/stacking_meta_runs/xgb_meta_20261021_092334_9024562d/output_checksums.json /app/output/stacking_meta_runs/xgb_meta_20261021_092334_9024562d/output_checksums.json
COPY output/stacking_meta_runs/xgb_meta_20261021_092334_9024562d/protocol.json /app/output/stacking_meta_runs/xgb_meta_20261021_092334_9024562d/protocol.json
COPY output/stacking_meta_runs/xgb_meta_20261021_092334_9024562d/frozen_candidates.json /app/output/stacking_meta_runs/xgb_meta_20261021_092334_9024562d/frozen_candidates.json
COPY output/stacking_meta_runs/xgb_meta_20261021_092334_9024562d/run_status.json /app/output/stacking_meta_runs/xgb_meta_20261021_092334_9024562d/run_status.json
COPY output/stacking_meta_runs/xgb_meta_20261021_092334_9024562d/predict_csv.py /app/output/stacking_meta_runs/xgb_meta_20261021_092334_9024562d/predict_csv.py
COPY output/stacking_meta_runs/xgb_meta_20261021_092334_9024562d/frozen_models/XGB_d4_n200.joblib /app/output/stacking_meta_runs/xgb_meta_20261021_092334_9024562d/frozen_models/XGB_d4_n200.joblib
# Nhóm SHAP: background, thứ tự đặc trưng/lớp và dữ liệu golden để kiểm tra startup.
COPY output/xai_shap_runs/shap_20261022_021654_2555e479/output_checksums.json /app/output/xai_shap_runs/shap_20261022_021654_2555e479/output_checksums.json
COPY output/xai_shap_runs/shap_20261022_021654_2555e479/protocol.json /app/output/xai_shap_runs/shap_20261022_021654_2555e479/protocol.json
COPY output/xai_shap_runs/shap_20261022_021654_2555e479/run_status.json /app/output/xai_shap_runs/shap_20261022_021654_2555e479/run_status.json
COPY output/xai_shap_runs/shap_20261022_021654_2555e479/background.npy /app/output/xai_shap_runs/shap_20261022_021654_2555e479/background.npy
COPY output/xai_shap_runs/shap_20261022_021654_2555e479/background_probabilities.csv /app/output/xai_shap_runs/shap_20261022_021654_2555e479/background_probabilities.csv
COPY output/xai_shap_runs/shap_20261022_021654_2555e479/model_reference.json /app/output/xai_shap_runs/shap_20261022_021654_2555e479/model_reference.json
COPY output/xai_shap_runs/shap_20261022_021654_2555e479/selected_input.csv /app/output/xai_shap_runs/shap_20261022_021654_2555e479/selected_input.csv
COPY output/xai_shap_runs/shap_20261022_021654_2555e479/golden_predictions.csv /app/output/xai_shap_runs/shap_20261022_021654_2555e479/golden_predictions.csv
# Nhóm tích hợp: hợp đồng CSV và prompt/schema/hướng dẫn Gemini.
# Chỉ COPY các tệp cần chạy, giữ nguyên byte và checksum nguồn.
COPY output/integration_runs/integration_20261022_075217_0b67d48f/output_checksums.json /app/output/integration_runs/integration_20261022_075217_0b67d48f/output_checksums.json
COPY output/integration_runs/integration_20261022_075217_0b67d48f/protocol.json /app/output/integration_runs/integration_20261022_075217_0b67d48f/protocol.json
COPY output/integration_runs/integration_20261022_075217_0b67d48f/input_schema.json /app/output/integration_runs/integration_20261022_075217_0b67d48f/input_schema.json
COPY output/integration_runs/integration_20261022_075217_0b67d48f/system_prompt.txt /app/output/integration_runs/integration_20261022_075217_0b67d48f/system_prompt.txt
COPY output/integration_runs/integration_20261022_075217_0b67d48f/generation_config.json /app/output/integration_runs/integration_20261022_075217_0b67d48f/generation_config.json
COPY output/integration_runs/integration_20261022_075217_0b67d48f/check_guide.json /app/output/integration_runs/integration_20261022_075217_0b67d48f/check_guide.json
# BE chạy bằng UID10001, không phải root. Chỉ runtime cần quyền ghi.
# Compose gắn named volume vào runtime để dữ liệu còn sau khi tạo lại container.
RUN useradd --uid 10001 --create-home nidr && mkdir -p /app/BE/runtime && chown nidr:nidr /app/BE/runtime
USER nidr
# EXPOSE chỉ mô tả cổng trong image; không tự mở cổng lên máy chủ.
EXPOSE 8000
# HTTP chỉ dùng trong mạng Compose; lệnh BE chạy LAN thông thường vẫn yêu cầu TLS.
# Một worker để dùng chung model, SQLite, hàng đợi và phiên đăng nhập.
# 0.0.0.0 là bên trong container; Compose không publish cổng BE.
# Cho BE thời gian dừng tác vụ; Compose chờ tối đa 120 giây trước khi buộc dừng.
CMD ["python", "-m", "uvicorn", "BE.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--timeout-graceful-shutdown", "100"]

# 2. Giai đoạn build FE: có dependencies phục vụ biên dịch.
# API_PROXY_TARGET là địa chỉ nội bộ; gateway thực tế chuyển API thẳng tới BE.
FROM node:22-bookworm-slim AS frontend-build
WORKDIR /build
ENV NEXT_TELEMETRY_DISABLED=1 API_PROXY_TARGET=http://backend:8000
# npm ci cài theo package-lock, thay vì tự chọn phiên bản mới.
COPY FE/package.json FE/package-lock.json ./
RUN npm ci
COPY FE/ ./
# Build production; postbuild đóng gói static assets/font vào standalone.
RUN npm run build

# Image FE chạy thực tế chỉ lấy standalone, không mang toàn bộ môi trường build.
FROM node:22-bookworm-slim AS frontend
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0 PORT=3000
COPY --from=frontend-build --chown=node:node /build/.next/standalone ./
# Dùng user node có sẵn trong image, chạy server production thay vì npm run dev.
USER node
EXPOSE 3000
CMD ["node", "server.js"]

# 3. Gateway: điểm truy cập duy nhất của trình duyệt, định tuyến FE/API.
# Mặc định dùng HTTP localhost; overlay production mount cấu hình HTTPS thay thế.
FROM nginx:1.28-alpine AS gateway
COPY deploy/docker/nginx.conf /etc/nginx/nginx.conf
# Cổng nội bộ: 8080 HTTP, 8443 HTTPS khi bật cấu hình VPS.
EXPOSE 8080 8443

# 4. Kafka adapters: gọi BE qua HTTP, không mang model hoặc môi trường khoa học dữ liệu.
FROM python:3.13-slim-bookworm AS streaming
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY streaming/requirements.txt /tmp/streaming-requirements.txt
RUN pip install --no-cache-dir -r /tmp/streaming-requirements.txt
COPY streaming/*.py /app/streaming/
# Producer kiểm schema độc lập khi BE tạm dừng; không COPY model/trọng số vào adapter.
COPY output/integration_runs/integration_20261022_075217_0b67d48f/input_schema.json /app/streaming/input_schema.json
RUN useradd --uid 10001 --create-home nidr && mkdir /state && chown nidr:nidr /state
USER nidr
CMD ["python", "-m", "streaming.consumer"]
