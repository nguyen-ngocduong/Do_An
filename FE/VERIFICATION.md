# Kiểm chứng FE NIDR — Next.js

## Cột đứng theo lớp và KDE minh họa — 06/11/2026

Tab **Theo lớp** trong Số mẫu đã xử lý dùng trục X là tám nhãn cố định, trục Y là số mẫu, kèm số đếm trên cột và đường Gaussian KDE minh họa. Chiều cao tỷ lệ đúng với số đếm, lớp không có mẫu không được nâng thành cột tối thiểu. Đường KDE phụ thuộc thứ tự nhãn và được ghi rõ là minh họa; không biểu thị khoảng cách tự nhiên giữa các lớp. Giữ nguyên phần vẽ Theo ngày, helper KDE theo ngày và pie Phân bố nhãn dự đoán.

Lint, TypeScript, **68 test / 19 file** và build production đạt qua `scripts/check_frontend.py` trong bản sao tạm. Sau sửa đệm nhãn cho trường hợp chỉ có một mẫu, chạy lại **24 test tập trung đạt** và build Docker có kiểm tra TypeScript đạt. Năm điểm KDE được đối chiếu độc lập với SciPy trên tần số của 2.000 mẫu, khớp đến tám chữ số thập phân.

Chrome kiểm tra bản production ở sáng/tối, rộng 1440/768/390 px, dùng snapshot số liệu Docker chỉ đọc và session/API fixture: tám số đếm, tỷ lệ cột, vị trí nhãn, chuyển tab bằng bàn phím, bảng số liệu, KDE theo ngày và focus pie đạt; không có JS error. Đây là kiểm thử với fixture, không phải thao tác trên phiên đăng nhập thật. Taste inspector không có FAIL, còn hai WARN về khoảng trống của các thẻ ngoài phạm vi sửa này. Ảnh/bằng chứng nằm trong `tests/results/class-columns-kde-20261106/` (ignored).

Đã cập nhật riêng frontend Docker tại `localhost:8080` bằng quyền người dùng đã cấp: image `sha256:290e2bea08f4ee32c95d771c4d72d32cbf59e0e6a4b2b8207eba8f4637fd678e`, frontend healthy, `/login` trả 200, `/health` trả ready. Backend không khởi động lại; không thay volume hoặc gọi thêm Gemini. Container/proxy preview đã được dừng. Gói ZIP bàn giao tạo trước đó chưa được đóng lại với giao diện mới.

AGY hết thời gian sau bảy phút và để lại thay đổi một phần; Codex đọc diff rồi hoàn thiện biểu đồ, CSS và test. Không ghi nhận lượt AGY timeout là thành công.

## Sidebar, footer sáng và biểu đồ Tổng quan — 04/11/2026

Theo yêu cầu mới nhất, sidebar đã bỏ khối Model đã chốt/id/stacking, giữ menu rộng-gọn và lối tắt Swagger. Footer dùng panel/text/muted/primary/line của theme, có phân cách nhẹ và giữ đủ thông tin/link. Màu Navy cố định của các đợt trước đã được thay theo chỉ đạo mới; theme tối vẫn đi theo màu panel hiện có, không bật trắng cố định.

Giải thích và đánh giá tách thành component dashboard-pipeline: ba phần phẳng Bằng chứng SHAP, Diễn giải Gemini, Đánh giá của bạn, mô tả ngắn và số đã có/tổng mẫu với progress. SHAP dùng metrics.shap_rows, Gemini dùng accepted và ghi rõ kiểm tra tự động, review dùng saved_reviews; không coi phiếu lưu là nhãn thật. Chi tiết đầy đủ trạng thái tác vụ/Gemini/review vẫn có trong disclosure. Link mở đúng run đã chọn hoặc gần nhất, không dựng khi chưa có run. Progress0 dùng khoảng0–100 và aria-valuetext0/tổng, không sinh phần trăm NaN.

