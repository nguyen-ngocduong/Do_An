# Backend CICIoT2023 — REST API, SHAP và Gemini

Cập nhật **04/11/2026, API 1.7.0**: `GET /api/dashboard` tổng hợp từ SQLite và artifact SHAP đã lưu. Endpoint có xác thực, nhận `period=today|7d|30d|all` (mặc định 7d) và `run_id` tùy chọn. Ngày theo Asia/Ho_Chi_Minh (UTC+7); mẫu được lọc theo thời gian server dự đoán. Cảnh báo, diễn giải và phiếu đánh giá là trạng thái hiện tại của nhóm mẫu đó. Run mới hoặc run có mẫu xử lý trong khoảng chọn được tính là có hoạt động.

Dashboard trả bốn KPI, tám lớp, số mẫu theo ngày, cảnh báo/run gần nhất, trạng thái XAI/Gemini và phiếu đánh giá. Toàn lịch sử giữ biểu đồ 30 ngày gần nhất và trả trường ngày riêng để FE nêu rõ. Danh sách chọn run giữ 100 run gần nhất, kèm metadata của run đang chọn dù cũ hơn. Diễn giải/phiếu lấy mức Kỹ thuật; SHAP dùng chung đếm một lần theo cặp run/dòng có `explanation.json`, kể cả Gemini lỗi. Tỷ lệ nghi vấn là null khi mẫu số bằng 0. Số phiếu đã lưu không xác minh tư cách chuyên gia hoặc độ mới của bằng chứng.

Các truy vấn đọc cùng SQLite snapshot; chỉ kiểm tra tồn tại tệp SHAP của các mẫu từng yêu cầu giải thích, không suy luận hoặc gọi Gemini. Chi phí đọc artifact tăng theo số mẫu đã giải thích trong phạm vi chọn. Cần BE 1.7.0 để nhận endpoint mới; FE mở `/dashboard` khi đăng nhập không có đích riêng.

Backend chạy trên một server bằng FastAPI. Swagger UI cho phép thử toàn bộ luồng mà chưa cần frontend. Model và background được nạp một lần; tiền xử lý/model đã fit được tái sử dụng nguyên từ artifact Kaggle.

Mã nguồn BE nằm trong `BE/`, thực hiện trên nhánh `duong`. [Frontend NIDR](../FE/README.md) nằm riêng trong `FE/`, dùng Next.js tại cổng 3000. Một server triển khai dùng Nginx làm cổng HTTPS cho cả FE/API; xem [cấu hình gateway](../FE/deploy/README.md).

Cập nhật **03/11/2026, API 1.6.0**: `DELETE /api/runs/{run_id}` xóa một lần chạy và dữ liệu runtime đi kèm, gồm CSV đã tải lên, dự đoán, SHAP/Gemini, cảnh báo/nhật ký và Human review. Cần xác thực như các thao tác ghi khác. Trả 409 khi dự đoán/Replay hoặc giải thích còn chờ/đang chạy; Replay phải dừng hẳn trước khi xóa, Batch phải chờ hoàn tất. Không thể hoàn tác; các artifact nguồn trong `output/` không bị xóa. Khởi động lại đúng BE đang chạy để nạp API mới, không mở process thứ hai dùng chung runtime.

Phản hồi xóa gồm `run_id`, `files_deleted` và `message`. Bình thường thư mục runtime và các bản ghi liên quan đều được dọn. Nếu `files_deleted=false`, lịch sử đã xóa nhưng thư mục `.deleted-*` còn lại dưới `RUNTIME_DIR/runs/` cần quản trị viên dọn sau khi xử lý lỗi quyền/I/O. Không báo đã xóa toàn bộ tệp trong trường hợp này. Lỗi transaction SQLite phục hồi tên thư mục và giữ nguyên các bản ghi.

Cập nhật **01/11/2026, API 1.4.0**: `POST /api/auth/login` nhận thêm `remember` (mặc định false). False cấp session cookie không Max-Age/Expires; true đặt Max-Age=28800. Cả hai có cùng thời hạn BE tối đa tám giờ, HttpOnly/Strict và Secure khi HTTPS; logout/restart vẫn thu hồi. Không lưu password/token trong JavaScript storage. Cần restart đúng process BE đang chạy để nhận schema mới.

