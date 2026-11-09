# Bằng chứng kiểm chứng BE

## BE 1.8.0: Kafka và Langfuse Cloud — 06/11/2026

Đã thêm Idempotency-Key và receipt SQLite bền vững, tracing tùy chọn cho Predict/SHAP/Gemini. **85 test BE/streaming đạt**, Kafka thật đối chiếu golden và Cloud nhận trace kiểm thử/trace dự đoán thật. Backend được cập nhật sau khi người dùng cho phép, có backup SQLite; hai run cũ, giải thích và Human review được giữ nguyên. Chi tiết, giới hạn và bằng chứng tại [kiểm chứng observability](../deploy/observability/VERIFICATION.md). Các mục dưới đây là lịch sử các đợt trước.

## API Tổng quan — 04/11/2026

API 1.7.0 thêm GET /api/dashboard. Đã chạy toàn bộ `pytest BE/tests -q --disable-warnings`: **56 test đạt**; log /tmp/nidr-dashboard-backend.log. Năm test mới dùng runtime/model thật và dữ liệu SQLite/artifact fixture để kiểm tra: xác thực/schema/validation; tổng 171 mẫu vượt trang hiển thị; run filter; nửa mở ngày Việt Nam quanh 17:00 UTC; ngày trống bằng 0; SHAP theo file kể cả trạng thái failed và không đếm hai audience; phiếu technical không trùng basic; đóng cảnh báo không đổi nhận định; toàn lịch sử giữ trend 30 ngày; xóa run cập nhật tổng.

Test khóa runtime.predict để xác nhận đọc dashboard không suy luận; model_load_count giữ 1. Artifact JSON tối giản trong test đếm file chỉ là fixture của phép thống kê, không dùng làm bằng chứng chất lượng SHAP. Bài test phiên bản Swagger được cập nhật từ 1.6.0 lên 1.7.0. Không thay model/background hoặc pipeline.

SQL đọc cùng snapshot, dùng bảng TEMP cho nhóm mẫu theo thời gian xử lý; chỉ chọn cột cần thiết. Mốc ngày được đổi sang UTC trước truy vấn, ngày biểu đồ theo UTC+7. Phạm vi cảnh báo/phiếu là nhóm mẫu, trạng thái hiện tại; đây không phải thời điểm tấn công hay tập đánh giá accuracy. SHAP đếm file chung đang có tại thời điểm đọc; số phiếu là bản đã lưu, không xác nhận còn khớp evidence signature. Bộ lọc all trả tổng toàn lịch sử đến hết hôm nay và biểu đồ 30 ngày gần nhất, có trường phạm vi riêng.

Kiểm chứng ban đầu: **27/10/2026**. Nhánh làm việc: **`duong`**. Các cập nhật mới nhất ghi trước phần lịch sử.

## Xóa lịch sử từng lần chạy — API 1.6.0, 03/11/2026

Thêm `DELETE /api/runs/{run_id}` có xác thực và kiểm tra Origin. Khóa điều phối chặn tác vụ mới khi xóa, từ chối queued/running/paused, worker dự đoán chưa dừng hẳn và mọi mức SHAP/Gemini còn chờ/đang chạy. SQLite xóa alert_events, alerts, human_reviews, explanations, predictions và runs trong cùng transaction. Đổi tên thư mục runtime trước transaction, phục hồi nếu DB thất bại; sau commit mới dọn tệp. Khi dọn tệp lỗi, phản hồi 200 với `files_deleted=false` và thông báo rõ lịch sử đã xóa nhưng tệp chưa dọn hết; không báo xóa tệp thành công. Không sửa hoặc xóa artifact nguồn.

Xuất CSV/ZIP và ghi review dùng cùng khóa để tránh đọc/ghi giữa lúc thư mục bị chuyển đi. Nếu thao tác control/explain đã qua kiểm tra ban đầu nhưng run bị xóa trước khi lấy khóa, require_signature trả xung đột rõ ràng thay vì lỗi KeyError.