Pie giữ hình quạt, thứ tự8 lớp,0/100% đúng; bỏ chữ trong hình và đặt tên/số mẫu/tỷ lệ ở chú giải có header, nhấn nhẹ lớp lớn nhất. Không hard-code DDoS70%. Cột theo ngày giữ Normal/khác Normal, thêm đường Gaussian KDE trên thời gian ngày với multiplicity bằng số lượt. N là tổng lượt, phương sai mẫu Bessel, Scott h=std*N^-0.2 với mức tối thiểu 0,5 ngày; đường vẽ 121 điểm từ nửa ngày trước/sau vùng ngày. Giá trị y=sum(count_i*Gaussian((x-i)/h)/h), tương ứng lượt/ngày; không phải moving average/Bézier hoặc dự báo. Không vẽ khi có ít hơn 2 ngày có lượt hoặc N < 2, có thông báo. Đây là xấp xỉ từ tổng theo ngày, không biết thời điểm trong ngày. Đối chiếu công thức với [SciPy gaussian_kde](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gaussian_kde.html) và ý nghĩa đường phủ từ [Seaborn histplot](https://seaborn.pydata.org/generated/seaborn.histplot.html); frontendSVG không gọi literalPython kde=True.

**Lint/TypeScript,56 test FE/18 file, build production và43 nhóm Chrome đạt**, model/background thật, Gemini giả lập, model_load_count=1, không lỗi console/JS. Build/source/dependencies/runtime/cổng riêng trong thư mục tạm, không ghi FE/.next người dùng. Log /tmp/nidr-light-dashboard-browser.log; tests/results/browser_checks.json. Test mới kiểm tra0/ngày đơn/đa-ngày/largecounts, tính đối xứng, 70%/20%, pipeline/counts/runlink/status; tham chiếu số SciPy độc lập với np.repeat([0,2],[10,10]): h=.563549667943491, N*KDE tại1=2.9327128722832714.

Chrome thêm fixtureFE43groups: tổng 50, DDoS 35/DoS 10 và năm ngày có lượt,18 Gemini accepted/30 SHAP/11 phiếu, để xem KDE, pie70% và trạng thái điền đủ. Tạm bọc fetch GETdashboard chỉ trong trình duyệt kiểm thử, giữ API/run thật và khôi phục fetch/dữ liệu thật trước luồng tiếp theo. Tệp light-dashboard-fixture.json và ảnh light-dashboard-* được đánh dấu là fixture; không dùng làm bằng chứng mô hình hay kết quả Google Gemini. Những kiểm tra golden/upload/Replay/SHAP/review/cảnh báo/xuất/xóa/auth thật trên runtime tạm tiếp tục đạt. Sidebar không còn XGBoost/modeltext; footerbg khớp panel ở sáng/tối; disclosure mở được,KDE khi đủ điều kiện rõ, không gọi Gemini do xem dashboard.

**Page Agent live đã hoàn tất đọc** http://localhost:3000/dashboard: menu không còn thẻ mô hình, ba mục giải thích mới hiện và footer sáng. Không đăng nhập/tìm mật khẩu/chạy SHAP hoặc Gemini/lưu/xóa dữ liệu. Bằng chứng tests/results/page-agent-light-dashboard.json. Matrix rà soát .impeccable/review/light-dashboard gồm desktop1440/1280, tablet768, mobile390/320, dark, pipeline/details/footer.

AGY được giao task qua scripts/agy_frontend.py. Lượt đầu soft-denied đọc tài liệu craft-floor ngoài workspace dù CLI exit 0; runner từ chối nghiệm thu. Thêm --allow-read đúng file hướng dẫn trong profile từng phiên. Lượt sau ghi 9 file đúng phạm vi nhưng print_timeout 600 s (không coi đạt); Codex hoàn thiện CSS/copy/ARIA và sửa import/fixturetest sai kiểu. Không dùng bypasspermissions, không để timeout làm task dở. Report/diff ở .agent-runs/20261104-231326-946411/; đây là runtime Gitignored.

Taste rawreports còn palette-purple ở màu lớp/badge, rainbow-chart 7 hue và icon-chips 4 KPI đã có theo thiết kế trước/ngữ nghĩa taxonomy; headline 28 px thuộc hệ đã chốt. Đợt này giữ màu dữ liệu và KPI ngoài scope; không thêm suppression hoặc tuyên bố tất cả heuristic đạt. Không đọc BE/.env, restart dịch vụ, sửa BE/runtime/output hoặc fit/train mô hình.


Reviewer độc lập đã mở đủ 13 ảnh và source liên quan, kết luận **ship trong phạm vi thay đổi này**, không có sửa UI bắt buộc. Report: `../work_dir/Nguyen_Ngoc_Duong_18_light_dashboard_review.md`.

Documenter đã cập nhật `design/DESIGN.md`, `design/SURFACE.md` và `.impeccable/design.json` để mô tả footer theo theme và hành vi thực tế; giữ palette/token hiện có, kiểm tra parse YAML/JSON đạt. Báo cáo: `../work_dir/Nguyen_Ngoc_Duong_18_light_dashboard_documenter.md`. Drift PRODUCT.md cũ vẫn ngoài phạm vi.

## Hoàn thiện cách đọc bằng chứng theo video demo — 04/11/2026

Giữ bộ chọn từng bước XAI theo câu trả lời của người dùng; thêm mục lục Trên trang này tự sáng giữa nội dung bước đang xem, tệp kết quả và đánh giá thủ công. Các phần này nằm trong cùng vùng nội dung bên cạnh thanh bước sticky trên desktop; từ 1000 px trở xuống thanh bước/mục lục xếp phía trên để dành chiều ngang đọc. Không tự chuyển Dự đoán/SHAP/Gemini khi cuộn.

`report_vi.md` dùng react-markdown 10.1.0 và remark-gfm 4.0.1, có Bản trình bày / Văn bản gốc. Tiêu đề, nhấn mạnh, code, danh sách và bảng được render; HTML nhúng bị bỏ, URL script không được dùng, ảnh ngoài không tải và waterfall dùng đúng URL artifact của mẫu. Kiểm thử đối chiếu chế độ nguồn với toàn bộ nội dung HTTP gốc. Báo cáo đã lưu có thể còn câu chữ từ phiên bản cũ; UI không sửa nội dung artifact trong runtime.

CSV chỉ rút gọn hiển thị cột value/shap_value tối đa sáu chữ số thập phân, impact_percentage_points bốn; số khác 0 rất nhỏ dùng dạng khoa học. Cột số căn phải; không đổi tên feature/lớp hoặc giá trị trong tệp tải. Chrome đối chiếu data-raw-value của cả năm dòng với API CSV gốc và xác nhận phần hiển thị đã được định dạng. Bảng dự đoán thêm created_at/predict_seconds sẵn có, Batch ghi rõ thời gian bình quân, không tải feature theo từng dòng. Latest run chỉ có một bản ghi được bổ sung tóm tắt toàn run thật; không bịa thêm run hoặc dùng thống kê nhóm mẫu thay cho toàn run. Nhãn pie đặt theo centroid hình quạt, hai dòng cân quanh điểm đó; unit test gồm 70%/20% và 100%.

Đối chiếu video tại giây 67: giao diện cũ ghi **7,625 s**, artifact `shap_seconds=7.624732632000814`; BE đo bằng perf_counter theo giây. Không có bằng chứng phải chia 1000. Formatter mới hiện 7,62 giây, tự tính ms/µs/phút/giờ theo giá trị. SHAP trong `BE/shap_service.py` là **PermutationExplainer trên toàn pipeline stacking**, không phải TreeSHAP trên XGBoost. Nhãn phương pháp trên UI đã được làm rõ. Sai số bảo toàn không xác nhận nhãn thật hoặc chứng minh đã loại bỏ mọi hallucination.

**Lint/TypeScript, 44 test FE/16 file, production build và 42 nhóm Chrome đạt.** Build/Chrome dùng bản sao FE/runtime/cổng riêng, giữ nguyên cache dev người dùng; model/background thật, Gemini giả lập, model_load_count=1, không lỗi console/JavaScript. Kiểm tra scrollspy xác nhận aria-current đúng khi cuộn đến tệp/đánh giá, quay lên bằng mục lục giữ URL/stage và số lần gọi Gemini. Các luồng upload/Batch/Replay, SHAP, Gemini lỗi/cache, review, cảnh báo, xuất và xóa lịch sử tiếp tục đạt. Log cuối `/tmp/nidr-video-polish-browser.log`; kết quả `tests/results/browser_checks.json`. Một lượt chụp bổ sung trước đó lỗi selector của harness đã sửa và chạy lại; không tính lượt đó là đạt.

**Page Agent đã kiểm tra live dev** trên `http://localhost:3000`: dashboard có Thông tin toàn bộ lần chạy; mẫu #000000 của run đã lưu mở được báo cáo định dạng với hai chế độ; sau khi cuộn, mục lục active Đánh giá thủ công. Một lượt tiếp nối chọn nhầm tab Tạo lần chạy đã thất bại; mở lại URL mẫu rõ ràng thì kiểm tra hoàn tất. Đây là các thao tác đọc, không upload/chạy SHAP/Gemini/lưu review hoặc đăng nhập hộ. Bằng chứng `tests/results/page-agent-video-polish.json`.

Đã mở ảnh 1440, 768, 390, 320 px và theme tối, gồm Markdown/nguồn/CSV, mục lục, bảng và dashboard. Matrix review ở `.impeccable/review/video-polish/`; ảnh gốc và Taste raw reports trong `tests/results`. Không tràn ngang cấp trang hoặc chữ dưới 12 px trong suite. Không thêm suppression: h1 28 px/nhãn phụ 12 px theo hệ hiện có; độ cao bảng/peek khác nhau do vùng master-detail cuộn riêng. Probe tối tiếp tục ghi contrast hai link trong playbook đang đóng như đợt trước; kiểm tra mở playbook trong suite vẫn đạt màu link thật. Không tuyên bố mọi heuristic đạt hoặc sửa drift PRODUCT.md ngoài phạm vi.


Reviewer độc lập đã đọc đủ 11 capture cuối và source liên quan, kết luận **ship trong phạm vi refinement theo video**, không có sửa đổi bắt buộc; review tại `../work_dir/Nguyen_Ngoc_Duong_16_video_polish_review.md`. Hai lượt CLI AGY review/documenter không trả kết quả đã được dừng (`error: interrupted`); không dùng chúng làm bằng chứng đạt. Sau đó dùng reviewer/documenter độc lập qua công cụ agent của phiên để hoàn tất. Documenter chỉ cập nhật `design/SURFACE.md`, giữ DESIGN.md và sidecar; báo cáo `../work_dir/Nguyen_Ngoc_Duong_16_video_polish_documenter.md`.

## Footer dùng chung toàn website theo PTIT — 04/11/2026

Người dùng bác bỏ footer dạng thẻ đề cương riêng dashboard và yêu cầu footer toàn website. Đã xem `https://ptit.edu.vn/`, đọc footer HTML công khai và chụp ảnh tham chiếu tại `design/reference/ptit-footer.png` (1440×1000; sidecar ghi nguồn). Thiết kế mới là dải navy phẳng, không bo khung/badge/avatar/card sinh viên, chia bốn cột nhận diện NIDR, đơn vị đào tạo, nhóm thực hiện và liên kết nhanh. Cỡ ≤1100 px chia hai cột; ≤600 px một cột. Nội dung vẫn là thông tin NIDR đã đối chiếu đề cương; không lấy email/địa chỉ PTIT làm kênh hỗ trợ của nhóm.

`shared/site-footer.tsx` được dùng tại OperationalShell, LoginForm và trang 404. Khối cũ trong dashboard cùng `dashboard/project-footer.tsx` và CSS riêng đã được bỏ. Footer ở cuối nội dung cuộn, không cố định đè thao tác; trang ngắn giữ footer ở đáy, trang dài cuộn tới cuối mới thấy. Login giữ form trong viewport đầu, footer ở sau. Logo/liên kết thật, không tạo social account hoặc placeholder.

**Lint/TypeScript, 38 test FE/13 file, production build và 41 nhóm Chrome đạt.** Browser xác nhận đúng một footer trên dashboard, lịch sử, tạo run, cảnh báo, theo dõi, dự đoán, chi tiết mẫu, xuất, login và 404. Bốn liên kết nội bộ được click tới đúng route; xem footer/điều hướng không gọi Gemini. Upload/Replay/SHAP/review/xuất/xóa tiếp tục đạt, không lỗi console/JavaScript, model_load_count=1; model/background thật và Gemini giả lập. Build và browser dùng bản sao/runtime tạm; không sửa BE, đọc .env, restart server hoặc thay artifact. Log cuối: `/tmp/nidr-site-footer-browser-final.log`; `tests/results/browser_checks.json` ghi 41 nhóm.

Trang mobile dài nay có scrollbar do footer: phép kiểm tra tâm dialog xóa dùng `document.documentElement.clientWidth` (vùng layout thực) thay vì `innerWidth` có cả rãnh scrollbar. Ảnh xác nhận hộp thoại vẫn ở tâm; không sửa CSS dialog hoặc nới sai số 2 px. Helper chờ dữ liệu và cuộn tới cuối main để ảnh footer ở Cảnh báo không bị chụp trước khi bảng tải xong.

Đã mở ảnh footer desktop/sáng/tối, mobile 390/320 và các route khác. Matrix cuối tại `.impeccable/review/site-footer/` và ảnh gốc `tests/results/site-footer-*.png`, `dashboard-footer-*.png`; login/404 có ảnh riêng. Taste giữ kết quả thô; không tuyên bố mọi heuristic đạt. Hook scan SiteFooter không có finding xác định; hook Login ngừng gợi ý sau >6 lần sửa trong session, không được coi là một lượt audit mới. Không thêm suppression. Tham chiếu cũ và các kết quả bên dưới là lịch sử; footer dạng thẻ không còn là thiết kế hiện tại.

Agent phụ Codex chạm giới hạn sử dụng trước khi thực hiện review/tài liệu. Đã thay bằng fresh review qua `agy --print` theo yêu cầu người dùng: đọc ảnh bị bác bỏ, tham chiếu PTIT, 13 capture cuối và source, trả **disposition: ship**, không có material fix. Review đầy đủ ở `work_dir/Nguyen_Ngoc_Duong_15_site_footer_review.md`. Agy cập nhật `design/SURFACE.md` và phần Site Footer trong `design/DESIGN.md`, giữ token/sidecar và PRODUCT drift cũ. Fingerprint sáu file UI khớp bản đã kiểm thử sau handoff; không có source UI thay đổi sau lượt 41 nhóm Chrome.

## Dashboard theo ảnh người dùng và footer đồ án — 04/11/2026

Tham chiếu là hai ảnh người dùng gửi, lưu tại `design/reference/dashboard-user-overview.png`, `dashboard-user-lower.png`; nguồn và checksum đi kèm. Giữ hệ Adminator, bố cục dashboard gọn hơn: bộ lọc/cập nhật chung một thẻ, KPI có đơn vị/icon, biểu đồ tròn với chú giải đủ tám lớp, thanh tiến độ trong run gần nhất, hai bảng rồi Giải thích và đánh giá. Cỡ 1024 px giữ bốn KPI trên một hàng và hai biểu đồ; tablet/điện thoại xếp lại khi thiếu chỗ. Không sao chép số liệu, độ tin cậy giả hoặc tuyên bố Normal là an toàn từ ảnh minh họa.

Footer Dark Navy ngay dưới Giải thích và đánh giá, hai phần trên desktop và xếp dọc trên màn hình nhỏ. Badge 14 px theo yêu cầu; tên đề tài nguyên văn, ngành Kỹ thuật Điện tử Viễn thông, hệ Chính quy, khóa 2022–2026 và ba sinh viên/mã/lớp lấy từ `Đề cương đồ án tốt nghiệp.docx`. Logo dùng ShieldCheck/NIDR hiện có. Không có ảnh trang trí mới hoặc logo học viện tự chế. Màu footer giữ tương phản ở cả hai theme.

**Lint, TypeScript, 38 test FE/13 file, build và 40 nhóm Chrome đạt.** Hai test chart mới kiểm tra đủ tám lớp/thứ tự, phần trên tổng, dữ liệu trống không tạo NaN/tỷ lệ giả và trường hợp 100% thuộc một lớp. Chrome đối chiếu tổng pie với API, đủ ba sinh viên/mã/lớp, cỡ 1024 px không rơi KPI sang hai hàng, bộ lọc vẫn đủ rộng ở tablet. Luồng upload/Replay/giải thích/review/xuất/xóa tiếp tục đạt; model/background thật, Gemini giả lập, model_load_count=1, không lỗi JavaScript/console. Log: `/tmp/nidr-dashboard-footer-browser.log`, kết quả `tests/results/browser_checks.json`. Không sửa BE, retrain, đọc .env hay restart server người dùng; build/browser dùng bản sao FE/runtime tạm.

Ảnh kiểm tra gồm desktop 1440/1280, cỡ tham chiếu 1024, tablet 768, mobile 390/320, theme tối, trống và pipeline có lỗi Gemini/phiếu đã lưu. `dashboard-footer-desktop.png`, `dashboard-footer-dark.png`, `dashboard-footer-mobile-topic.png`, `dashboard-footer-mobile-team.png`, `dashboard-footer-mobile-small.png` ghi phần chân trang; `dashboard-lower-desktop.png` ghi quan hệ hai bảng với pipeline. Helper cuộn vùng main ở desktop để tránh kéo cả shell ra ngoài viewport khi chụp. Ảnh trước thay đổi được giữ trong `tests/results/dashboard-before-footer/`.

Review độc lập đầy đủ xác nhận footer/thông tin nhóm/responsive phù hợp và yêu cầu giảm khoảng 60–80 px trước hai bảng. Đã giảm padding/khoảng cách của toolbar, KPI, chart và chiều cao vùng vẽ (giữ chữ 12 px thực); ảnh 1440/1280 sau sửa thấy rõ tiêu đề cả hai bảng ngay trong viewport đầu. Browser thêm điều kiện đo đáy hai tiêu đề không vượt chiều cao 900 px, đồng thời giữ phép kiểm tra một hàng KPI ở cỡ 1024. Build và 40 nhóm Chrome sau correction tiếp tục đạt. Reviewer đọc capture cuối, chấm **resolved**, disposition **ship** cho bản sửa mật độ; đây không phải một vòng audit toàn màn hình mới.

Taste giữ báo cáo thô `tests/results/taste-dashboard-*.json`; không tuyên bố tất cả heuristic đạt. Dark Navy, hai badge và ba thẻ sinh viên là yêu cầu rõ của người dùng; màu nhiều lớp phục vụ biểu đồ, không phải đổi thương hiệu toàn ứng dụng. Hook không báo lỗi xác định ở footer/kiểm thử chart; không thêm suppression mới.

Documenter đã cập nhật `design/SURFACE.md` với pie/phạm vi footer/breakpoint và sửa đúng một bullet `design/DESIGN.md` để ghi `--shadow-subtle` hiện dùng ở KPI dashboard. Giữ nguyên token và `.impeccable/design.json`. Drift PRODUCT.md cũ tiếp tục được ghi nhận, không mở rộng phạm vi sửa.

## Dashboard Tổng quan — 04/11/2026

Thêm `/dashboard` và mục **Tổng quan** đầu menu, dùng lại hệ màu/chữ/shell Adminator. Đăng nhập không có `next` mở dashboard; deep-link hợp lệ vẫn giữ trang đích. Trang có bộ lọc Hôm nay/7 ngày/30 ngày/Toàn bộ lịch sử và lần chạy, bốn KPI, biểu đồ ngày/tám lớp, cảnh báo/run gần nhất và tổng hợp SHAP/Gemini/phiếu đánh giá đã lưu. Không tổng hợp từ trang kết quả giới hạn 20 dòng: một request đọc `GET /api/dashboard` của BE 1.7.0 trả số liệu đầy đủ trong phạm vi chọn.

Phạm vi mẫu dùng thời điểm xử lý theo ngày UTC+7; trạng thái cảnh báo/giải thích/đánh giá là trạng thái hiện tại của nhóm mẫu đó. Toàn lịch sử có tổng đầy đủ nhưng biểu đồ ngày chỉ 30 ngày gần nhất, ghi rõ trên UI. SHAP đếm một lần mỗi mẫu có artifact dùng chung, kể cả khi Gemini lỗi; Gemini và phiếu đánh giá tổng hợp mức Kỹ thuật. Phiếu đã lưu không đồng nghĩa chuyên gia đã xác nhận nhãn thật hoặc còn phù hợp với bằng chứng mới. Không hiển thị accuracy, token/cost hoặc thời gian mô phỏng thành dữ liệu thực đo.

**Lint/TypeScript, 36 test FE trên 13 file, 56 test BE và production build đạt.** Build chạy trên bản sao FE tạm, không ghi đè `.next` của dev. **39 nhóm Chrome đạt**, dùng model/background thật, Gemini giả lập, model_load_count=1, không lỗi JavaScript/console. Bao gồm dashboard trống, 50 mẫu, đối chiếu API, bộ lọc giữ qua reload, tám lớp/ngày trống, mở bảng dữ liệu ngày, mặc định sau đăng nhập và tổng hợp sau lỗi Gemini/phiếu đã lưu. Các luồng upload, Replay, SHAP, review, xuất và xóa lịch sử tiếp tục đạt. Log: `/tmp/nidr-dashboard-backend.log`, `/tmp/nidr-dashboard-browser.log`; kết quả: `tests/results/browser_checks.json`.

**Dev/Webpack: 17 lượt điều hướng và thêm/bớt hook qua Fast Refresh đạt**, dùng bản sao/runtime riêng; không lỗi console/JavaScript. Kết quả ở `tests/results/dev-navigation/result.json`, log `/tmp/nidr-dashboard-dev.log`. Không tuyên bố đã xác định nguyên nhân cảnh báo `use()` lịch sử.

Ảnh dashboard gồm 1440/1280, tablet 768, mobile 390 và 320 px, theme tối, trạng thái trống và đã có lỗi Gemini/phiếu đánh giá. Biểu đồ giữ chữ ở kích thước CSS thực thay vì thu nhỏ toàn SVG; ngày có thể chọn bằng bàn phím và đọc qua bảng dữ liệu. Ảnh `dashboard-mobile-pipeline-filled.png` đã được chụp lại sau khi đổi viewport trước khi cuộn, để thấy đủ tác vụ/Gemini/đánh giá thay vì chụp nhầm đầu trang.

Review độc lập phát hiện bộ lọc lần chạy bị ép hẹp ở tablet 768 px. Đã chuyển bộ lọc thành một cột từ 1000 px; thêm kiểm tra chiều rộng select tối thiểu 320 px tại viewport 768 và ảnh `dashboard-tablet-selected.png` với tên CSV thật đang chọn. Giữ bố cục ba cột ở desktop rộng. Browser/build sau sửa tiếp tục đạt 39 nhóm. Reviewer đọc hai ảnh tablet mới và chấm vấn đề này **resolved**, verdict **ship** trong phạm vi bản sửa; đây không phải một lượt review toàn màn hình mới. Lượt review đầy đủ trước đó đã đọc đủ 12 capture và chỉ yêu cầu sửa ô chọn này.

**Page Agent: kiểm tra một phần, chưa đạt lượt đọc kết quả đầy đủ.** Ban đầu extension mở dashboard và được chuyển về đăng nhập; đã báo đúng trạng thái, không tìm mật khẩu. Sau khi người dùng xác nhận restart BE/đăng nhập, Page Agent thao tác bộ lọc; metadata Next.js xác nhận route có `period=30d` và run đã chọn. Hai lượt đọc lại kết quả bị timeout 180 giây và được hủy; không coi đó là phép kiểm tra KPI đã đạt. Client MCP đã đóng, không restart server người dùng hoặc gửi yêu cầu upload/SHAP/Gemini/review/xóa/đăng xuất trên dữ liệu đang dùng. Bằng chứng: `tests/results/page-agent-dashboard.json`. MCP Next.js khi kiểm tra không có lỗi hoạt động (`configErrors=[]`, `sessionErrors=[]`).

Taste giữ báo cáo thô trong `tests/results/taste-dashboard-*.json`: màu tím còn ở nhãn lớp Recon/Spoofing, không phải màu thương hiệu; nhãn phụ 12 px và tiêu đề 28 px theo hệ chữ vận hành hiện có. Không thay màu lớp hoặc thêm suppression để làm xanh detector. Hook Impeccable không báo lỗi xác định ở hai component dashboard mới. Giới hạn API/snapshot và cách đếm artifact được ghi trong `BE/README.md`, `BE/VERIFICATION.md`.

Documenter đã đối chiếu CSS/component/capture với hệ Adminator và cập nhật `design/SURFACE.md` cho tác vụ Tổng quan. Giữ nguyên token-bearing `design/DESIGN.md` và `.impeccable/design.json` vì đây là mở rộng tác vụ, không thay nhận diện. Drift `PRODUCT.md` cũ (IoT Sentinel/HTML thuần/Human review tạm hoãn) được ghi nhận, không sửa ngoài phạm vi.

## Giao diện theo Adminator — 03/11/2026

Người dùng chọn preview.colorlib.com/theme/adminator/index.html làm tham chiếu diện mạo mới và yêu cầu đổi Hợp đồng đầu vào thành Đầu vào. Đã mở trang tham chiếu bằng Chrome 1440 × 1000; ảnh gốc và nguồn ở design/README.md. Source Next.js giữ nguyên tổ chức, API và tác vụ; chỉnh token/bố cục trong globals.css và tiêu đề panel upload. Không nhập framework giao diện khác, thêm số liệu kinh doanh của demo hoặc sửa BE/model/artifacts.

Thay khung trắng bao quanh toàn trang bằng canvas xám xanh #f1f5f9, sidebar/header trắng, sidebar 248/88 px, header 60 px. Hành động dùng #2563eb; theme tối xanh than và liên kết #93c5fd. Các thẻ, bảng, form, tab, export và login dùng chung nhận diện mới. Cập nhật kiểm tra chiều rộng menu và màu link theo token hiện tại; bổ sung xác nhận panel Đầu vào và canvas không có khung bao cũ.

**Lint/TypeScript, 33 test FE/11 file, production build và 36 nhóm Chrome đạt.** Model/background thật, Gemini giả lập, model_load_count=1; không lỗi console/JavaScript. Build/browser chạy trên bản sao FE tạm để không đụng cache .next của dev đang mở. Log /tmp/nidr-adminator-check.log, kết quả tests/results/browser_checks.json. Luồng upload/Batch/Replay, lựa chọn và khung xem nhanh, SHAP/Gemini, Human review, lifecycle cảnh báo, tải báo cáo và xóa lịch sử tiếp tục đạt.

**Dev/Webpack: 13 lần chuyển trang và thêm/bớt hook qua Fast Refresh đạt**, không lỗi console/JavaScript; dùng bản sao/runtime/cổng riêng. Log /tmp/nidr-adminator-dev-check.log, tests/results/dev-navigation/result.json. Kết quả này không xác định nguyên nhân cảnh báo use() cũ đã báo trước đó.

Đã xem ảnh desktop/tablet/mobile/theme tối. Reviewer độc lập xét 11 capture với tham chiếu và direction contract, trả **ship**, không có material fix. Các ảnh thuộc kiểm thử dữ liệu thật và phản hồi Gemini giả lập, không phải kết quả Google API. Không tràn ngang cấp trang hoặc chữ dưới 12 px trong các capture của suite.

Taste đo runtime trong Chrome và giữ raw reports: không còn palette-purple cho màu nhận diện. Các cảnh báo 28 px title, chữ phụ 12 px/monospace ID và chiều cao bảng so với peek được đánh giá theo UI vận hành. Login giữ radial/bóng mềm do người dùng yêu cầu trước đó; detector vẫn ghi gradient/heavy-shadow. Closed playbook ở nền tối có thể giữ màu computed cũ trong probe; suite mở và xác nhận link bằng màu menu active thực tế. Không thêm suppression hoặc tuyên bố toàn bộ detector đạt.

Documenter đã cập nhật design/DESIGN.md, design/SURFACE.md và .impeccable/design.json theo CSS thực tế. YAML/JSON schema và tham chiếu token được kiểm tra. PRODUCT.md cũ còn ghi IoT Sentinel/plain HTML; đây là drift đã có trước, không sửa ngoài phạm vi đợt giao diện này.

## Điều tra cảnh báo conditional use() — 03/11/2026

Người dùng báo Console Error “This library called use() to suspend ...” trên Next.js 16.4.3/Webpack. Đã tìm thấy thông báo trong log development của server vận hành; bản ghi không kèm component stack. MCP Next đang ghi trang /alerts nhưng get_errors không có lỗi đang hoạt động. FE không gọi trực tiếp React.use; các hook điều hướng Next có sử dụng API đó bên trong. Chưa đủ bằng chứng xác định component/nguyên nhân hoặc khẳng định đã sửa dứt điểm. Không tắt StrictMode, che console, sửa node_modules hoặc đổi phiên bản thư viện để né cảnh báo.

Bổ sung thu thập Runtime.consoleAPICalled loại error vào Browser, vì trước đó chỉ thu ngoại lệ Runtime.exceptionThrown. React có thể báo lỗi qua console.error mà không ném ngoại lệ. Production build trên bản sao tạm và 36 nhóm browser đạt với bộ thu mới; không lỗi console/JavaScript, model_load_count=1, Gemini giả lập.

Thêm dev_navigation_check.py: Next dev/Webpack, Chrome và BE/model thật trên cổng/runtime/tài khoản fixture riêng. Đăng nhập, chuyển 13 lần giữa Cảnh báo/Lịch sử/Tạo lần chạy và thêm/bớt hook trong bản sao Alerts để thử Fast Refresh. Đạt, không lỗi console/JavaScript; chưa tái hiện được cảnh báo người dùng báo. Không sửa dữ liệu server vận hành, đọc BE/.env hoặc gọi Gemini thật; không ghi đè .next hiện có. Kết quả tests/results/dev-navigation/result.json; log /tmp/nidr-dev-navigation-check.log. Bản production kiểm tra tại /tmp/nidr-console-browser-check.log.

Các lần dựng thử dev qua Nginx production gặp HMR/hydration chưa sẵn sàng, nên không dùng làm bằng chứng đạt của chế độ dev. Bài dev hoàn tất dùng trực tiếp cổng Next loopback, chờ form được hydrate trước khi nhập/gửi. Khi gặp lại cảnh báo cần lấy Call Stack sau tải lại hoàn toàn để phân biệt lỗi còn lặp lại với thông báo của lần render trước.

## Trung tâm cảnh báo theo ảnh Stitch — 03/11/2026

Trang Cảnh báo có bốn tổng thật từ REST API, phạm vi theo lớp/run và gồm mọi trạng thái. Bảng chỉ in mã mẫu, trạng thái dòng đang xem và phân trang; UUID chuyển vào Thông tin lần chạy mở theo nhu cầu. Thẻ chi tiết chia header/body, nhãn/xác suất/model nguồn, trạng thái XAI/Gemini có tên, liên kết xem kết quả, bộ đếm ghi chú và thao tác. Playbook/lịch sử mở rộng; desktop cuộn riêng trong thẻ, mobile chuyển dưới bảng. Không thêm PCAP, chỉ số độ tin cậy hay model minh họa của ảnh Stitch vào dữ liệu thật.

Lint/TypeScript, **33 test FE trên 11 file và production build đạt**. Hai test API mới kiểm tra số tổng vượt phạm vi trang, giữ lớp/run, chỉ dùng GET và không trả số 0 giả khi lỗi. Build dùng bản sao FE tạm, không ghi đè .next của dev đang chạy. Không sửa BE, đọc .env hoặc gọi Gemini thật.

Browser suite Chrome đạt **36 nhóm**, dùng frozen model/background thật và Gemini giả lập, model_load_count=1, không lỗi JavaScript. Có đối chiếu bốn tổng với API sau khi lọc DDoS, cột đầu chỉ khớp mã #000000, kiểm tra bộ đếm ghi chú, lưu/tiếp nhận/đóng có xác nhận/mở lại, thông tin run và lịch sử mở được. Các luồng upload, dự đoán/SHAP, Gemini cache/lỗi, Human review, xuất tệp và xóa lịch sử tiếp tục đạt. Log: `/tmp/nidr-alerts-ui-check.log`; dữ liệu kiểm thử ở runtime tạm.

Đã xem ảnh desktop 1280/1440, tablet 768, mobile 390 và nền tối, gồm trạng thái cuộn nội dung thẻ. Bộ kiểm tra không phát hiện tràn ngang cấp trang hoặc chữ dưới 12 px. Ảnh và các phép đo Taste của Alerts lưu trong tests/results; ảnh chờ toast lưu tự ẩn để không che nội dung.

Taste giữ kết quả thô, không tuyên bố đạt toàn bộ: palette-purple là nhận diện người dùng đã chốt; small-title 24 px và tiny-text ở nhãn phụ 12 px theo hệ chữ ứng dụng hiện có. Probe nền tối khi playbook đóng ghi màu chuyển tiếp cũ của hai link nguồn; khi mở playbook, Chrome xác nhận màu thực tế rgb(196,181,253), phép đo alerts-dark-playbook không còn lỗi contrast. Không sửa palette hoặc thêm suppression để làm xanh detector. Hook Impeccable không báo lỗi xác định ở component Alerts mới.

## Tải dữ liệu khi Page Agent mở tab nền — 03/11/2026

Page Agent tạo tab với active=false. Trước sửa, usePolling bỏ cả request đầu khi document.hidden; SessionGate không có session/error nên dashboard giữ Đang tải. Hai regression test mới đã tái hiện thất bại trước sửa. Sau sửa, request đầu khi mount/đổi key/refresh vẫn chạy ở tab nền; polling định kỳ tiếp tục dừng khi ẩn và khôi phục khi visible. Request cũ vẫn abort/không ghi đè dữ liệu mới, không tự gửi thao tác ghi.

**Lint/TypeScript và 31 test FE đạt. Production build đạt trên bản sao FE tạm**, dùng cùng dependencies đã cài và không đụng cache .next của server dev đang chạy. Browser suite bản build tạm đạt **35 nhóm, exit 0**, thêm Chrome target nền thật với document.hidden=true: tải cookie session, sidebar và lịch sử trống mà không cần kích hoạt tab. Toàn bộ chức năng cũ tiếp tục đạt; không lỗi JavaScript; model_load_count=1; Gemini của suite là giả lập. Log `/tmp/nidr-page-agent-fe-check.log`; kết quả/ảnh được chép về tests/results trước khi dọn bản build tạm.

Page Agent MCP + extension 1.12.4 được thử riêng qua model do người dùng cấu hình trong extension và báo thao tác sidebar/Lịch sử thành công. Đây là kiểm tra điều hướng, không phải thực nghiệm chất lượng Gemini XAI. Không đọc BE/.env, sửa BE, gọi diễn giải Gemini của NIDR hoặc restart server vận hành. Hướng dẫn và các lỗi Base URL/Hub cache được ghi trong ../docs-md/PAGE_AGENT_SETUP.md.

## Sidebar rộng/gọn và xóa lịch sử — 03/11/2026

Sidebar desktop có nút ba gạch chuyển 228/88 px, icon Lucide 24 px và nhãn ngắn, lưu tùy chọn trong trình duyệt; mobile dùng Menu riêng. NIDR chuyển sang topbar khi gọn; Swagger giữ tên truy cập đầy đủ dù nhãn dài ẩn. Lịch sử có nút Xóa và dialog xác nhận tên/timestamp/phạm vi dữ liệu, nút đỏ, Hủy là lựa chọn đầu tiên. Dialog căn giữa viewport, cuộn khi cần và hỗ trợ tên tệp dài. Xóa thành công dọn last-run/lựa chọn của đúng run; cập nhật danh sách và trang. Không tự retry DELETE; BE cũ trả 405 có hướng dẫn khởi động lại.

**Lint, TypeScript, production build, 29 test FE/10 file và 51 test BE đạt. Browser suite cuối đạt 34 nhóm, exit 0** (`/tmp/nidr-history-browser-final.log`, `tests/results/browser_checks.json`). Model nạp một lần; artifacts/model/SHAP thật, Gemini giả lập. Không đọc .env, gọi Google hoặc restart server vận hành.

Browser thực hiện: thu gọn tăng vùng nội dung 140 px; giữ qua điều hướng/reload; phím Enter mở rộng; Menu mobile độc lập; xem sáng/tối và tablet. Khi kiểm tra Enter qua CDP phải gửi cả ký tự carriage-return để Chrome chạy hành vi button gốc; không thêm handler bàn phím giả vào ứng dụng. Nút Swagger có aria-label/tooltip ở thanh gọn.

Với xóa lịch sử, chọn một run fixture thật, mở bảng để tạo last-run/lựa chọn trong storage rồi về lịch sử. Hủy giữ nguyên dữ liệu; xác nhận trả 404 khi đọc lại đúng run, thư mục runtime bị dọn, last-run/lựa chọn không còn, run khác vẫn mở được. Dialog đo tâm ở desktop/mobile lệch dưới 2 px. Chỉ xóa dữ liệu runtime tạm của kiểm thử.

Đã xem ảnh `sidebar-expanded-desktop.png`, `sidebar-collapsed-desktop.png`, `sidebar-collapsed-tablet.png`, `sidebar-collapsed-mobile.png`, `history-delete-confirm-desktop.png` và `history-delete-confirm-mobile.png`. Ảnh theme tối và bản gọn 1920 cũng được lưu. Font hiển thị tối thiểu 12 px, không tràn ngang cấp trang. Chữ Xóa sáng #b91c1c có tương phản khoảng 5,84:1 trên nền hover #f3f3f6; CTA trắng trên đỏ cũng đạt AA.

Taste tiếp tục đo app qua phiên CDP đã xác thực, có thêm sáu trạng thái sidebar và ba trạng thái xóa; không có FAIL mới ngoài màu tím đã chốt trên các màn này. Các cảnh báo tiêu đề 24 px/nhãn phụ/monospace và canvas lịch sử ít dữ liệu vẫn được phân loại theo mục polish trước. Không thêm suppression Impeccable; không chạy lại detector audit ngoài hook đang bật.

API xóa cần **BE 1.6.0**; process BE đang chạy phải được người dùng khởi động lại để nạp route mới. `files_deleted=false` giữ cảnh báo rõ ràng trên UI; phần giới hạn dọn tệp và transaction được ghi trong BE/README.md và BE/VERIFICATION.md.

## Hoàn thiện UI bằng Taste Skill và Impeccable — 03/11/2026

Áp dụng Taste app screens `framed-sheet`, seed `623988554` (devtools, giữ palette/type) và Impeccable polish/craft floor. Thay đổi ở globals.css, OperationalShell, hai cột số của lịch sử/dự đoán và browser_check.py. Khung điều hướng trung tính, vùng làm việc riêng, chữ bảng 13 px, panel bớt bóng, theme tối nền than; mobile có Menu hỗ trợ Escape/trả focus. Bộ lọc trên tablet và khi mở peek trên laptop đổi thành hai cột. Không sửa BE hoặc pipeline.

**Lint, TypeScript, 26 test FE và production build đạt. Browser suite bản cuối đạt 32 nhóm**, có thêm kiểm tra Menu mobile mở/đóng/chọn trang/Escape. Kiểm tra Batch/Replay, phân trang, giữ lựa chọn/cuộn, SHAP thật, Gemini giả lập, JSON/CSV/Markdown/PNG, Human review lưu/reload/tải JSON, cảnh báo và xuất ZIP/CSV đều đạt. Không lỗi JavaScript; `model_load_count=1`. Model/background/artifacts thật, runtime tạm, không gọi Google hoặc restart server của người dùng. Không chạy lại pytest BE vì không sửa backend.

Taste static lint đã chạy trên FE/src. CLI inspector chạy login production trên Chrome thật ở **1440/768/390**; với các trang cần đăng nhập, dùng chính probe/layout/app và judge/APP_SKIP của Taste trong phiên CDP đã xác thực của browser suite (không bỏ xác thực). Có **22 bản đo runtime**, lưu `tests/results/taste-*.json`; CLI login lưu `tests/results/taste-login/report.json`. Đây là phép đo DOM và ảnh ở trạng thái được chụp, không phải chứng nhận UX toàn diện. Ảnh upload và prediction có đủ 1440/768/390; các màn còn lại có desktop/mobile, một số có theme tối. Đã trực tiếp xem ảnh upload, monitor, predictions, báo cáo Gemini, alerts và export tối.

Các kết quả Taste thô vẫn được giữ, **không tuyên bố bộ quy tắc Taste đạt hoàn toàn**:

- `palette-purple`/static `purple`: giữ màu thương hiệu người dùng đã chốt; không đổi nhận diện để làm xanh detector.
- `gradient`, `heavy-shadow` chỉ ở login: nền radial và bóng card là yêu cầu trước đó của người dùng. Các panel vận hành đã bỏ bóng lặp lại.
- `small-title`: detector trang giới thiệu cảnh báo tiêu đề 24 px; app guideline của cùng skill cho phép 20–24 px. Giữ cỡ phù hợp dashboard.
- `tiny-text`: nhãn phụ/metadata 12 px và danh sách đặc trưng làm tỷ lệ dưới 13 px cao. Dữ liệu bảng 13 px, thân bài 14 px; browser suite xác minh không có chữ hiển thị dưới 12 px. Không có lỗi contrast do probe báo.
- `mono`: ID, khóa đặc trưng và dữ liệu JSON/code cần truy vết; giữ monospace đúng ngữ cảnh. Không dùng nó cho văn xuôi báo cáo.
- `hero-void` ở login và `panel-void` ở lịch sử: canvas toàn viewport có khoảng trống khi ít bản ghi, không thêm dữ liệu giả để lấp trang. Hai panel theo dõi vẫn cùng đáy theo yêu cầu người dùng.
- Static `shadow` còn nhận cả `box-shadow: none`; các điểm dùng bóng thật còn lại là login/popover, không phải bóng của panel vận hành. Màu ngữ nghĩa SHAP/lớp và dấu phân cách metadata giữ nguyên.

Không thêm suppression Impeccable trong đợt này. Ngoại lệ Inter có sẵn vẫn giữ theo nhận diện đã chốt. Kết quả, ảnh và bản đo ở `tests/results/` là tệp kiểm chứng local được gitignore; thiết kế cuối được ghi trong `design/DESIGN.md`.

Thực hiện từ **29/10/2026**, cập nhật **02/11/2026** trên nhánh **duong**, theo [PLAN.md](PLAN.md). FE đã chuyển sang Next.js/React/TypeScript theo cấu trúc P-150, giữ giao diện Miro. Kết quả dưới đây thuộc **FE mới**, không dùng kết quả bản JavaScript thuần để nghiệm thu Next.js.

## Trang mẫu, xem tệp và đánh giá thủ công — BE 1.5.0

Peek có một nút Xem toàn bộ kết quả dẫn tới đúng dòng ở Toàn pipeline. Bỏ toggle Khung xem nhanh, cột ghi Giải thích, chỉ tô nền khi checkbox được chọn. Trang mẫu cố định Kỹ thuật; URL Basic cũ được chuẩn hóa Technical, bộ lọc bảng/xuất vẫn đọc Basic đã lưu. Thêm vùng xem bốn tệp JSON/Markdown/CSV/PNG và form Human review theo lựa chọn người dùng: lưu SQLite và tải JSON, không tự chấm hoặc sửa nhãn model.

**Lint/typecheck/build đạt, 26 test FE / 9 file, 46 test BE và 31 nhóm browser đạt.** Bằng chứng browser: `/tmp/nidr-review-browser-acceptance.log` và `tests/results/browser_checks.json`, process exit 0. Model/SHAP thật, Gemini giả lập, model_load_count=1. OpenAPI thực tế **1.5.0, 26 thao tác / 22 đường dẫn**. Không gọi Google, đọc .env, restart dịch vụ vận hành hoặc ghi output nguồn.

Browser đối chiếu JSON và năm hàng CSV với tệp API gốc, mở Markdown và PNG thực, điền review không tự chấm, lưu/refresh/tải JSON khớp bản SQLite, chuỗi script trong ghi chú giữ dạng text. Review điểm chưa chấm là null; sửa nhãn chỉ là đề xuất riêng. Link peek giữ checkbox khi quay về, canonical Technical và không gọi Gemini. ZIP có thêm human_reviews.json; tám tệp nền khớp gói tải thật. Test FE còn xác minh draft không bị thay khi revision bằng chứng đổi và chỉ lưu sau xác nhận; test BE kiểm tra fingerprint cũ trả 409, quyền truy cập và persistence.

Đã xem ảnh `human-review-desktop.png`, `human-review-mobile.png`, `artifact-preview-desktop.png`, `artifact-preview-mobile.png`, `peek-prediction-mobile.png`, `predictions-desktop.png`; kiểm tra font >=12 px và không tràn ngang cấp trang chạy cùng từng ảnh. Browser suite đã cập nhật các selector khi có thêm JSON viewer, chờ ảnh lazy vào viewport, chờ đúng cache Basic và terminal state của yêu cầu Gemini mới thay vì đọc trạng thái SHAP cũ. Đây là thay đổi kiểm thử theo luồng mới; không bỏ đối chiếu tệp/bằng chứng.

BE vận hành cần người dùng restart đúng process lên 1.5.0 để có API review/tạo bảng mới. Bản đánh giá mới nhất được lưu theo run/dòng/mức; chưa có lịch sử phiên bản đánh giá hoặc xác minh chuyên môn người đánh giá. Đây không phải thực nghiệm chuyên gia độc lập hay xác nhận nhãn thật. Artifact/báo cáo cũ giữ nguyên nội dung tại lúc sinh; bản review hiện tại nằm riêng trong database.

## Dự đoán và Xuất kết quả theo hai ảnh mới — 02/11/2026

Trang dự đoán đổi sang bộ lọc/bảng bên trái và peek bên phải, thêm Đi tới dòng, màu nhãn và thanh xác suất. Tab SHAP có nền và ba thanh đóng góp tương đối, giữ dấu số, đơn vị điểm phần trăm và tên đặc trưng thật. Trang xuất có thông tin snapshot, ba lựa chọn CSV/ZIP/báo cáo từng mẫu và danh mục tệp lấy từ API. Các tệp nền chỉ tải trong ZIP được ghi rõ; không tạo nút tải giả, PDF, dung lượng hay chứng nhận 100% Valid.

**Lint/typecheck/build, 24 test FE và 29 nhóm browser đạt ở bản cuối.** Browser kiểm tra Đi tới dòng đổi đúng mẫu/phân trang, chặn dòng chưa dự đoán mà không gọi Gemini. Đối chiếu bảy tên tệp nền với ZIP tải thật; chọn Basic/dòng 14 rồi đối chiếu từng tệp với API, tải PNG/Markdown thực. Đổi bộ chọn và xuất tệp không tăng số lần gọi Gemini. Model/SHAP thật, Gemini giả lập, model_load_count = 1; không chạy lại pytest BE hoặc gọi Google.

Đã xem ảnh `predictions-desktop.png`, `export-wide.png`, `export-dark.png`, `export-mobile.png` và `export-case-files-desktop.png`. Đã sửa banner snapshot trên mobile để thông tin file/số dòng không bị ép hẹp; browser đo vùng nội dung rộng trên 200 px ở viewport 390 px và ghi chú xuống hàng. Ảnh kiểm tra font tối thiểu 12 px và không tràn ngang cấp trang. Lượt sau sửa CSS từng mất kết nối CDP với Chrome ở bước đăng nhập lại; chạy xác nhận lại cùng bản cuối đạt đủ 29 nhóm. Không suy đoán nguyên nhân ngắt kết nối thành lỗi sản phẩm hoặc nguyên nhân phần cứng.

Kết quả mới nhất tại `tests/results/browser_checks.json`; hướng dẫn sử dụng tại README.md. Không sửa BE, đọc .env, restart dịch vụ vận hành hoặc ghi artifacts nguồn. Đã xác nhận có CLI agy và lưu prompt bàn giao ở `work_dir/Nguyen_Ngoc_Duong_05_fe_predictions_export.md`; không cần chuyển tiếp vì task đã hoàn thành trong phiên này.

## Khung xem nhanh theo ảnh tham chiếu — 02/11/2026

Thẻ có header dòng/X, nhãn và xác suất nổi bật, trạng thái XAI, ba tab, tám xác suất đúng thứ tự với lớp dự đoán tô tím. Footer cố định gồm Xem SHAP và Giải thích Gemini; CTA Gemini chỉ gửi dòng đang xem ở mức Kỹ thuật, không đổi checkbox và không tự retry. Giữ Xem thêm/Thu gọn và cuộn riêng cho báo cáo dài. Không thêm TCP/Port/thời điểm phát hiện khi API chưa có dữ liệu; xác suất tiếp tục ghi Xác suất đầu ra.

**Lint/typecheck/build, 24 test FE và 27 nhóm browser đạt.** Browser mở mẫu Normal ở mức Basic, đối chiếu tám lớp và lớp tô nổi bật với API, bấm CTA Gemini: nhận đúng mẫu ở Technical, chỉ thêm một lần gọi giả lập, giữ checkbox và chuyển phần xem sang Technical. Xem/tab/theme không thêm lời gọi. Kiểm tra cũ về SHAP, deep link, Xem thêm/Thu gọn, lỗi quota và đăng nhập vẫn đạt; model_load_count = 1.

Đã xem ảnh `peek-prediction-wide.png` (1920 × 1080), `peek-prediction-mobile.png` (390 × 844), `peek-prediction-dark.png`, `peek-gemini-mobile.png` và `predictions-desktop.png`. Ở màn hình rộng, đủ tám xác suất trong thẻ mà không cần cuộn; màn hình thấp có vùng cuộn và footer giữ nguyên. Mỗi ảnh được kiểm tra chữ tối thiểu 12 px và không tràn ngang cấp trang. Model/SHAP thật, Gemini giả lập; không gọi Google, sửa BE, đọc .env hoặc restart server của người dùng. Không chạy lại pytest BE cho thay đổi này.

## Thanh chọn mẫu dùng Kỹ thuật cố định — 01/11/2026

Bỏ dòng phụ dưới Dùng Gemini, thay dropdown trong thanh chọn mẫu bằng nhãn Kỹ thuật. Yêu cầu từ thanh này luôn gửi audience_level=technical; khi đang xem báo cáo Basic, sau khi BE tiếp nhận sẽ chuyển phần xem về Technical.

Lint/typecheck/build và **24 test FE đạt**; browser suite **26 nhóm đạt**. Kiểm tra cố ý chọn bộ lọc Basic rồi gửi ba mẫu từ thanh chọn: nhận kết quả Technical, phần xem tự chuyển Technical và không tạo biến thể Basic. Đã xem ảnh bulk-selection-desktop/mobile, xác nhận không còn dropdown/dòng phụ trong thanh chọn. Model/SHAP thật, Gemini giả lập; không gọi Google, không sửa BE hoặc restart server vận hành. Các test BE trước đó giữ làm lịch sử.

## BE đang chạy chưa nhận remember — 01/11/2026

Request với username/password trống và remember=false nhận 422 body.remember không được hỗ trợ ở cả BE 8000 và FE 3000. Request không chứa credentials và bị schema từ chối trước xử lý đăng nhập. Mã BE hiện tại đã có remember/API 1.4.0; process vận hành cần restart đúng checkout. FE đổi riêng lỗi này thành hướng dẫn cập nhật, giữ HTTP 422 và không tự gửi lại khi bỏ remember. Lint/typecheck/build và **24 test FE đạt**; không chạy lại BE/browser suite cho thay đổi thông báo. Không đọc .env hoặc restart server của người dùng.

## Đổi tên website thành NIDR — 01/11/2026

Tên NIDR và tên đầy đủ Network Intrusion Detection and Response thống nhất từ src/lib/brand.ts, dùng ở login, sidebar, footer và metadata/tab trình duyệt. Lint/build đạt; Chrome profile tạm xác minh tên thương hiệu, footer, title và tooltip tên đầy đủ, chụp login-nidr.png / login-nidr-mobile.png. Các kiểm tra nội dung đạt; thư mục profile được dọn riêng sau lỗi chờ Chrome đóng hoàn toàn. Không gửi đăng nhập hoặc thay dữ liệu nguồn. Không chạy lại bộ nghiệp vụ cho đổi tên hiển thị.

## Căn giữa chữ nút Đăng nhập — 01/11/2026

Nhãn nút căn giữa, icon mũi tên/spinner đặt tuyệt đối để không làm lệch chữ. Lint và build đạt. Chrome với profile tạm mở trang login công khai, không gửi đăng nhập: đo tâm chữ so với tâm nút sai lệch khoảng 0,008 px ở 1280 px và 390 px. Ảnh login-centered.png và login-centered-mobile.png trong tests/results. Không chạy lại các bộ kiểm tra nghiệp vụ cho chỉnh CSS này.

## Chỉnh form đăng nhập theo góp ý UX — 01/11/2026

Thương hiệu chuyển vào card 460 px, đệm ngang 40 px, bo 16 px và bóng mềm; nền radial tím/xanh nhẹ theo yêu cầu. CTA tím #6d28d9, placeholder admin/dấu chấm, footer gọn. Trợ giúp là nút chữ Quên mật khẩu? mở hướng dẫn liên hệ quản trị. Khu phản hồi dành sẵn 60 px; trạng thái gửi có spinner và khóa form. Ẩn chỉ báo N qua devIndicators=false. Chữ CTA tương phản 7,10:1; chữ lỗi sáng #b91c1c trên nền đỏ nhạt đạt khoảng 5,90:1; giữ tương phản input hai theme.

API **1.4.0** nhận remember=false mặc định: cookie theo phiên trình duyệt. Khi chọn, Max-Age=28800; thời hạn BE vẫn tám giờ và logout/restart vẫn thu hồi. Không lưu password/token trong localStorage. **Lint/typecheck/build, 23 test FE, 43 test BE và Next dev proxy check đạt.** Browser suite kiểm tra placeholder, trợ giúp, spinner khi trì hoãn mạng, vị trí nút không thay đổi khi lỗi trống/sai, session cookie khi tắt và persistent cookie khi bật Ghi nhớ phiên. 26 nhóm đạt; model nạp một lần, Gemini giả lập.

Đã xem ảnh login-wide (1920 × 1080), login-mobile, login-dark, login-submitting và login-error. Các file ở tests/results được ghi từ browser thật. Không restart BE/FE của người dùng hoặc thay artifact nguồn. BE vận hành cần restart lên 1.4.0 để nhận trường remember; cấu hình Next devIndicators cần được Next nạp lại.

## Sửa login 403 khi đi qua Next dev — 01/11/2026

Next rewrites đổi Host thành địa chỉ nội bộ BE, trong khi Origin giữ cổng FE. BE đã dùng X-Forwarded-Host được Next ghi đè, chỉ tin khi kết nối từ loopback. Origin ngoài/giả và forwarded host từ kết nối không tin cậy vẫn bị từ chối.

**42 test BE và 26 nhóm browser qua Nginx HTTPS đạt** sau bản sửa. Thêm `tests/dev_proxy_check.py` dùng Next dev thật, cùng next.config.ts và frozen model, kiểm tra login/session/upload/logout cùng hai trường hợp origin/forwarded-host giả bị chặn. Kết quả tại `tests/results/dev_proxy_checks.json`, model_load_count = 1, Gemini calls = 0. Không thay code giao diện hoặc restart server đang chạy. Kết quả lint/typecheck/build và 22 test FE thuộc lượt sửa thông báo trước đó.

## Xử lý BE vận hành chưa có API đăng nhập — 01/11/2026

Đã kiểm tra không dùng credentials: `/health` trả 200 ở cổng 8000 và qua FE 3000, nhưng `/api/auth/session` trả 404 ở cả hai cổng. Tiến trình BE đang chạy chưa nạp endpoint mới; FE proxy tới BE hoạt động. Không restart tiến trình của người dùng và không đọc `.env`.

Đổi lỗi login 404/405 thành hướng dẫn khởi động lại BE ở terminal hiện tại, giữ mã lỗi và không tự gửi lại mật khẩu. **Lint/typecheck/build và 22 test FE đạt**. Không chạy lại browser suite hoặc pytest BE cho thay đổi xử lý thông báo này; các kết quả 26 nhóm/40 test bên dưới thuộc lượt xác thực trước. Cần người dùng restart đúng BE đang chạy để endpoint mới có hiệu lực.

## Đăng nhập và đăng xuất bằng form — 01/11/2026

Người dùng chọn chức năng hoạt động đầy đủ, dùng tài khoản quản trị BE hiện có. Thêm `/login` tiếng Việt theo nhận diện ứng dụng, tên đăng nhập/mật khẩu, hiện ẩn mật khẩu, trạng thái gửi/lỗi/trợ giúp, sáng/tối và nút Đăng xuất. Dashboard có SessionGate; UiProvider/metadata chỉ khởi tạo sau xác thực. Khi phiên bị từ chối, quay về form và giữ route nội bộ hợp lệ, chặn return URL ra ngoài ứng dụng.

BE **1.3.0** bổ sung ba endpoint auth; cookie HttpOnly/Strict, Secure ở HTTPS, tối đa tám giờ, bị thu hồi ở BE khi logout và mất khi restart. Nginx bảo vệ trang riêng tư, chuyển về login khi chưa xác thực; login/bundle tĩnh/icon công khai để form tải được. Dữ liệu API và file kết quả tiếp tục được BE kiểm tra. HTTP Basic giữ cho Swagger/CLI; phiên cookie không lưu password/token trong storage của JavaScript.

**Lint, typecheck, build, 21 test FE, 40 test BE và 26 nhóm browser đạt.** Luồng chính đăng nhập bằng form/cookie thật. Đã kiểm tra trống/sai/đúng, focus khi thiếu tên, hiện/ẩn mật khẩu, cookie HttpOnly/Secure/Strict, refresh, deep link, tải CSV/ZIP/PNG/Markdown bằng cookie, logout, thu hồi phiên và yêu cầu đăng nhập lại. Kiểm tra bổ sung mô phỏng trình duyệt còn Basic cũ: dashboard vẫn cần cookie, form không tự chuyển đi khi chỉ có Basic. 40 test BE có thêm sáu test auth: cookie/revocation, xoay token, sai tài khoản/không phản chiếu password, CSRF/Secure, hết hạn/restart và giới hạn nhập sai.

Hai điểm từ lượt review đã sửa và được chấm lại: redirect nội bộ dùng URLSearchParams giữ đủ `class`, `row`, `audience` và giá trị có `%26`/`%3D` qua gateway; viền input dùng token muted, tương phản **4,76:1 sáng / 6,96:1 tối**, xem `tests/results/login-contrast.json`. Review chỉ xác nhận hai điểm được yêu cầu sửa, không phải chứng nhận an toàn toàn hệ thống.

Ảnh đã kiểm tra: `login-desktop.png` (1280 × 720), `login-mobile.png` (390 × 844), `login-dark.png` (1280 × 900), `login-error.png`. Browser suite vẫn dùng frozen model/SHAP thật, model_load_count = 1, Gemini giả lập; runtime/cổng/chứng chỉ tạm. Không đọc BE/.env, không restart BE/Nginx của người dùng và không thay artifact nguồn. BE vận hành cần được người dùng restart để nhận API 1.3.0.

## Cân lại trang Theo dõi lần chạy — 01/11/2026

Thanh tiến độ nằm trong thẻ file, có số dòng và phần trăm; màu thanh dùng token theo trạng thái chạy/tạm dừng/hoàn tất. Bốn chỉ số là bốn ô riêng, có icon và màu nhẹ. Hai panel phân bố/kết quả dùng grid stretch để cân đáy; cột phân bố hẹp hơn, có số dòng và tỷ lệ theo số dòng đã dự đoán. Liên kết Xem bảng dự đoán nằm ở tiêu đề, bảng chỉ hiển thị tối đa năm dòng. Màn hình nhỏ chuyển panel về một cột và thống kê về hai cột.

**Lint, typecheck, build, 19 test FE và 24 nhóm browser đạt.** Browser kiểm tra tiến độ thuộc thẻ file, bốn ô thống kê tách nhau, hai panel cùng đáy ở 1920 px và xếp dọc ở 390 px. Đã chạy Replay 50 dòng với khoảng cách 1 giây, xem trạng thái đang chạy giữa file, tạm dừng, tiếp tục và dừng có xác nhận; không trùng dòng. Model/SHAP thật, Gemini giả lập và model_load_count = 1.

Đã xem ảnh `monitor-wide.png`, `monitor-mobile.png`, `replay-running-wide.png`, `replay-paused-dark.png` và `replay-paused-mobile.png`. Ảnh cùng các kiểm tra font tối thiểu 12 px, không tràn ngang nằm trong `tests/results/`. Không thay BE, hợp đồng API hoặc artifact nguồn; không gọi Google API mới, không restart dịch vụ của người dùng. Không chạy lại pytest BE cho thay đổi bố cục này.

## Trình bày lại văn bản Gemini — 30/10/2026

Diễn giải đầy đủ đổi sang báo cáo có độ rộng tối đa 1.160 px, chia rõ nhận định/so sánh/SHAP/đặc trưng/giới hạn; gợi ý kiểm tra nằm ở cột bên phải khi đủ rộng. Trang nhỏ và peek dùng một cột. Hướng dẫn cố định theo lớp nằm trong accordion riêng, vẫn có thể mở để đọc.

Lượt này **lint, typecheck, build, 19 test FE và 23 nhóm browser đều đạt**. Đã đối chiếu toàn bộ các đoạn văn bản trong phản hồi Gemini giả lập với textContent của báo cáo: tóm tắt, hai phần tổng hợp, từng đặc trưng, nguồn/nội dung/mục đích kiểm tra và giới hạn đều được giữ nguyên. Kiểm tra Xem thêm/Thu gọn và không phát sinh thêm lời gọi Gemini tiếp tục đạt.

Ảnh mới đã xem: `tests/results/gemini-report-wide.png` (1920 × 1080), `gemini-desktop.png` (1280 × 720), `gemini-report-mobile-content.png` (390 × 844). Kiểm tra font tối thiểu 12 px, không tràn ngang và toàn bộ luồng cũ chạy cùng browser suite. Gemini dùng giả lập; không thay prompt/model/API, không restart BE hoặc sửa dữ liệu nguồn.

## Điều chỉnh giao diện theo ảnh người dùng — 30/10/2026

Đã ẩn ID khỏi lịch sử CSV và trạng thái kết nối thành công, làm lại upload/chọn mẫu, thêm nút X đóng peek/cảnh báo, tách panel và thu gọn Gemini bằng Xem thêm/Thu gọn. Trang cảnh báo cập nhật theo ảnh 8. Giữ cảnh báo mất mạng, hợp đồng API, dữ liệu nguồn và cơ chế chọn mẫu chủ động.

Lượt này lint/typecheck/test/build đều đạt; test FE tăng lên **19**, browser suite tăng lên **23 nhóm**. Kiểm tra bỏ/chọn lại file và focus; Gemini mặc định thu gọn, mở rộng không đổi chiều cao panel và cuộn riêng, không gọi Gemini mới; nút X đóng cảnh báo rồi chọn dòng mở lại; lịch sử giữ liên kết kết quả và không hiện ID. Đã xem ảnh upload, thanh chọn mẫu, Gemini thu gọn/mở rộng và cảnh báo ở desktop/mobile. Kiểm tra chữ nhỏ nhất 12 px và tràn ngang chạy cùng mỗi lần chụp.

Không thay đổi mã BE trong lượt chỉnh UI này; kết quả **34 test BE** bên dưới thuộc lượt chuyển serving trước đó, không chạy lại để ghi thành kết quả mới. Không restart server của người dùng, không đọc .env, không gọi Google mới và không ghi artifact nguồn.

## Kết quả thực tế

| Kiểm tra | Kết quả |
|---|---|
| Node / npm | **22.23.4 / 10.9.9**; `npm ci` từ lockfile thành công |
| Phiên bản FE | Next **16.4.3**, React **19.3.1**, TypeScript **6.0.3**, Tailwind **4.3.3** |
| `npm run lint` | Đạt, `--max-warnings=0` |
| `npm run typecheck` | Đạt, TypeScript strict |
| `npm run test` | **26 tests / 9 files passed**, Vitest/React Testing Library |
| `npm run build` và postbuild | Đạt; App Router, standalone có public/JS/CSS/font |
| Kiểm thử BE sau bổ sung Human review | **46 passed**, 629 cảnh báo thư viện, **33,02 s** |
| `.venv/bin/python FE/tests/dev_proxy_check.py` | Đạt 6 luồng qua Next dev rewrites thật, không gọi Gemini |
| `.venv/bin/python FE/tests/browser_check.py` | **31 nhóm kiểm tra đạt**, Chrome + Nginx TLS + Next production + BE thật |
| OpenAPI BE | **1.5.0**, **26 thao tác / 22 đường dẫn** |
| Model / SHAP | Frozen model và SHAP thật, **model_load_count = 1**, không fit/retrain |
| Gemini | Giả lập phản hồi accepted và lỗi 429; không gọi Google mới |
| Viewport | 1280 × 720, 390 × 844, sáng/tối; đã xem ảnh render; không tràn ngang cấp trang trong các ảnh kiểm tra |

`npm run build` chạy cả TypeScript của bản cuối sau khi sửa khôi phục scroll. Các thao tác trên dùng Node.js 22 qua nvm; không thay Node mặc định của người dùng.

## Kiểm thử component và state

26 test bao phủ:

- API chỉ cùng origin `/api/`, chặn URL ngoài origin/traversal; mã hóa query và giữ số 0.
- Multipart không tự đặt Content-Type, chỉ gửi một POST, giữ mã lỗi và thông báo tiếng Việt.
- Polling không chồng request; abort khi đổi mẫu/unmount, loại phản hồi cũ, tạm ngừng khi tab ẩn và giữ dữ liệu cuối khi lỗi.
- React Strict Mode cleanup đúng; mount, đổi tab/mức diễn giải không tự POST/Gemini. Nút yêu cầu gửi đúng dòng/mức/lựa chọn Gemini.
- Checkbox theo row_index, chọn/bỏ chọn trang không ảnh hưởng trang khác, không trùng và không quá 50.
- Phân biệt null với 0, xác suất với điểm phần trăm, đóng góp âm và phần ngoài top-5.
- Văn bản Gemini có thẻ script hiển thị dưới dạng text; bản nháp có nhãn cần sửa.
- Tab dùng ArrowLeft/ArrowRight/Home/End để chuyển cả lựa chọn và focus.
- URL trở về sau đăng nhập chỉ nhận route nội bộ hợp lệ; chặn URL ngoài origin và đường dẫn bất thường.
- Redirect mã hóa đầy đủ query và ký tự đã escape; không tách nhầm tham số của trang đích thành tham số form login.
- Login 404/405 có hướng dẫn restart BE, giữ mã HTTP và không tự gửi lại credentials.
- Lựa chọn remember được gửi đúng true/false; mặc định tắt.
- BE cũ từ chối trường remember được giải thích bằng hướng dẫn cập nhật, không tự bỏ lựa chọn và gửi lại mật khẩu.
- Parser CSV xử lý BOM, dấu phẩy/nháy và xuống dòng trong chuỗi.
- Human review không tự chấm/lưu, giữ draft khi revision đổi; chỉ gửi đúng mẫu/fingerprint sau xác nhận và hiện bản đã lưu để tải.

## Kiểm tra trên browser/gateway thật

1. Chạy `nginx -t`, Next standalone, cổng TLS và deep-link production.
2. Trang riêng tư thiếu phiên chuyển tới login; API thiếu/sai quyền trả 401, Swagger giữ HTTP Basic. Login/icon/bundle tĩnh công khai. Chặn source riêng tư và auth nội bộ; xác minh golden khi khởi động.
3. Upload gần 10 MiB được chuyển tới BE để kiểm tra schema; quá 10 MiB/11 MiB và 1.001 dòng bị chặn đúng.
4. HTTP Basic và lịch sử trống; route sai hiển thị trang không tìm thấy.
5. CSV sai schema giữ form, không tạo run.
6. Upload 50 dòng và Batch đủ 50/50; nhãn và tám xác suất của 16 dòng đầu khớp golden (`rtol=1e-6`, `atol=1e-7`).
7. Phân trang đúng row_index.
8. Lọc Web-Based, chọn Normal/BruteForce/Web-Based độc lập xem nhanh, đóng khung không bỏ checkbox; tính SHAP thật và không gọi Gemini khi bỏ chọn Gemini.
9. Reload trực tiếp deep-link dòng 14 của bản production, vẫn đọc đúng bằng chứng.
10. Đọc đúng 46 đặc trưng/đúng thứ tự từ API, không có label; SHAP/metadata đúng mẫu; kiểm tra desktop/mobile.
11. Đổi mức basic chỉ GET; bấm yêu cầu mới gọi Gemini giả lập một lần, dùng lại SHAP.
12. Quay về bảng giữ technical, mẫu #000014, checkbox dòng 2 và scroll 180 px.
13. Tiếp nhận, ghi chú, đóng có xác nhận, mở lại; chuỗi script trong ghi chú không thực thi.
14. Tải CSV và ZIP qua browser, đọc lại CSV đủ 50 dòng.
15. PNG/Markdown đúng mức diễn giải tải được qua gateway; thiếu tài khoản bị chặn.
16. Chủ động retry Gemini có xác nhận; lỗi quota 429 giữ SHAP, trạng thái partial, không tự retry qua polling.
17. Ngoại tuyến giữ bằng chứng; nối lại chỉ đọc dữ liệu.
18. Replay pause/resume/stop có xác nhận, không nhân đôi row_index.
19. **CSV hợp lệ đúng 10 MiB** đi hết gateway, được dự đoán Normal đúng golden; padding ở cột label không vào model.
20. Không ghi nhận lỗi JavaScript trong lượt kiểm tra; model chỉ nạp một lần.
21. Xem thêm/Thu gọn trong peek không đổi chiều cao khung, có cuộn riêng và không gọi Gemini lại; đổi mẫu tự thu gọn trong test component.
22. Nút X đóng panel cảnh báo, chọn dòng mở lại đúng chi tiết và lọc theo lớp.
23. Lịch sử chỉ hiện tên file CSV; giữ liên kết tới run và ẩn ID trong nội dung bảng.
24. Trang Theo dõi có tiến độ trong thẻ file, bốn ô chỉ số riêng và liên kết bảng ở tiêu đề; panel cùng đáy ở màn hình rộng, xếp dọc trên mobile. Kiểm tra cả Replay đang chạy giữa file và tạm dừng ở sáng/tối.
25. Form đăng nhập trống/sai/đúng, placeholder, trợ giúp chữ, spinner khi chờ và nút không đổi vị trí lúc lỗi; cookie HttpOnly/Secure/Strict, session/persistent đúng lựa chọn Ghi nhớ phiên và giữ phiên khi refresh. Không lưu mật khẩu vào localStorage/sessionStorage.
26. Đăng xuất thu hồi cookie; deep link giữ nguyên nhiều tham số và giá trị đã mã hóa, phiên bị thu hồi không đọc lại được sau reload. Mô phỏng Basic còn lưu của ứng dụng cũ vẫn trở về form vì dashboard yêu cầu cookie.
27. Peek giữ đủ tám lớp/thứ tự, tô đúng lớp dự đoán; một link mở trang đầy đủ đúng dòng, chuẩn hóa Technical, giữ checkbox khi quay về và không gọi Gemini. Footer giữ trong thẻ, Gemini dài cuộn riêng.
28. Đi tới dòng nhận chỉ số có #, đổi đúng mẫu/trang, từ chối dòng chưa dự đoán và không tạo lời gọi Gemini.
29. Xuất kết quả có ba lựa chọn; danh mục tệp nền khớp ZIP, tệp mẫu/mức khớp API; tải CSV/ZIP/PNG/Markdown thật. Banner mobile có vùng chữ đủ rộng, ghi chú xuống hàng; không gọi Gemini khi đổi danh mục.
30. Xem trước JSON và CSV khớp tệp nguồn, mở được Markdown/PNG của đúng mẫu.
31. Human review lưu/đọc lại sau refresh, tải JSON khớp bản lưu, không tự chấm hoặc thay dự đoán/Gemini; không thực thi HTML trong ghi chú.

CSV browser 50 dòng được dựng bằng cách lặp bộ 16 mẫu tham chiếu để phủ lớp và phân trang. Đây không phải tập đánh giá độc lập. BE tests còn đối chiếu 50 mẫu tích hợp gốc, Gemini timeout/thiếu key, hai mức dùng chung SHAP, checksum và persistence.

Next có thể stream shell trước khi `notFound()` xảy ra, khi đó HTTP vẫn là 200 và boundary 404 hiển thị phía client. Kiểm tra route sai đối chiếu boundary và UI, không coi mọi trang stream là HTTP 404.

## Bằng chứng và phạm vi chạy

- `tests/results/browser_checks.json`: 31 nhóm kiểm tra và danh sách ảnh của lượt mới nhất; thêm xem trước tệp và Human review, giữ các luồng cũ.
- `tests/results/backend-tests.xml`: bản XML từ lượt pytest 40 passed sau bổ sung auth.
- Ảnh trong `tests/results/`: bảng, chi tiết, input, Gemini, cảnh báo, mobile, nền tối, partial và Replay pause. Đã xem trực tiếp ảnh bảng desktop, bằng chứng mobile, chi tiết nền tối và cảnh báo mobile của FE mới.

Các file kết quả được Git bỏ qua. Browser suite khởi động BE/Next/Nginx/Chrome tại cổng tạm với runtime/tài khoản/chứng chỉ riêng và đóng/xóa sau kiểm tra. HTTP client xác minh CA tạm; Chrome chỉ bỏ qua lỗi chứng chỉ trong profile thử nghiệm. Không đọc/sửa BE/.env, không dừng hoặc khởi động lại BE vận hành, không gọi Gemini thật, không sửa artifact output.

## Chuyển đổi và thiết kế

- Bỏ `FE/index.html`, `FE/assets/` và hash router cũ; chỉ còn source sản phẩm Next.js trong `src/`.
- BE `/` có xác thực và redirect sang `/docs`, không mount FE. Giữ API input 46 trường, SHAP metadata và các REST API đã có.
- Giữ token, hai ảnh Miro, file thiết kế và test còn dùng. Không xóa BE/runtime, .env, TLS hoặc module Python đang phục vụ chạy/kiểm tra.
- Nội dung chính 14 px, chữ phụ tối thiểu 12 px; mỗi lần chụp browser kiểm tra không có text hiển thị dưới 12 px. Giữ Inter theo Miro và kế hoạch được duyệt; ngoại lệ `overused-font=inter` chỉ áp dụng `FE/src/app/globals.css` trong `.impeccable/config.json`. Không tắt quy tắc chữ nhỏ hoặc bỏ qua cả file/rule.
- Một máy dùng Nginx làm cổng chung, Next/BE bind loopback; model chỉ nằm trong một process BE. Template triển khai đã thử ở instance tạm, chưa áp dụng vào Nginx vận hành.

## Giới hạn

Chưa đánh giá phản hồi Gemini mới từ Google trong lượt này, thực nghiệm đánh giá với chuyên gia độc lập, chất lượng diễn giải basic, truy cập từ máy LAN khác, chứng chỉ production, trình đọc màn hình, clipboard hệ điều hành hoặc trình duyệt/thiết bị khác Chrome. Form review mới kiểm tra về chức năng lưu/đọc/xuất, không chứng nhận chất lượng nhận xét hoặc chuyên môn người nhập. Đây không phải chứng nhận accessibility hay phép thử tải lớn.

SHAP mô tả đầu ra mô hình, chưa chứng minh nhân quả hoặc xác nhận tấn công. Validation/test nguồn đã từng được xem. Metadata API chưa cung cấp được hiển thị `—` kèm lý do; thời gian artifact không được gọi là latency mở trang. Ngữ cảnh storage của origin cũ không tự chuyển sang cổng FE mới; kết quả BE giữ nguyên.