Cập nhật **01/11/2026, API 1.3.0**: thêm đăng nhập/đăng xuất bằng form tại FE `/login`, dùng lại tài khoản quản trị hiện có. `POST /api/auth/login` cấp cookie HttpOnly, SameSite=Strict, Secure khi HTTPS; `GET /api/auth/session` đọc phiên và `POST /api/auth/logout` thu hồi phiên. Phiên tối đa tám giờ, chỉ lưu hash token trong process BE duy nhất; restart BE yêu cầu đăng nhập lại. HTTP Basic tiếp tục dùng cho Swagger/CLI. Không thay pipeline hoặc dữ liệu runtime.

Sai đăng nhập 10 lần trong một phút theo địa chỉ client bị tạm chặn ở endpoint login (`429`, Retry-After); thao tác ghi kiểm tra Origin/Referer và Fetch Metadata, chặn origin khác cả với cookie lẫn Basic. Đây là ứng dụng một tài khoản quản trị, không có đăng ký/khôi phục mật khẩu qua email hoặc nhiều vai trò. Cơ chế HTTP Basic cũ vẫn dùng theo hợp đồng riêng. Tham khảo [HTTP Basic của FastAPI](https://fastapi.tiangolo.com/advanced/security/http-basic-auth/) và [hướng dẫn CSRF của OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).

Cập nhật **29/10/2026, API 1.2.0**: FE theo Miro đã chuyển sang Next.js, bỏ mount FE cũ; root BE chuyển tới Swagger; thêm `GET /api/runs/{run_id}/inputs/{row_index}` đọc đúng 46 đặc trưng đã lưu cho tab Đầu vào, không chứa nhãn thật và không suy luận lại. `/api/model` có thêm cấu hình SHAP để FE đọc metadata thật.

Cập nhật **28/10/2026, API 1.1.0**: bổ sung thống kê dashboard, bộ lọc, danh sách giải thích, quản lý cảnh báo có nhật ký, hướng dẫn theo tám lớp và hai mức diễn giải. Các request cũ mặc định dùng `audience_level=technical`. Nếu BE đang chạy ở terminal riêng, khởi động lại tiến trình đó để nhận code mới; không mở thêm server dùng chung runtime.

## Chạy trên máy local

Chạy các lệnh dưới đây từ thư mục gốc repo. Dùng Python 3.13 và môi trường riêng; tránh dùng các thư viện khác phiên bản của môi trường Anaconda chung.

```bash
python -m venv .venv
.venv/bin/python -m pip install -r BE/requirements-lock.txt
.venv/bin/python -m BE.init_env
.venv/bin/python -m BE
```

Nếu `.venv` đã tồn tại và đã cài dependencies, chỉ cần hai lệnh cuối. `BE.init_env` không ghi đè file `BE/.env` đã có.

Mở **http://127.0.0.1:8000/docs** để dùng Swagger qua HTTP Basic, hoặc **http://127.0.0.1:3000/login** để dùng form FE. Cả hai dùng cùng `ADMIN_USERNAME` (mặc định `admin`) và `ADMIN_PASSWORD` trong **`BE/.env`**. Mở file này trên máy của bạn để lấy hoặc đổi mật khẩu. File có quyền đọc/ghi cho chủ sở hữu và được Git bỏ qua. Nếu BE đang chạy code cũ, khởi động lại đúng process đó để nhận API đăng nhập mới; không mở process thứ hai trên cùng runtime.

Để có diễn giải từ Google, thêm `GEMINI_API_KEY` vào `BE/.env`, rồi khởi động lại BE. Giữ model mặc định `gemini-3.5-flash-lite`. Nếu chưa có key, vẫn dùng được Predict/SHAP; yêu cầu có Gemini nhận trạng thái `partial`/`not_configured` và vẫn có báo cáo số liệu.

Địa chỉ kiểm tra:

- `/health`: trạng thái sẵn sàng, không cần đăng nhập.
- `/`: chuyển tới Swagger, cần đăng nhập; không phục vụ source FE.
- `/docs`: Swagger UI, cần đăng nhập.
- `/openapi.json`: schema OpenAPI, cần đăng nhập.

Swagger UI sử dụng JavaScript/CSS từ CDN mặc định của FastAPI; máy mở Swagger cần truy cập được CDN đó.

## Artifact cần có

Đường dẫn mặc định tính từ repo root:

| Nguồn | Thư mục |
|---|---|
| Model | `output/stacking_meta_runs/xgb_meta_20261021_092334_9024562d/` |
| SHAP/background | `output/xai_shap_runs/shap_20261022_021654_2555e479/` |
| Prompt/schema/môi trường tham chiếu | `output/integration_runs/integration_20261022_075217_0b67d48f/` |

Bundle cần dùng là `frozen_models/XGB_d4_n200.joblib` trong thư mục model. Bundle lớn không được lưu trong Git; cần tải output Kaggle nguồn khi clone repo sang máy khác. Xem [hướng dẫn artifact](../output/README.md).

Có thể đổi vị trí qua `XGB_DIR`, `SHAP_DIR`, `INTEGRATION_DIR`, `RUNTIME_DIR` trong `BE/.env`. `BE/.env.example` liệt kê cấu hình hỗ trợ.

Khi khởi động, BE kiểm tra checksum và phiên bản trước khi nạp bundle; đối chiếu 16 dòng golden và xác suất nền. Thiếu/sai artifact hoặc khác phiên bản bắt buộc thì startup thất bại, không chạy model khác để thay thế. Python được kiểm tra cùng major/minor với nguồn; patch hiện tại được ghi lại trong `startup_checks.json`.

## Thử luồng hoàn chỉnh bằng Swagger

1. Gọi `GET /api/model` để xem model, kết quả golden, RAM, số lần nạp và trạng thái Gemini.
2. Gọi `GET /api/schema` hoặc tải CSV header qua `GET /api/input-template`.
3. Gọi `POST /api/runs`: chọn file `output/integration_runs/integration_20261022_075217_0b67d48f/input_features.csv`, đặt `mode=batch`, bấm Execute. Lưu `id` được trả về.
4. Gọi `GET /api/runs/{run_id}` đến khi `status=completed`. Gọi `/predictions` để xem nhãn/xác suất của 50 dòng.
5. Gọi `POST /api/runs/{run_id}/explanations` với JSON sau để thử SHAP mà không gọi API bên ngoài:

```json
{
  "row_indices": [0],
  "use_gemini": false,
  "retry_gemini": false
}
```

6. Gọi `GET /api/runs/{run_id}/explanations/0` để xem tiến độ. Khi hoàn thành, kết quả có top 5 SHAP và các URL tải waterfall/báo cáo.
7. Sau khi đã thêm API key và restart, gửi lại dòng đó với `use_gemini=true` để thêm diễn giải. BE dùng lại SHAP đã lưu.
8. Xuất dự đoán qua `/export?format=csv`, hoặc gói kết quả qua `/export?format=zip`.

Muốn thử Normal, BruteForce và Web-Based, upload **`output/xai_shap_runs/shap_20261022_021654_2555e479/selected_input.csv`** rồi chọn các dòng **`[0, 2, 14]`**. Các chỉ số này chỉ áp dụng CSV 16 mẫu đó, bắt đầu từ 0.

CSV phải có đúng 46 tên đặc trưng nguồn; cột `label` tùy chọn được bỏ khỏi đầu vào model và prompt. Thứ tự cột được sắp lại theo bundle. Giữ cách ép `float32`, chuyển Inf sang giá trị thiếu và tiền xử lý đã fit từ helper nguồn. Các giá trị không đổi được sang số hoặc tràn `float32` bị từ chối.

## Các API

| Method | Endpoint | Vai trò |
|---|---|---|
| POST | `/api/auth/login` | Kiểm tra tài khoản quản trị và cấp phiên cookie; không trả mật khẩu hoặc token trong JSON |
| GET | `/api/auth/session` | Đọc tài khoản và thời hạn phiên hiện tại; cần xác thực |
| POST | `/api/auth/logout` | Thu hồi phiên cookie và xóa cookie; gọi lại vẫn an toàn |
| GET | `/api/model` | Model, kiểm tra nguồn, RAM và trạng thái các worker |
| GET | `/api/schema` | Thứ tự đặc trưng/lớp và hợp đồng đầu vào |
| GET | `/api/input-template` | CSV header mẫu |
| POST | `/api/runs` | Upload CSV, tạo tác vụ batch/replay; trả `202` |
| GET | `/api/runs` | Lịch sử có phân trang |
| GET | `/api/runs/{run_id}` | Trạng thái, số dòng đã xử lý và số lượng giải thích theo trạng thái |
| GET | `/api/runs/{run_id}/summary` | Phân bố tám lớp, số mẫu nghi vấn và trạng thái giải thích/cảnh báo |
| GET | `/api/runs/{run_id}/predictions` | Đọc dự đoán, lọc lớp/trạng thái giải thích và phân trang |
| GET | `/api/runs/{run_id}/inputs/{row_index}` | 46 đặc trưng float32 trước tiền xử lý của một dòng; null cho giá trị thiếu, không có label |
| POST | `/api/runs/{run_id}/control` | Điều khiển replay; tiếp tục batch bị gián đoạn/lỗi |
| POST | `/api/runs/{run_id}/explanations` | Chọn các dòng đã có dự đoán; trả `202` |
| GET | `/api/runs/{run_id}/explanations` | Danh sách trạng thái giải thích theo mức diễn giải; có bộ lọc/phân trang |
| GET | `/api/runs/{run_id}/explanations/{row_index}` | Trạng thái, SHAP, Gemini và URL tải file |
| GET | `/api/runs/{run_id}/explanations/{row_index}/files/{filename}` | Tải file kết quả được phép |
| GET | `/api/runs/{run_id}/export` | Xuất CSV hoặc ZIP |
| GET | `/api/alerts` | Lọc cảnh báo theo lần chạy, lớp và trạng thái tiếp nhận |
| GET | `/api/alerts/{alert_id}` | Chi tiết, bằng chứng dự đoán, hướng dẫn và lịch sử xử lý |
| PATCH | `/api/alerts/{alert_id}` | Tiếp nhận/đóng/mở lại cảnh báo; ghi tài khoản và ghi chú |
| GET | `/api/playbooks/{class_name}` | Hướng dẫn tham khảo có nguồn cho một trong tám lớp |

Mã lỗi chính: `401` chưa xác thực, `404` không có tài nguyên, `409` trạng thái chưa phù hợp, `413` quá dung lượng, `422` dữ liệu không hợp lệ, `429` đầy hàng chờ giải thích.

`202` chỉ xác nhận đã tiếp nhận tác vụ. Cần đọc endpoint trạng thái để biết xử lý thực tế đã xong hay chưa.

## API dashboard và cảnh báo

`GET /api/runs/{run_id}/summary` trả đủ tám lớp, kể cả lớp có số lượng bằng 0. `processed_rows` là số dự đoán đã lưu; `pending_rows` là số dòng chưa dự đoán. `prediction_status=completed` không đồng nghĩa đã giải thích xong mọi mẫu. `explanation_counts.not_requested` giúp FE phân biệt chưa yêu cầu với tác vụ lỗi; tất cả số đếm giải thích/Gemini chỉ tính mức diễn giải đã chọn.

Ví dụ bộ lọc:

```text
GET /api/runs/{run_id}/predictions?predicted_class=BruteForce&explanation_status=not_requested
GET /api/runs/{run_id}/explanations?status=partial&audience_level=basic
GET /api/alerts?run_id={run_id}&status=new&predicted_class=Web-Based
```

`total` trong danh sách là số dòng khớp bộ lọc, trước phân trang; `total_predicted` trong danh sách dự đoán là số dòng đã dự đoán trước lọc. Các API đọc chỉ đọc dữ liệu đã lưu, không gọi model hay Gemini.

Mỗi dự đoán **khác Normal** tạo một cảnh báo theo model trong cùng transaction lưu dự đoán. Khóa duy nhất `(run_id,row_index)` tránh tạo trùng; đây chưa phải xác nhận tấn công. Các lần gọi model bên trong SHAP không tạo cảnh báo mới. Tạo cảnh báo không tự xếp hàng giải thích hoặc gọi Gemini.

Trạng thái cảnh báo: `new → acknowledged → closed`; mở lại bằng `closed → acknowledged`. Gửi lại cùng trạng thái/ghi chú không tạo thêm sự kiện. Ví dụ PATCH:

```json
{
  "status": "acknowledged",
  "note": "Đã tiếp nhận để kiểm tra thêm bằng chứng."
}
```

Bỏ `note` để giữ ghi chú cũ; gửi chuỗi rỗng để xóa ghi chú hiện tại. Lịch sử vẫn giữ các ghi chú trước. API dùng tài khoản đăng nhập làm `actor`, không nhận tên actor tùy ý từ client. Vì nhóm dùng chung tài khoản, nhật ký chưa phân biệt từng cá nhân. Thao tác xử lý cảnh báo không gán nhãn thật, không thay đổi model và không hoàn thành human review.

Khi khởi động bản mới, BE tự nâng schema giải thích, gán các bản ghi cũ vào mức `technical`, giữ nguyên dữ liệu và thêm cảnh báo cho dự đoán cũ khác Normal. Phần chuyển schema/sao chép được thực hiện trong transaction; chạy lại không tạo trùng cảnh báo hoặc nhật ký. File kết quả cũ vẫn ở vị trí cũ.

## Hai mức diễn giải và hướng dẫn theo lớp

Request cũ tiếp tục mặc định `technical` (Kỹ thuật). Muốn diễn giải Dễ hiểu:

```json
{
  "row_indices": [0, 1],
  "use_gemini": true,
  "audience_level": "basic",
  "retry_gemini": false
}
```

Theo dõi bằng `GET /api/runs/{run_id}/explanations/0?audience_level=basic`. Trạng thái/cache Gemini tách theo mức; SHAP, xác suất và bằng chứng dùng chung. Mức `technical` giữ prompt và đường dẫn cache cũ; `basic` bổ sung chỉ dẫn dùng câu ngắn, từ phổ thông và giải nghĩa thuật ngữ. Cả hai vẫn phải qua cùng kiểm tra schema/bằng chứng/tiếng Việt. Kiểm tra tự động chưa chứng minh chất lượng ngữ nghĩa hoặc khả năng đọc hiểu thực tế.

Đổi mức có thể phát sinh lời gọi Gemini mới, không phải một lượt `retry` của mức cũ. `retry_gemini=true` chỉ tạo lại Gemini cho mức được yêu cầu và lưu lịch sử riêng. Hàng chờ 50 tính cả mẫu/mức đang chờ hoặc đang chạy.

`GET /api/playbooks/BruteForce` trả hướng dẫn cố định do nhóm biên soạn, có phiên bản và link nguồn MITRE/NIST; hướng dẫn IoT tham khảo thêm UK Government. Đây là tài liệu gợi ý theo lớp rộng, không phải ánh xạ đã xác nhận sang kỹ thuật MITRE hoặc CVE. Không thực thi thao tác mạng. Nguồn được ghi rõ trong [playbooks.py](playbooks.py); nội dung cần được người vận hành đối chiếu với hạ tầng thực tế.

Chi tiết giải thích và cảnh báo có kèm hướng dẫn. Báo cáo mới có phần hướng dẫn riêng do chương trình tra cứu, kể cả khi Gemini chưa cấu hình/lỗi. Báo cáo lưu snapshot `playbook.json` để giữ đúng phiên bản đã dùng. ZIP chứa hai biến thể diễn giải nếu đã yêu cầu, cùng cảnh báo và nhật ký xử lý; CSV dự đoán giữ cấu trúc cũ.

## Phát lại CSV và trạng thái

Chọn `mode=replay` khi upload. Mặc định `interval_seconds=1`, cho phép từ 0,05 đến 60 giây. Mỗi nhịp gọi model cho dòng được phát; không dùng bảng dự đoán tính sẵn để giả lập suy luận. Đây vẫn là mô phỏng từ CSV, không phải bắt gói mạng trực tiếp.

Ví dụ body gửi `/control`:

```json
{"action": "pause"}
```

Các action khác là `resume` và `stop`. Dòng đang suy luận có thể hoàn tất sau yêu cầu pause/stop. `resume` tiếp tục từ dòng chưa được lưu, không tạo lại các dòng đã có. Batch hỗ trợ `resume` sau khi bị gián đoạn/lỗi; pause/stop dành cho replay.

Trạng thái lần chạy: `queued`, `running`, `paused`, `stopped`, `interrupted`, `failed`, `completed`.

Trạng thái giải thích: `queued`, `shap_running`, `gemini_running`, `completed`, `partial`, `failed`, `interrupted`. `partial` nghĩa là vẫn giữ phần đã có, ví dụ SHAP đã thành công nhưng thiếu Gemini key hoặc diễn giải không đạt kiểm tra.

Khi server khởi động lại, tác vụ đang chạy được đánh dấu `interrupted`. Người dùng chủ động gửi `resume` cho dự đoán hoặc yêu cầu giải thích lại để tiếp tục từ cache. Không tự động phát sinh lời gọi Gemini sau restart.

## Giới hạn và cách dùng Gemini

- Mỗi CSV tối đa 1.000 dòng/10 MiB; chỉ một tác vụ dự đoán/phát lại hoạt động tại một thời điểm.
- Mỗi yêu cầu giải thích tối đa 50 dòng không lặp; toàn hàng chờ kể cả dòng đang chạy tối đa 50 mẫu.
- Hai worker là luồng trong một process: dự đoán và giải thích. Model dùng chung khóa; không giữ khóa khi chờ Google.
- Model dùng hai CPU threads. Tiền xử lý không fit lại, OOF/fold không được tạo lại.
- SHAP giải thích cả pipeline trên 46 đặc trưng gốc, background 32 mẫu, ngân sách 465 và ngưỡng bảo toàn `1e-5`.
- Gemini dùng phản hồi có schema; kiểm tra lớp, thứ tự/hướng SHAP và tiếng Việt. Chỉ sửa văn bản tối đa một lần; không tự retry lỗi API hoặc sai bằng chứng.
- Mặc định có khoảng nghỉ bốn giây giữa các lời gọi mới; đổi bằng `GEMINI_PAUSE_SECONDS` nếu tài khoản của bạn cho phép.
- `retry_gemini=true` là yêu cầu chủ động tạo lượt Gemini mới, có thể phát sinh chi phí. Các phản hồi cũ được chuyển vào `previous_gemini/`, SHAP được giữ lại.
- API không nhận upload model hoặc API key; key chỉ đặt ở môi trường server. Không có chức năng tự chặn IP hay tự đổi dự đoán theo LLM.

## Dữ liệu được lưu

Từ API **1.5.0**, người dùng có thể lưu đánh giá thủ công của mẫu trong bảng SQLite `human_reviews`:

- `GET /api/runs/{run_id}/human-reviews/{row_index}`: đọc bản đã lưu và dấu vân tay của bằng chứng hiện tại.
- `PUT` cùng đường dẫn: lưu tên người đánh giá, nhận định về nhãn, nhãn đề xuất tùy chọn, ba tiêu chí 1–5 và ghi chú. Điểm chưa chấm là `null`. Tài khoản người lưu lấy từ phiên đăng nhập; không nhận tài khoản giả trong body.
- `GET .../human-reviews/{row_index}/export`: tải JSON đã lưu, kèm ngữ cảnh, dấu vân tay và cờ `stale` nếu bằng chứng đã thay đổi. `audience_level` mặc định `technical`.

Đánh giá lưu riêng, không thay nhãn model, xác suất hay trạng thái cảnh báo. Tư cách chuyên gia chưa được xác minh; nhận định/nhãn đề xuất do người dùng nhập không tự trở thành nhãn thật. Nếu bằng chứng đổi sau lúc mở form, PUT trả 409 để người dùng đọc lại và đối chiếu trước khi lưu. Khi đang sinh giải thích, chờ ghi xong tệp trước khi đánh giá. ZIP thêm `human_reviews.json`; có thể gồm bản đánh giá dựa trên bằng chứng cũ, cần đối chiếu fingerprint.

BE đang chạy cần khởi động lại đúng process để nạp API/schema 1.5.0. Không mở thêm process dùng chung runtime; việc tạo bảng mới không xóa các kết quả đã lưu.

Mặc định mọi dữ liệu ứng dụng ghi vào **`BE/runtime/`**, được Git bỏ qua:

```text
BE/runtime/
  startup_checks.json
  app.sqlite3
  server.lock
  runs/<run_id>/
    input.csv
    input_features.csv
    input_values.npy
    protocol.json
    cases/row_0000/
      explanation.json
      shap_values.npz
      top5_features.csv
      waterfall.png
      llm_input.json
      gemini_status.json
      report_vi.md
      playbook.json
      audiences/basic/         # Chỉ tạo khi yêu cầu mức Dễ hiểu
        gemini_status.json
        explanation_vi.json
        report_vi.md
        playbook.json
```

Bundle, background và các artifact trong `output/` chỉ được đọc. Khóa `server.lock` ngăn hai process dùng cùng runtime; chạy Uvicorn với một worker. Gói ZIP chứa snapshot các kết quả hoàn thành/partial, không chứa `.env` hay credentials.

## Truy cập LAN bằng HTTPS

Tạo chứng chỉ cho IP/tên máy thực tế của server. Ví dụ thay `192.168.1.10` bằng IP LAN của máy bạn:

```bash
.venv/bin/python -m BE.create_certificate --host 192.168.1.10
.venv/bin/python -m BE --host 0.0.0.0 --ssl-certfile BE/runtime/tls/cert.pem --ssl-keyfile BE/runtime/tls/key.pem
```

Mở `https://192.168.1.10:8000/docs`. Chứng chỉ tự ký dành cho demo nội bộ; cài tin cậy chứng chỉ công khai trên máy truy cập. Giữ private key tại server. Lệnh chạy BE yêu cầu HTTPS khi bind địa chỉ ngoài loopback.

## Kiểm thử

```bash
.venv/bin/python -m pytest BE/tests -q --disable-warnings
```

Kiểm thử sử dụng model/background thật và source CSV đã lưu, kiểm tra batch/replay/restart, schema, giới hạn tải lên, SHAP, cache và xuất file. Phần Gemini dùng phản hồi giả hoặc báo cáo đã lưu để kiểm tra luồng/bằng chứng; không gọi Google và không đánh giá chất lượng ngữ nghĩa của LLM.

Xem [bằng chứng kiểm chứng BE](VERIFICATION.md) để biết các kiểm tra nào đã thực sự chạy. Validation/test nguồn đã từng được xem; các CSV đối chiếu không phải test độc lập mới. Form Human review nhận đánh giá của người dùng; chưa có đánh giá nhãn thật độc lập hoặc xác minh tư cách chuyên gia.

## Kafka và Langfuse Cloud — BE 1.8.0

Hướng dẫn đầy đủ tại [deploy/observability/README.md](../deploy/observability/README.md). `POST /api/runs` nhận header `Idempotency-Key` tùy chọn: cùng key/nội dung trả lại run đã lưu, khác nội dung trả 409. Receipt và run lưu cùng transaction SQLite; receipt vẫn giữ khi run bị xóa để tránh tự nhập lại dữ liệu đã xóa. API upload trực tiếp không có header vẫn hoạt động như trước.

`GET /api/observability` có xác thực, không trả secret. Langfuse Cloud đọc từ `.env.observability` khi chạy local hoặc biến môi trường trong Compose. Model và SHAP background không thay đổi; tracing không làm phát sinh lời gọi Gemini mới. Consumer yêu cầu BE có cơ chế chống trùng; producer dùng schema đóng băng trong image nên không cần BE online hoặc credentials.