**51 test BE đạt** bằng `.venv/bin/python -m pytest BE/tests -q --disable-warnings` (exit 0; log `/tmp/nidr-delete-all-be.log`). Năm test mới dùng runtime tạm và model thật: xóa cả hai mức giải thích/review/cảnh báo/tệp, giữ nguyên run khác, auth/Origin/ID, chặn Replay kể cả sau stop nhưng predict còn ghi, chặn SHAP đang chạy, rollback SQL khi trigger từ chối delete và báo đúng lỗi rmtree. Kiểm tra khóa ngoại không có orphan; gọi xóa lần hai/đọc/xuất run đã xóa nhận 404. Không gọi Google, không đọc .env hoặc restart BE vận hành.

Khả năng giới hạn: dữ liệu đã tải xuống trước đó không được thu hồi; lỗi dọn tệp cần quản trị viên xử lý thư mục `.deleted-*` trong runtime theo README. Không có nút xóa hàng loạt hoặc tự động xóa theo thời gian.

## Đánh giá thủ công lưu SQLite — API 1.5.0

Thêm bảng `human_reviews` và ba thao tác GET/PUT/export JSON, giữ bản mới nhất theo run/dòng/mức. OpenAPI thực tế **26 thao tác / 22 đường dẫn**. Schema không nhận trường ngoài hợp đồng, điểm chỉ nhận số nguyên 1–5 hoặc null; tên người đánh giá không được toàn khoảng trắng, tài khoản được ghi từ phiên đăng nhập. PUT vẫn kiểm tra Origin. Nhãn đề xuất và ghi chú không sửa nhãn/probabilities hoặc trạng thái cảnh báo.

Lệnh `.venv/bin/python -m pytest BE/tests -q --disable-warnings` đạt **46 passed, 629 cảnh báo thư viện, 33,02 s**, log `/tmp/nidr-human-review-backend-confirm.log`. Ba test mới kiểm tra save/đọc lại sau mở Store, JSON tải xuống, tách Technical/Basic, auth/CSRF, điểm/tên/nhãn/giả mạo người lưu, đúng dòng và fingerprint. Khi tệp đổi, GET đánh dấu stale, PUT dùng fingerprint cũ trả 409, bản cũ vẫn được giữ đến khi người dùng chủ động lưu mới. Dòng chưa có dự đoán trả 404. Không tự chấm hoặc xác minh tư cách chuyên gia.

ZIP thêm `human_reviews.json`. Chỉ ghi runtime trong lúc ứng dụng chạy; test dùng runtime/model/SHAP thật riêng và Gemini giả lập. Không ghi artifact output hoặc đọc .env; chưa restart BE vận hành. Người dùng cần restart đúng process BE lên 1.5.0 để nạp endpoint/tạo bảng mới. Kiểm tra giao diện được ghi riêng ở FE/VERIFICATION.md sau lượt browser cuối.

## Tùy chọn Ghi nhớ phiên — 01/11/2026

API **1.4.0**, giữ **23 thao tác / 20 đường dẫn**. LoginRequest thêm remember=false mặc định; cookie không Max-Age/Expires khi tắt, Max-Age=28800 khi bật. Hai chế độ cùng thời hạn BE tối đa tám giờ, giữ HttpOnly/Strict/Secure, rotate/revoke và session store trong process. Không thay luồng model/SHAP/Gemini.

Pytest đạt **43 passed**, 629 cảnh báo thư viện, **45,01 giây** (lượt chạy cùng build FE và dev proxy check). XML `/tmp/iot-login-polish-backend-tests.xml` được sao vào FE/tests/results/backend-tests.xml. Test mới xác minh cả hai chế độ cookie và logout. Next dev proxy check đạt; browser suite qua Nginx HTTPS đạt **26 nhóm**, gồm form mới, spinner, ổn định bố cục lỗi và thuộc tính cookie của hai lựa chọn. Gemini giả lập/không gọi thật; model nạp một lần. Không đọc .env hoặc restart BE vận hành.

## Sửa Origin qua Next dev rewrites — 01/11/2026

