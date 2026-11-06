# Tác vụ NIDR theo tham chiếu Adminator

Mode: Operate.

Nhóm đồ án chạy thử CSV, rà kết quả mô hình và đọc bằng chứng của từng dòng. Tham chiếu hiện tại là [Adminator](https://preview.colorlib.com/theme/adminator/index.html), được người dùng chọn ngày 03/11/2026; ảnh và nguồn tại [README.md](README.md). Token/chữ/shell ở [DESIGN.md](DESIGN.md), source thực thi trong `FE/src/app/globals.css`. Hướng này thay các mô tả framed-sheet/tím trước đây; cấu trúc tác vụ từ Miro tiếp tục được giữ.

## Tổng quan

Trang `/dashboard` là mục **Tổng quan** đầu menu và trang đích mặc định khi đăng nhập không có deep-link riêng. Hàng đầu có tiêu đề **Tổng quan giám sát an ninh** và Tạo lần chạy; bộ lọc thời gian/lần chạy, Làm mới và thời điểm cập nhật nằm chung một thẻ, phạm vi dữ liệu nằm ngay dưới. Bốn ô số liệu gồm mẫu đã dự đoán, mẫu nghi vấn (khác Normal), cảnh báo chờ tiếp nhận và mẫu đã có SHAP. Trang đọc tổng đầy đủ từ API tổng hợp, không cộng các dòng của một trang bảng kết quả; tự làm mới 15 giây và có nút làm mới chủ động. Bốn KPI giữ số 30px, xuống 26px ở mobile; nền icon pha màu theo chỉ số và bóng `shadow-subtle` chỉ áp dụng tại các ô dashboard này, không đặt thành quy tắc cho mọi card vận hành. Chữ giao diện nền vẫn 14px, nhãn/chú thích 12px theo hệ Adminator hiện có.

Thời gian chọn là Hôm nay, 7 ngày, 30 ngày hoặc Toàn bộ lịch sử, theo ngày xử lý mẫu UTC+7. Tham số thời gian/lần chạy nằm trong URL và giữ khi tải lại. Trạng thái cảnh báo, diễn giải và phiếu đánh giá phản ánh hiện tại của nhóm mẫu đã chọn. Toàn lịch sử có tổng đầy đủ nhưng biểu đồ hoạt động chỉ 30 ngày gần nhất, ghi rõ phạm vi. SHAP đếm một lần mỗi mẫu có tệp bằng chứng dùng chung, kể cả khi Gemini lỗi; trạng thái diễn giải/Gemini/phiếu đánh giá tổng hợp mức Kỹ thuật. Phiếu đã lưu không xác nhận nhãn thật và có thể cần xem lại khi bằng chứng thay đổi.

Hai biểu đồ trình bày số mẫu theo lớp/thời gian và tỷ trọng tám lớp cố định. Cập nhật theo yêu cầu đã chốt ngày 06/11/2026: thẻ **Số mẫu đã xử lý** mặc định mở **Theo lớp**, dùng tám cột đứng với trục X là tên lớp và trục Y là số mẫu. Số đếm nguyên hiển thị trên từng cột, giữ thứ tự/màu lớp như pie; chiều cao tỷ lệ thật, lớp 0 không có cột. Nhãn xoay trong vùng SVG có đủ đệm phía dưới, không thu nhỏ font dưới 12px trên mobile. Trục Y bắt đầu 0 và bao phủ cả cột/đường với khoảng trống cho số đếm, kể cả khi chỉ có 1 mẫu. Đường **KDE minh họa** từ `class-kde.ts` dùng chỉ số lớp 0..7 cố định, tần số là số mẫu; Gaussian/Scott với băng thông tối thiểu 0,5; 121 điểm trong [-0,5; 7,5], nhân mật độ về thang số mẫu/bin 1 nhãn. Chỉ vẽ khi có ít nhất 2 lớp dương và 2 mẫu. Ghi rõ đường phụ thuộc thứ tự nhãn và chỉ để tham khảo; không diễn giải tên lớp như thời gian, khoảng cách tự nhiên hoặc xác suất. Số liệu chính xác vẫn ở cột và bảng mở rộng. Bộ chọn **Theo ngày · KDE**, phép tính và phần vẽ theo ngày được giữ nguyên. Hai nút hỗ trợ Tab, mũi tên, Home/End và aria-selected/tabpanel. Khi component không nhận class_counts, chỉ hiện dữ liệu ngày, không tự dựng số đếm lớp. Hoạt động theo ngày dùng cột đứng chồng Normal/khác Normal, giữ số lượt thật của từng ngày, chọn ngày bằng chuột/bàn phím và mở bảng số liệu; ngày không có mẫu vẫn hiện 0. Đường KDE tổng số lượt là ước lượng Gaussian từ số liệu tổng theo ngày, không phải thời điểm gói mạng hay dự báo. Helper `activity-kde.ts` dùng số lượt làm số quan sát lặp ở chỉ số ngày, quy tắc Scott và băng thông tối thiểu 0,5 ngày; tính 121 điểm và đưa về đơn vị lượt/ngày để cùng thang với các cột có bin một ngày. Chỉ vẽ khi có ít nhất hai ngày dương và tổng ít nhất hai mẫu; khi thiếu điều kiện, giữ cột và hiện thông báo chưa đủ ngày để ước lượng. Không gắn nhãn KDE cho đường nội suy hoặc dùng một đường cong cố định. SVG đo chiều rộng theo vùng chứa, chiều cao 176px, vùng vẽ 132px và chữ trục 12px; giảm số nhãn ngày khi hẹp.

Phân bố lớp giữ biểu đồ tròn theo phần trên tổng mẫu thật, không đổi thành donut hoặc chuẩn hóa theo lớp lớn nhất. Bỏ nhãn chen trong hình quạt: tên lớp, số mẫu và tỷ lệ nằm ở chú giải có tiêu đề cột; số căn phải, tỷ lệ 14px/600, lớp có số mẫu lớn nhất được nhấn nền nhẹ. Chú giải giữ đủ Normal, BruteForce, DDoS, DoS, Mirai, Recon, Spoofing, Web-Based theo thứ tự cố định. Lớp 0 không vẽ lát; tổng bằng 0 có vòng rỗng, “0 mẫu” và tỷ lệ —; một lớp chiếm 100% vẽ hình tròn đầy đủ. Hover/focus vào lát hoặc hàng chú giải làm nổi phần tương ứng và hiện tên lớp/số mẫu/tỷ lệ ở dòng chi tiết phía dưới; rời chuột/blur trở về lớp nhiều nhất, không lọc dữ liệu. Dòng chi tiết được xuống dòng ở mobile. Theme tối dùng màu lát sáng hơn để giữ phân biệt trên nền panel, không dùng hiệu ứng 3D, glow hoặc nhãn chen trong lát. Không hard-code DDoS 70% hoặc số mẫu của một lần chạy. Nhãn dự đoán không xác nhận tấn công thực tế.

Sau biểu đồ là tối đa năm cảnh báo và năm lần chạy gần nhất, có đường mở hồ sơ/run thật; phần Giải thích và đánh giá mở đầu bằng ba phần phẳng: Bằng chứng SHAP, Diễn giải Gemini và Đánh giá của bạn. Mỗi phần có mô tả ngắn, số đã có trên tổng mẫu và thanh tỷ lệ; SHAP dùng metrics.shap_rows, Gemini dùng số accepted với nhãn Đạt kiểm tra tự động, đánh giá dùng số phiếu đã lưu. Tiến độ có tên/giá trị truy cập, trường hợp tổng 0 vẫn hiện 0 và thanh rỗng. Các trạng thái tác vụ, từng trạng thái Gemini và chi tiết nhận định/đề xuất nhãn được giữ trong mục Xem chi tiết tất cả trạng thái. Link mở đúng lần chạy đã chọn, hoặc ghi rõ lần chạy gần nhất; không hiện link giả khi chưa có run. Các phần không đóng thêm card bên trong card; diễn giải tự động và phiếu của người dùng không thay xác nhận nhãn thực tế. Desktop dùng hai cột biểu đồ/bảng và ba cột trạng thái; các panel bảng giữ chiều cao theo dữ liệu. Khi danh sách gần nhất chỉ có một lần chạy, thẻ bổ sung phần Thông tin toàn bộ lần chạy: số dòng CSV, đã dự đoán, chưa xử lý, Batch/Replay và lần cập nhật. Các giá trị lấy từ chính run đó, không suy ra từ nhóm mẫu lọc theo ngày hoặc dựng thêm dòng để lấp chỗ trống. Bộ lọc, KPI và hình được giữ gọn để bắt đầu thấy tiêu đề hai bảng trong khung nhìn desktop đầu tiên. Ở 1220px trở xuống, thanh công cụ xuống hàng, pie và chú giải dùng hai cột gọn với chú giải một danh sách; ở 1000px trở xuống, biểu đồ/bảng, bộ lọc và trạng thái xếp một cột, bốn KPI thành hai cột. Trong khoảng 761–1000px, pie và chú giải đặt cạnh nhau; từ 760px trở xuống xếp dọc. Bảng rộng tự cuộn trong vùng bảng. Trạng thái trống có số 0 hợp lệ và hướng dẫn đổi phạm vi/tải CSV; lỗi tải không thay bằng số 0 giả, dữ liệu cuối vẫn đọc được khi mất kết nối.

## Footer dùng chung toàn website

Footer khép toàn bộ các trang của hệ thống, không còn là thẻ đề tài riêng trên Tổng quan. Thay đổi này theo yêu cầu người dùng ngày 04/11/2026 (bác bỏ footer dạng thẻ qua ảnh `orca-paste-1793763906876-b5055a3e-7709-486f-bcd5-39ee743cee3d.png`) và tổ chức thông tin tham chiếu cấu trúc chân trang [Học viện Công nghệ Bưu chính Viễn thông](https://ptit.edu.vn/) (ảnh `FE/design/reference/ptit-footer.png`). Component `SiteFooter` tại `FE/src/components/shared/site-footer.tsx` được dùng chung cho operational shell (`operational-shell.tsx`), trang đăng nhập (`auth/login-form.tsx`) và trang 404 (`app/not-found.tsx`).

Theo yêu cầu cập nhật ngày 04/11/2026, footer dùng cùng nền panel với UI thay cho dải Navy cố định: nền `--panel`, chữ `--text`/`--muted`, liên kết `--primary`, đường phân cách `--line`. Vì vậy theme sáng có footer trắng, theme tối dùng panel tối tương ứng. Hover dùng màu chữ chính và gạch dưới, focus có outline primary. Footer vẫn trải hết chiều rộng vùng nội dung (ở dashboard và các trang vận hành, `margin: 32px -32px -40px`, mobile `28px -16px -32px`), không đóng khung card, không bo góc hay đổ bóng. Giữ bố cục thông tin theo cột; không đưa lại badge in hoa, avatar sinh viên hoặc tiêu đề đồ án phóng lớn.

Bố cục gồm 4 cột thông tin tổ chức và một dải chân trang phụ:

1. **Về NIDR**: Biểu tượng `ShieldCheck`, tên thương hiệu 22px, mô tả hệ thống phát hiện xâm nhập mạng IoT giải thích bằng SHAP và Gemini, nhãn Đồ án tốt nghiệp · Nhóm số 07.
2. **Đơn vị đào tạo**: Học viện Công nghệ Bưu chính Viễn thông (liên kết ngoài trỏ `https://ptit.edu.vn/`), Khoa Viễn thông I / Bộ môn Mạng viễn thông, ngành Kỹ thuật Điện tử Viễn thông, hệ Chính quy · Khóa 2022–2026.
3. **Nhóm thực hiện**: Danh sách 3 sinh viên đối chiếu từ `Đề cương đồ án tốt nghiệp.docx`: Nguyễn Ngọc Dương (B22DCVT112 · D22VTHI02), Hà Minh Hải (B22DCVT173 · D22VTMD03), Tạ Trung Kiên (B22DCVT265 · D22VTMD01), số định danh dùng chữ số cố định (tabular-nums).
4. **Liên kết nhanh**: Điều hướng nội bộ tới Tổng quan (`/dashboard`), Lịch sử lần chạy (`/runs`), Tạo lần chạy (`/runs/new`), Trung tâm cảnh báo (`/alerts`) và Tài liệu API (`/docs`).

Dải chân trang phụ phía dưới (`.site-footer-bottom`) ngăn cách bởi đường viền 1px, hiển thị tên nhóm/năm và công nghệ CICIoT2023 · SHAP · Gemini.

Quy tắc hiển thị và cuộn:

- Footer nằm cuối luồng cuộn nội dung tự nhiên, không cố định (`position: fixed`) đè lên thao tác làm việc.
- Trên trang Đăng nhập, khối form đăng nhập giữ trọn vẹn trong khung nhìn đầu tiên (`min-height: calc(100dvh - 80px)`); footer chỉ xuất hiện khi cuộn trang.
- Đáp ứng màn hình (Responsive): Desktop (>1100px) chia lưới 4 cột; từ 1100px trở xuống chia lưới 2 cột; từ 600px trở xuống xếp dọc 1 cột. Không phát sinh thanh cuộn ngang trang.

Sidebar giữ menu mở/thu gọn và shortcut Swagger API ở cuối; thẻ Model đã chốt, mã model và chuỗi stacking đã được bỏ theo yêu cầu người dùng. Metadata model vẫn do các màn hình cần nó đọc, không dùng việc bỏ thẻ để xóa loader hoặc dữ liệu API.

## Tạo và theo dõi lần chạy

Trang tạo chia form tải CSV và card **Đầu vào**; bên trái có chọn/thả tệp, Batch/Replay và Bắt đầu dự đoán. Batch xử lý toàn tệp; Replay mô phỏng từng dòng và có tạm dừng/tiếp tục/dừng. Dừng và xóa có xác nhận; không gọi Replay là bắt gói thời gian thực. Input là feature gốc, không huấn luyện/fit lại hoặc đưa nhãn thật vào model/prompt.

Theo dõi có ngữ cảnh CSV, tiến độ, bốn ô thống kê thật và hai panel phân bố/kết quả gần đây. Không đưa số liệu kinh doanh từ demo Adminator vào ứng dụng. Các thẻ vận hành có chiều cao tự nhiên theo nội dung; monitor giữ stretch tại cặp panel hiện có.

## Bảng và giải thích

Khung nhìn đầu tiên của bảng gồm ngữ cảnh lần chạy, bộ lọc, hành động giải thích dòng đã chọn, bảng và khung xem nhanh; không thêm dãy KPI trên bảng dự đoán. Checkbox chọn nhiều dòng độc lập với dòng đang xem; đóng peek không bỏ lựa chọn. Dữ liệu dòng bắt đầu từ 0. Đi tới dòng kiểm tra dữ liệu và giữ đường quay lại; bảng rộng cuộn trong vùng bảng. Cột Thời điểm xử lý dùng thời điểm đã lưu của dự đoán và thời gian suy luận sẵn có từ API; Batch ghi Bình quân batch, Replay ghi Suy luận dòng. Đây là thời điểm xử lý mẫu CSV, không phải thời gian bắt gói mạng; không tải thêm feature cho từng dòng chỉ để làm đầy bảng.

Peek có Dự đoán / SHAP / Gemini và CTA đọc toàn bộ kết quả. Trang chi tiết có Toàn pipeline / Dự đoán / SHAP / Gemini, với Đầu vào / Đầu ra / Metadata / Lỗi. Mỗi lần mở giữ đúng run, row_index và audience_level; phản hồi đến trễ của dòng trước không ghi đè dòng mới. Hai mức Dễ hiểu/Kỹ thuật dùng chung SHAP, trạng thái Gemini riêng; màn chi tiết giữ mức Kỹ thuật theo triển khai hiện tại.

Giữ bộ chọn bước; mục lục **Trên trang này** theo dõi độc lập vị trí nội dung bước đang xem, Tệp kết quả và Đánh giá thủ công. Cuộn hoặc nhấp mục lục không đổi bước/tab/URL và không gửi yêu cầu SHAP/Gemini. Trên desktop, thanh bước cùng mục lục dính bên cạnh nội dung, có giới hạn chiều cao theo viewport và cuộn riêng khi cần. Từ 1000px trở xuống, chúng xếp thành các hàng phía trên để dành chiều ngang đọc. Tệp và form đánh giá nằm trong cùng vùng nội dung chi tiết, phân cách bằng đường kẻ, không lồng thêm card. Chuyển động cuộn tôn trọng reduced motion.

Giữ thứ tự lớp Normal, BruteForce, DDoS, DoS, Mirai, Recon, Spoofing, Web-Based và tên feature nguồn. Xác suất là “xác suất đầu ra”, chưa phải độ tin cậy hiệu chuẩn. SHAP thuộc xác suất toàn pipeline DT/RF/HGB → XGBoost trên 46 feature gốc; dương cam, âm xanh, kèm dấu, đơn vị điểm phần trăm và phần còn lại. Peek dùng top 3 + 43 feature; biểu đồ đầy đủ top 5 + 41 feature. SHAP không xác nhận nguyên nhân thực tế. Phương pháp hiện tại là PermutationExplainer trên toàn pipeline stacking. Thời lượng SHAP nhận từ trường shap_seconds theo giây; UI đổi đơn vị µs/ms/giây/phút/giờ bằng tính toán tương ứng, không chia 1.000 khi chưa có bằng chứng đơn vị nguồn thay đổi. Sai số bảo toàn không xác nhận nhãn thật hoặc chứng minh diễn giải Gemini không còn sai sót.

Chỉ nút yêu cầu chủ động mới tạo SHAP/Gemini; polling, đổi tab/mức, điều hướng và xuất chỉ đọc. Yêu cầu giải thích tối đa 50 dòng, gồm cả Normal. Retry Gemini là thao tác rõ ràng. Lỗi Gemini không xóa dự đoán hoặc SHAP đã có. Báo cáo Gemini phân cấp tóm tắt, bằng chứng, gợi ý và giới hạn; nội dung phải đúng mẫu/mức.

Vùng tệp của mẫu giữ bốn lựa chọn JSON, Markdown, CSV và waterfall có sẵn từ API. Markdown có **Bản trình bày / Văn bản gốc**: bản trình bày hỗ trợ tiêu đề, nhấn mạnh, code, danh sách và bảng GFM; bỏ HTML nhúng, giữ xử lý URL an toàn của thư viện, chỉ tải ảnh waterfall qua URL artifact đúng mẫu. Văn bản gốc và tệp tải không bị viết lại. Vùng đọc rộng tối đa 75ch, chữ 14px/1.8; nguồn dùng monospace 13px/1.8, phần tệp dài cuộn trong vùng tối đa 620px. Bảng CSV chỉ định dạng các cột value/shap_value tối đa sáu chữ số thập phân và impact_percentage_points bốn; số khác 0 nhỏ hơn ngưỡng hiển thị dùng dạng khoa học. Cột số căn phải, chữ số cố định; tệp nguồn giữ nguyên giá trị. Bảng rộng cuộn ngang trong vùng bảng, không nén số hoặc đẩy tràn toàn trang.

## Cảnh báo và Human review

Cảnh báo tạo từ dự đoán khác Normal. Bốn ô tổng quan lấy tổng thật theo phạm vi API và cập nhật theo hành vi hiện có. Bảng hiển thị mã dòng; UUID có trong thông tin lần chạy để phân biệt cùng chỉ số ở các run. Desktop có hồ sơ bên cạnh với header cố định/body cuộn; tablet/mobile chuyển xuống dưới và mở theo nội dung.

Giữ tiếp nhận, ghi chú tối đa 2.000 ký tự, đóng kèm xác nhận/lý do, mở lại và bảo vệ bản nháp khi đổi dòng/bộ lọc. CTA xem bằng chứng chỉ đọc. Trạng thái Mới → Đã tiếp nhận → Đã đóng → Đã tiếp nhận khi mở lại là tiến trình xử lý, không xác nhận nhãn thật, mức nghiêm trọng hoặc phản ứng chặn mạng.

Human review là form độc lập trên trang giải thích: thông tin người đánh giá, nhận định, nhãn đề xuất, ba điểm 1–5 mặc định trống và ghi chú. Không tự chấm hoặc mặc định đồng ý. Giữ xác nhận đối chiếu, lưu/tải JSON, cảnh báo bản cũ theo fingerprint và bảo vệ bản nháp. Trạng thái đóng cảnh báo, kiểm tra tự động và lời Gemini không thay review của người dùng.

## Xuất và trạng thái biên

Xuất gồm CSV, ZIP và báo cáo mẫu Markdown/PNG, với danh mục tệp nguồn thật. ZIP gom các tệp đã lưu; đổi mức chỉ ảnh hưởng danh mục mẫu, không phát sinh giải thích mới. Chỉ hiện nút tải khi có URL thật. Giữ xóa từng lần chạy, phạm vi dữ liệu bị xóa, khóa khi đang xử lý và phản hồi dọn tệp chưa hoàn tất.

Lỗi/chờ/mất kết nối/thiếu dữ liệu có nhãn và hành động phù hợp. Thiếu số liệu dùng dấu — và lý do, không dựng token/cost/cache/latency hoặc lấy metadata mẫu khác. Form, phiên cookie và API giữ hành vi hiện có. Không thay dữ liệu thật bằng dữ liệu reference.

## Tiêu chí màn hình

- Giữ bộ lọc, phân trang, lựa chọn và vị trí khi quay lại bảng theo cơ chế hiện có.
- Đúng run/dòng/mức đọc ở mọi đường mở mẫu, đọc bằng chứng và xuất.
- Desktop/tablet/mobile không tràn ngang cấp trang; bảng có vùng cuộn riêng.
- Cả nền sáng/tối có chữ trạng thái, focus bàn phím và vùng bấm phù hợp; reduced motion tắt chuyển động.
- Khối dữ liệu dài mở rộng hoặc cuộn đúng vùng; không áp chiều cao đồng đều lên mọi card.
- Chỉ đưa chỉ số vận hành có dữ liệu API thật vào trang Tổng quan; không thêm số liệu kinh doanh, tìm kiếm/avatar hoặc khả năng chặn mạng chỉ có trong tham chiếu demo.

Kiểm chứng và ảnh tại [FE/VERIFICATION.md](../VERIFICATION.md) và `FE/tests/results/`; mô hình thật và Gemini giả lập trong kiểm thử không chứng minh chất lượng trả lời của API Gemini thực.
