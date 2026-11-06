# Frontend NIDR

**NIDR** là viết tắt của **Network Intrusion Detection and Response**. Tên hiển thị được lấy từ `src/lib/brand.ts`.

FE dùng **Next.js App Router, React, TypeScript strict và Tailwind/CSS**, tổ chức theo frontend P-150 và giữ [giao diện Miro](https://miro.com/app/board/uXjVEU3YmTc=/?moveToWidget=3458764688660488795). Source đặt trong `FE/`; FastAPI ở `BE/` giữ toàn bộ dự đoán, SHAP, Gemini và lưu trữ.

## Chạy local

Dùng **Node.js 22.12 trở lên thuộc dòng 22**, npm và BE đã chạy ở `127.0.0.1:8000` theo [hướng dẫn BE](../BE/README.md). Không mở thêm BE dùng chung runtime.

```bash
cd /home/admin123/Desktop/dataocubuntu/do_an/DATN/FE
nvm use 22
npm ci
npm run dev -- --hostname 127.0.0.1 --port 3000
```

Mở **http://127.0.0.1:3000/login**, nhập `ADMIN_USERNAME` và `ADMIN_PASSWORD` trong `BE/.env`. Trang riêng tư tự chuyển tới form khi chưa có phiên. BE cần code **1.4.0** để nhận lựa chọn Ghi nhớ phiên; nếu BE đang chạy bản cũ, khởi động lại đúng process ở terminal của bạn, không mở thêm process dùng chung runtime. FE không có tài khoản hoặc Gemini key riêng.

Phiên dùng cookie HttpOnly, SameSite=Strict, có Secure trên HTTPS và hết hạn sau tối đa **8 giờ**. Nút **Đăng xuất** ở topbar thu hồi phiên tại BE. Restart BE cũng làm các phiên cũ hết hiệu lực; dữ liệu lần chạy vẫn được giữ. Không lưu mật khẩu/token vào localStorage hoặc sessionStorage. Swagger/CLI tiếp tục dùng HTTP Basic; khi dùng giao diện, ưu tiên đăng nhập bằng form để Đăng xuất quản lý trọn phiên cookie.

**Ghi nhớ phiên** mặc định tắt: cookie không có Max-Age/Expires. Khi bật, cookie được giữ trong thời hạn tám giờ để có thể mở lại trình duyệt; thời hạn BE vẫn tám giờ và logout/restart vẫn thu hồi phiên. Việc khôi phục session cookie còn phụ thuộc tùy chọn khôi phục phiên của trình duyệt. Placeholder `admin` chỉ là gợi ý tên đăng nhập. Quên mật khẩu mở hướng dẫn liên hệ quản trị, không giả lập chức năng gửi email. Nút N của Next dev được ẩn bằng devIndicators=false.

Các API/file dùng `/api/...` cùng origin. Next rewrites chuyển tiếp sang `http://127.0.0.1:8000` mặc định. Nếu BE dùng cổng khác, sao chép `.env.example` thành `.env.local` và sửa `API_PROXY_TARGET` trước khi chạy/build; đây là biến server-only, không chứa mật khẩu. Không mở Next dev ra LAN. Dev dùng SessionGate trước dashboard; production còn có Nginx auth_request. Login và bundle tĩnh công khai, dữ liệu API luôn yêu cầu xác thực.

## Bản production trên một server

```bash
cd /home/admin123/Desktop/dataocubuntu/do_an/DATN/FE
npm ci
npm run build
HOSTNAME=127.0.0.1 PORT=3000 npm run start
```

`postbuild` đóng gói `public/`, JS/CSS/font vào `.next/standalone/`; `start` dùng bản standalone. Cổng HTTPS triển khai là **Nginx → Next.js cho trang / FastAPI cho API**, cùng một máy. Nginx bảo vệ cả trang FE bằng tài khoản BE. Xem [deploy/README.md](deploy/README.md) và [deploy/nginx.conf](deploy/nginx.conf). Cấu hình đã được kiểm tra với instance tạm; không tự cài/reload Nginx vận hành.

## Tổ chức source

| Thư mục | Vai trò |
|---|---|
| `src/app/` | Layout, metadata, route App Router; page ghép component |
| `src/components/shared/` | Shell, dialog, tab, JSON, lỗi và tải tệp |
| `src/components/dashboard/` | Tổng quan và biểu đồ từ API tổng hợp |
| `src/components/runs/` | Lịch sử, upload, theo dõi Batch/Replay và xuất |
| `src/components/predictions/` | Bộ lọc, bảng, checkbox, khung xem nhanh |
| `src/components/explanations/` | Predict → SHAP → Gemini, bốn tab bằng chứng |
| `src/components/alerts/` | Tiếp nhận, ghi chú, đóng/mở lại và lịch sử |
| `src/lib/api/`, `src/types/` | Hàm REST có kiểu, hợp đồng request/response |
| `src/lib/use-polling.ts`, `use-action.ts` | Đọc tuần tự/hủy request; thao tác ghi chủ động |
| `src/store/` | Context cho theme, lựa chọn và ngữ cảnh bảng |
| `src/mocks/` | Fixture chỉ được import từ test |
| `design/` | Token, bố cục và ảnh Miro tham chiếu |
| `tests/browser_check.py` | Chrome + Nginx/Next/BE/model thật, Gemini giả lập |

Bản `index.html`, `assets/` và router hash cũ đã được bỏ. BE `/` chuyển tới Swagger; không còn phục vụ FE. Không có migration database hoặc thay artifact.

## Route và hành vi

- `/dashboard`: trang mặc định sau đăng nhập, bốn KPI, cột hoạt động xử lý/ngày kèm KDE khi đủ dữ liệu, pie tám lớp với nhãn trong chú giải, cảnh báo/run gần nhất và tiến độ giải thích/đánh giá. Bộ lọc ngày theo UTC+7, polling 15 giây; cần BE 1.7.0.
- `/runs`, `/runs/new`: lịch sử và CSV tối đa 1.000 dòng / 10 MiB.
- `/runs/[runId]/monitor`: tiến độ thật; Replay có tạm dừng/tiếp tục/dừng có xác nhận.
- `/runs/[runId]/predictions`: lọc, phân trang, chọn tối đa 50 dòng gồm Normal; checkbox độc lập xem nhanh. Cột thời điểm xử lý lấy `created_at`/`predict_seconds`; Batch ghi rõ thời gian bình quân.
- `/runs/[runId]/rows/[rowIndex]`: 46 đặc trưng, tám xác suất, SHAP top-5/phần còn lại, Gemini và metadata/lỗi. SHAP dùng PermutationExplainer trên toàn pipeline stacking; `shap_seconds` là giây và UI tự đổi đơn vị thời lượng.
- `/alerts`: ghi chú và nhật ký xử lý; đóng cần lý do, có thể mở lại.
- `/runs/[runId]/export`: tải CSV/ZIP; Markdown/PNG/JSON/top-5 CSV ở chi tiết mẫu.

Footer nền sáng theo token giao diện dùng chung cho các trang chức năng, đăng nhập và trang không tìm thấy; nội dung theo cột gồm NIDR, đơn vị đào tạo, nhóm thực hiện và liên kết nhanh. Component ở `src/components/shared/site-footer.tsx`, đặt cuối vùng cuộn của shell/public page. Thông tin nhóm lấy từ `Đề cương đồ án tốt nghiệp.docx`. Khối banner đề tài riêng của dashboard và component `project-footer.tsx` cũ đã được bỏ. Footer dùng màu panel/text/link hiện tại, tự thích ứng theme tối; sidebar chỉ giữ lối tắt API, không còn thẻ model đã chốt.

URL giữ bộ lọc, mức diễn giải, mẫu, bước/tab và đường quay về. Context/sessionStorage giữ lựa chọn và vị trí cuộn theo run. Theme và ID gần nhất nằm trong localStorage; không lưu credential/khóa API/ghi chú. Storage của origin/port cũ không tự chuyển sang origin mới; dữ liệu đã lưu ở BE vẫn giữ nguyên.

Polling chỉ GET, tuần tự khoảng 2,5 giây, tạm ngừng khi tab ẩn, hủy khi đổi mẫu/mức/trang. Mất mạng giữ kết quả cuối. Đổi mức Dễ hiểu/Kỹ thuật ở bảng/xuất hoặc mở trang không tự gọi SHAP/Gemini. POST/PATCH/PUT không tự retry; gọi lại Gemini là thao tác có xác nhận riêng. Hai mức dùng chung SHAP và có kết quả Gemini riêng; trang Giải thích một mẫu cố định Kỹ thuật.

Màn lịch sử chỉ hiện tên CSV; ID vẫn nằm trong đường dẫn/API để tra cứu. Topbar không hiển thị thông báo kết nối thành công. Khung xem nhanh và chi tiết cảnh báo đóng bằng nút ×; đóng panel không xóa dữ liệu hoặc đổi trạng thái cảnh báo. Gemini trong peek có **Xem thêm / Thu gọn**, đọc toàn bộ nội dung trong vùng cuộn riêng mà không gọi API lại. Trang chi tiết mẫu giữ diễn giải đầy đủ theo dạng báo cáo: nhận định, so sánh, bằng chứng SHAP, bảng giải thích đặc trưng, gợi ý kiểm tra và giới hạn. Màn hình rộng có hai cột; mobile dùng một cột. Hướng dẫn cố định theo lớp có mục mở rộng riêng.

Khung xem nhanh nhấn mạnh lớp dự đoán và xác suất đầu ra, giữ tám lớp đúng thứ tự và tô tím lớp đang dự đoán. **Xem toàn bộ kết quả** là nút duy nhất ở chân thẻ, mở trang Giải thích một mẫu tại bước Toàn pipeline, đúng dòng và mức Kỹ thuật. Trang đầy đủ có các bước Dự đoán, SHAP và Gemini. Điều hướng không tạo lời gọi Gemini; quay về bảng giữ các checkbox đã chọn. Gửi yêu cầu giải thích vẫn thực hiện từ thanh chọn mẫu hoặc trang chi tiết. Đã bỏ toggle Khung xem nhanh; bấm Xem nhanh ở mỗi dòng để mở, dấu × để đóng. Chỉ dòng được checkbox chọn mới có nền chọn.

Trang mẫu có vùng **Tệp kết quả của mẫu** để xem trước `explanation.json`, `report_vi.md`, `top5_features.csv`, `waterfall.png` và tải tệp đang xem. Báo cáo Markdown có **Bản trình bày / Văn bản gốc**; bản trình bày hỗ trợ nhấn mạnh, code, danh sách và bảng, bỏ HTML nhúng và chỉ tải ảnh waterfall của đúng mẫu. CSV trên UI rút gọn tối đa sáu chữ số thập phân (tác động: bốn), số khác 0 rất nhỏ dùng dạng khoa học; tệp tải giữ nguyên. Mục lục **Trên trang này** tự sáng theo vị trí cuộn giữa bước đang xem, tệp và đánh giá, độc lập với bộ chọn Toàn pipeline/Dự đoán/SHAP/Gemini. Cuộn không đổi bước, URL hoặc gửi yêu cầu giải thích. Phần **Đánh giá thủ công** cho nhập nhận định/nhãn đề xuất, ba điểm chất lượng tùy chọn và ghi chú. Điểm trống không tự thành đạt. Đánh dấu đã đối chiếu, bấm Lưu đánh giá để lưu SQLite, rồi tải JSON đã lưu. Tải lại bản đã lưu cần xác nhận nếu có nháp chưa lưu; mở trang không tự lưu/gọi Gemini. BE **1.5.0** trở lên cần được nạp lại trong terminal hiện có để dùng API này. Đánh giá là nội dung do người dùng nhập, không tự xác minh tư cách chuyên gia hoặc thay nhãn model.

Trang dự đoán nhóm bộ lọc/bảng bên trái, peek bên phải. **Đi tới dòng** nhận `14` hoặc `#000014`, chuyển đúng trang và mẫu đã dự đoán; không gửi yêu cầu giải thích. Thanh trong bảng biểu thị xác suất đầu ra. Thanh trong tab SHAP so sánh đóng góp top 3 theo đơn vị điểm phần trăm, cùng xác suất nền và số đặc trưng còn lại.

**Xuất kết quả & Báo cáo** có ba lựa chọn: CSV, gói ZIP và báo cáo từng mẫu. Danh mục hiển thị tám tệp nền trong ZIP, bao gồm `human_reviews.json`, cùng các tệp thực tế theo mẫu/mức diễn giải. CSV/ZIP tải toàn lần chạy; chọn mẫu/mức chỉ đổi danh mục báo cáo từng mẫu. Có thể tải Markdown/PNG và các dữ liệu giải thích đã lưu, gồm trạng thái/bản nháp khi có. Chưa hỗ trợ PDF; xuất tệp không chạy lại model, SHAP hoặc Gemini.

Thanh chọn nhiều mẫu dùng mức **Kỹ thuật** cố định khi gửi yêu cầu giải thích. Sau khi BE tiếp nhận, bảng chuyển sang mức Kỹ thuật để theo dõi kết quả. Bộ lọc mức diễn giải phía trên phục vụ việc đọc các báo cáo đã lưu.

## Kiểm tra

Từ `FE/`, dùng Node.js 22:

```bash
npm run lint
npm run typecheck
npm run test
npm run build
```

Từ repo root:

```bash
.venv/bin/python -m pytest BE/tests -q --disable-warnings
.venv/bin/python FE/tests/dev_proxy_check.py
.venv/bin/python FE/tests/browser_check.py
```

`dev_proxy_check.py` cần Node.js 22 và node_modules FE hiện có. Script tạo project Next dev tối thiểu trong thư mục tạm, dùng chính next.config.ts để kiểm tra auth/upload qua rewrites. Cổng, tài khoản, runtime và cache riêng; không đọc `.env`, không gọi Gemini, không cần Docker/Chrome cho kiểm tra này. Kết quả tại `tests/results/dev_proxy_checks.json`.

Browser suite cần bản `npm run build` mới nhất, Google Chrome/Chromium, Docker đang hoạt động và OpenSSL. Script sử dụng image `nginx:1.28-alpine`; chạy `docker pull nginx:1.28-alpine` trước nếu máy chưa có. Python dùng môi trường BE đã khóa. Kiểm thử mở BE/Next/Nginx/Chrome ở cổng tạm, runtime và tài khoản fixture riêng, rồi đóng/xóa khi kết thúc. Không đọc `BE/.env`, không dùng runtime vận hành và không gọi Gemini thật. Chứng chỉ tạm chỉ dùng trong kiểm thử; Chrome bỏ qua lỗi CA của chứng chỉ này, HTTP client xác minh CA tạm được chỉ định.

Kiểm tra riêng Next dev/Webpack và Fast Refresh: `.venv/bin/python FE/tests/dev_navigation_check.py` từ repo root. Script tạo bản sao FE tạm, dùng Node.js 22/Chrome và BE với tài khoản fixture, không cần build trước hoặc Docker. Thử chuyển trang và thêm/bớt hook trong bản sao để phát hiện lỗi React khi cập nhật nóng. Cả hai bộ kiểm tra đều thu thập `console.error` và ngoại lệ JavaScript; kết quả dev lưu tại `tests/results/dev-navigation/`. Không ghi đè `.next` của server đang chạy.

Kết quả và ảnh sinh trong `tests/results/` được Git bỏ qua. [VERIFICATION.md](VERIFICATION.md) ghi các kiểm tra thực tế và giới hạn; [PLAN.md](PLAN.md) lưu kế hoạch đã duyệt.

Phần **Giải thích và đánh giá** trên Tổng quan gồm bằng chứng SHAP, diễn giải Gemini qua kiểm tra tự động và phiếu đánh giá đã lưu, cùng số mẫu/tổng mẫu thật. Các trạng thái chi tiết vẫn mở được bên dưới. Đường KDE là ước lượng Gaussian từ tổng lượt xử lý theo ngày (Scott, bandwidth tối thiểu0,5ngày); chỉ vẽ khi ít nhất hai ngày có lượt, không phải dự báo hay thời điểm bắt gói. FE không dùng Seaborn ở runtime và không thay BE/model.