Next 16.4.3 bật changeOrigin khi proxy, đổi Host sang cổng BE và ghi đè X-Forwarded-Host bằng Host của FE. Bản cũ chỉ so Origin với Host nội bộ nên chặn nhầm login từ cổng 3000. `verify_browser_origin` hiện lấy X-Forwarded-Host khi client là loopback 127.0.0.1/::1; kết nối ngoài loopback không được tin header này. Giữ so khớp Origin/Referer chính xác và chặn Fetch Metadata khác origin. Không thêm CORS wildcard hoặc tắt CSRF.

Pytest đạt **42 passed**, 629 cảnh báo thư viện, **28,58 giây**, XML `/tmp/iot-origin-backend-tests.xml` được sao vào `FE/tests/results/backend-tests.xml`. Hai test mới phủ forwarded host loopback/không loopback, Referer và Origin giả/sai/null.

`.venv/bin/python FE/tests/dev_proxy_check.py` đạt đủ login, đọc cookie session, upload multipart, chặn origin ngoài, chặn header forwarded-host giả qua Next và logout. Script chạy Next dev thật với chính next.config.ts trên cổng tạm, dùng frozen model một lần, không gọi Gemini; project/runtime/cache tạm đã dọn. Kiểm tra Next rewrites này bổ sung phần chưa được phủ bởi gateway Nginx trong suite trước. Đã chạy lại browser suite qua gateway HTTPS, **26 nhóm đạt** với model/SHAP thật và Gemini giả lập. Không đọc `.env` hoặc restart BE vận hành; người dùng cần restart đúng process để nạp bản sửa.

## Đăng nhập và đăng xuất bằng cookie — 01/11/2026

API **1.3.0**, **23 thao tác / 20 đường dẫn**. Thêm login/session/logout bằng tài khoản hiện có, giữ HTTP Basic cho Swagger/CLI. Phiên random token 256 bit, BE chỉ giữ SHA256 trong bộ nhớ, giới hạn tám giờ, rotate khi đăng nhập lại và revoke khi logout; restart xóa phiên. Cookie HttpOnly/Strict, Secure khi HTTPS. Cookie mutations/login/logout kiểm tra Origin/Referer/Fetch Metadata; endpoint login có giới hạn 10 lần nhập sai/phút theo client. Không thay model, SHAP, jobs hoặc artifact nguồn.

Lệnh `.venv/bin/python -m pytest BE/tests -q --disable-warnings --tb=short --junitxml=/tmp/iot-login-backend-tests.xml` đạt **40 passed**, 629 cảnh báo thư viện, **28,21 giây**. Sáu test mới xác minh cookie/login/logout, token cũ không dùng lại, sai Basic không bị che bởi cookie, lỗi không lộ credentials, Secure/CSRF, timeout phiên/restart và throttling. XML được sao vào `FE/tests/results/backend-tests.xml` (ignored).

Chrome + Nginx + Next production + BE/model/SHAP thật đạt **26 nhóm kiểm tra**, dùng form và cookie thật, Gemini giả lập. Bao gồm deep link, refresh, sign out/revocation, xuất báo cáo và các luồng cũ. Không khởi động lại BE vận hành hoặc đọc .env; để dùng form mới, người dùng restart đúng process BE với source 1.3.0. Cấu hình Nginx mới chỉ được thử ở instance tạm. Đây không phải kiểm thử xâm nhập hoặc chứng nhận an toàn cho triển khai Internet.

## Chuyển FE sang Next.js — 30/10/2026

Theo [FE/PLAN.md](../FE/PLAN.md), FE đã chuyển sang Next.js/React/TypeScript và Nginx làm cổng HTTPS chung trên cùng máy. BE bỏ mount `/assets` và trả redirect có xác thực từ `/` sang `/docs`. REST API/OpenAPI vẫn **1.2.0, 20 thao tác / 17 đường dẫn**; pipeline, database, `.env` và artifact nguồn giữ nguyên.

Sau thay đổi serving, lệnh `.venv/bin/python -m pytest BE/tests -q --disable-warnings --tb=short --junitxml=/tmp/iot-next-backend-tests.xml` đạt **34 passed**, 629 cảnh báo thư viện, **26,10 giây**. Test serving chuyển sang kiểm tra redirect/xác thực và các đường dẫn source riêng tư; giữ các test input 46 trường/checksum. Bản XML được lưu thêm tại `FE/tests/results/backend-tests.xml` (Git bỏ qua).

Kiểm thử production Next/Nginx/Chrome với BE/model thật nằm trong [FE/VERIFICATION.md](../FE/VERIFICATION.md). Các process kiểm thử dùng cổng/runtime/tài khoản tạm, không khởi động lại BE của người dùng và không gọi Gemini thật. Phần bên dưới ghi lịch sử trước khi chuyển Next.js.

## Cập nhật BE 1.2.0 và FE — 29/10/2026

Đã phục vụ [FE theo Miro](../FE/README.md) tại `/`, giữ Swagger ở `/docs`, chỉ mount tài nguyên `FE/assets/`. Thêm API đầu vào từng dòng và metadata cấu hình SHAP cho giao diện. Các mục ngày 27–28/10 bên dưới là lịch sử kiểm chứng BE.

Lượt `.venv/bin/python -m pytest BE/tests -q --disable-warnings --junitxml=/tmp/iot-fe-backend-tests.xml` đạt **34 passed**, 629 cảnh báo thư viện, **26,32 giây**. Ba test mới kiểm tra phục vụ FE/xác thực/phạm vi file tĩnh, 46 đặc trưng có giá trị thiếu/không có label, và chặn mảng đầu vào đã lưu bị sửa checksum. OpenAPI có **20 thao tác / 17 đường dẫn**, phiên bản **1.2.0**.

Kiểm thử Chrome với BE/model/SHAP thật và Gemini giả lập đạt **14 nhóm kiểm tra**, gồm upload, chọn mẫu, hai mức giải thích, cảnh báo, tải tệp, lỗi 429, mất kết nối và điều khiển Replay. Model nạp một lần. Xem [FE/VERIFICATION.md](../FE/VERIFICATION.md) cho bằng chứng và giới hạn. Server kiểm thử dùng runtime/cổng tạm và đã đóng; không khởi động lại tiến trình BE của người dùng, không gọi Google mới, không thay artifact nguồn.

## Cập nhật BE 1.1.0 — 28/10/2026

Đã bổ sung summary theo lần chạy, bộ lọc dự đoán, danh sách giải thích có phân trang, cảnh báo theo model và nhật ký tiếp nhận/đóng/mở lại, hướng dẫn có nguồn cho tám lớp, hai mức Gemini basic/technical.

Lệnh kiểm thử cuối:

```bash
.venv/bin/python -m pytest BE/tests -q --disable-warnings --junitxml=BE/runtime/test_results.xml
```

Kết quả: **31 passed**, 0 fail/error/skipped, **26,07 giây**. Có 629 cảnh báo thư viện thuộc môi trường nguồn, được pytest tổng hợp; không tự nâng thư viện đã khóa. Ngoài 22 test cũ, chín test mới kiểm tra:

- Tổng hợp tám lớp và phân biệt dự đoán hoàn tất với giải thích chưa yêu cầu/lỗi; bộ lọc, tổng số và phân trang nhất quán.
- Summary khi replay đang pause; resume không nhân đôi cảnh báo.
- Không tạo cảnh báo cho Normal, chuyển trạng thái đúng thứ tự, actor lấy từ đăng nhập, giữ dự đoán và human review; xuất nhật ký trong ZIP.
- Gửi tiếp nhận đồng thời không nhân đôi sự kiện.
- Nâng database schema cũ, giữ dự đoán/Gemini đã có; backfill và restart không nhân đôi cảnh báo/nhật ký.
- Nâng schema thất bại sau khi sao chép dữ liệu thì rollback cả DDL và dữ liệu cũ.
- Đủ tám hướng dẫn có nguồn, hoạt động khi không cấu hình Gemini.
- Hai mức Gemini có request hash, trạng thái, báo cáo và retry riêng; dùng lại SHAP, giữ cache technical; ZIP chứa cả hai biến thể.
- Chỉ yêu cầu basic không tạo nhầm trạng thái technical; thiếu key vẫn có hướng dẫn và báo cáo.

OpenAPI sinh từ mã hiện tại có **19 thao tác HTTP trên 16 đường dẫn**, phiên bản **1.1.0**. Đã đối chiếu lại **745 mục checksum nguồn**, tất cả khớp. Bằng chứng tại `BE/runtime/test_results.xml` và `BE/runtime/backend_extension_checks.json`.

Lượt thay đổi này dùng TestClient, database tạm, model/SHAP thật và Gemini giả lập; **không khởi động/khởi động lại BE đang chạy và không gọi Google API mới**. Nâng schema database vận hành chỉ xảy ra khi người dùng khởi động lại BE bằng code mới.

Hai mẫu local trong run `b251ef93b9694a4c9565f5ad747f31dd` đã gọi Gemini thật và nhận accepted ở phiên trước ngày 27/10/2026. Đó là bằng chứng cho luồng cũ mặc định technical; chưa kiểm chứng chất lượng ngôn ngữ của basic bằng phản hồi mới từ Google. Hướng dẫn theo lớp do nhóm biên soạn từ nguồn đã ghi, chưa được human review nghiệm thu.

Các mục ngày 27/10/2026 bên dưới giữ làm lịch sử kiểm chứng phiên bản ban đầu.

## Môi trường và model

- Linux x86_64, 8 CPU threads logic, tổng RAM khoảng 7,45 GiB.
- Python local **3.13.5**; run Kaggle ghi Python 3.13.15. BE kiểm tra cùng major/minor và ghi nhận patch thực tế.
- Các phiên bản NumPy, pandas, scikit-learn, joblib, XGBoost, SHAP, Matplotlib và Google Gen AI khớp run nguồn. Toàn bộ môi trường đã khóa trong `requirements-lock.txt`.
- Model chốt: `XGB_d4_n200`, bundle SHA256 `72d62f8760e48287fff7dcb590944f7169055d7fc0fb6a5b2969e6287f389033`.
- Background SHAP: 32 dòng train, 46 đặc trưng, `float32`.
- Không fit tiền xử lý, tạo lại fold/OOF hoặc huấn luyện lại model trong lượt triển khai này.

## Kiểm thử tự động đã chạy

Lệnh:

```bash
.venv/bin/python -m pytest BE/tests -q --disable-warnings --junitxml=BE/runtime/test_results.xml
.venv/bin/python -m pip check
```

Kết quả: **22 passed**, không có test fail/error/skipped. Lượt cuối mất khoảng **19,19 giây**. `pip check` không phát hiện dependency bị hỏng.

Các nhóm đã kiểm tra:

- Checksum sai và phiên bản thư viện lệch bị chặn trước khi nạp joblib.
- Xác thực HTTP Basic, Swagger/OpenAPI, schema và CSV template.
- Dự đoán đủ 50 mẫu khớp CSV nguồn, phân trang và xuất CSV/ZIP.
- CSV thiếu/trùng cột, giá trị không hợp lệ, số dòng/dung lượng vượt giới hạn và cột `label` tùy chọn.
- Replay có pause/stop/resume; dừng ngắt được nhịp chờ 60 giây; không tạo trùng dòng.
- Restart giữ kết quả đã có và tiếp tục từ dòng chưa lưu.
- SHAP thật trên DDoS và các mẫu Normal/BruteForce/Web-Based; xử lý được giá trị thiếu bằng preprocessor đã lưu.
- Đối chiếu mảng SHAP của một mẫu với artifact nguồn khi cùng seed và dữ liệu.
- Thiếu Gemini key vẫn có dự đoán, SHAP, báo cáo và trạng thái partial.
- Gemini giả lập: phản hồi hợp lệ, sửa thiếu dấu một lần, đổi lớp bị từ chối, quota 429, timeout, cache phản hồi và chủ động retry.
- Validator đã đối chiếu đủ 50 báo cáo Gemini accepted lưu từ Kaggle.
- Hàng chờ 50 mẫu, yêu cầu trùng, tải file được phép và không nạp lại model cho mỗi request.
- Chặn hai server dùng chung runtime; CLI yêu cầu TLS khi mở LAN; chứng chỉ có SAN đúng host và không ghi đè private key đã có.

Lượt pytest có các cảnh báo deprecation từ Matplotlib/pyparsing và Starlette TestClient. Đây là cảnh báo tương thích của thư viện, không phải lỗi test; báo cáo trên vẫn giữ nguyên các phiên bản nguồn để tái sử dụng artifact.

## Kiểm chứng qua server HTTP thật

Đã chạy `.venv/bin/python -m BE` và gọi API tại `http://127.0.0.1:8000`:

| Nội dung | Kết quả |
|---|---|
| `/health` | HTTP 200, ready |
| `/docs` khi chưa đăng nhập | HTTP 401 |
| `/docs`, `/openapi.json` có xác thực | HTTP 200 |
| OpenAPI | 13 thao tác HTTP trên 12 đường dẫn |
| Batch CSV 50 mẫu | Đủ 50 dòng; nhãn và tám xác suất khớp artifact nguồn với `rtol=1e-6`, `atol=1e-7` |
| Số lần nạp model trong process | 1 |
| Xuất ZIP và tải waterfall/báo cáo | Thành công |
| Thiếu API key | Mẫu vẫn có SHAP/báo cáo, Gemini ghi `not_configured` |

Ba mẫu được giải thích thật từ CSV golden 16 dòng:

| Chỉ số dòng | Lớp dự đoán | Thời gian SHAP | Sai số bảo toàn lớn nhất |
|---:|---|---:|---:|
| 0 | Normal | 5,867 s | 1,11e-16 |
| 2 | BruteForce | 0,562 s | 1,11e-16 |
| 14 | Web-Based | 0,548 s | 3,47e-17 |

Ca đầu có chi phí khởi tạo/JIT. Đây là thời gian SHAP được ghi cho từng mẫu, không phải tổng thời gian API gồm biểu đồ/lưu file. RAM RSS sau các lượt này khoảng **966,68 MiB**; số đo không phải cam kết tải tối đa.

Bằng chứng chi tiết giữ ở local:

- `BE/runtime/startup_checks.json`: source hash, phiên bản, kiểm tra golden và nền SHAP.
- `BE/runtime/test_results.xml`: kết quả 22 test.
- `BE/runtime/live_http_checks.json`: lượt gọi HTTP thật và các run ID demo.
- `BE/runtime/tls_http_checks.json`: kiểm chứng HTTPS.

## HTTPS đã kiểm chứng

Đã tạo chứng chỉ tự ký tạm và khởi động một instance kiểm thử HTTPS trên loopback với runtime riêng. Client xác minh chứng chỉ bằng CA được chỉ định, kiểm tra `/health`, yêu cầu đăng nhập Swagger và đọc OpenAPI thành công. Instance kiểm thử đã dừng sau khi kiểm tra; không để lại server HTTPS phụ.

Chưa kiểm tra truy cập từ một máy khác trong LAN. Khi triển khai LAN, cần tạo chứng chỉ cho IP/tên máy thực tế và cài tin cậy trên máy truy cập theo `README.md`.

## Phạm vi kết luận

- Đã đối chiếu lại **745 mục checksum** trong ba manifest nguồn; tất cả khớp. Artifact `output/` không bị sửa nội dung.
- Các luồng Predict, SHAP, persistence, REST API và Swagger đã chạy thật trên local.
- **Chưa gọi Gemini API thật trong lượt này:** môi trường local chưa có `GEMINI_API_KEY`. Kiểm thử Gemini dùng phản hồi giả và các báo cáo đã lưu; không chứng minh chất lượng phản hồi mới từ Google.
- Các CSV nguồn và validation/test đã từng được xem. Đây là kiểm chứng tái lập/tích hợp, không phải đánh giá độc lập mới về chất lượng phát hiện.
- Human review vẫn được tạm hoãn theo yêu cầu. Không suy từ trạng thái accepted tự động rằng nội dung đã được chuyên gia xác nhận.
