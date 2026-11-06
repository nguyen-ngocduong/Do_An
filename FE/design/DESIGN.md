---
name: NIDR
description: Giao diện vận hành CSV, dự đoán và bằng chứng SHAP/Gemini theo tham chiếu Adminator.
colors:
  bg: "#f1f5f9"
  nav: "#ffffff"
  panel: "#ffffff"
  raised: "#f8fafc"
  line: "#e2e8f0"
  field-line: "#bac7d8"
  text: "#1e293b"
  muted: "#60718a"
  primary: "#2563eb"
  action: "#2563eb"
  action-hover: "#1d4ed8"
  button: "#2563eb"
  on-button: "#ffffff"
  success: "#15803d"
  warn: "#b45309"
  danger: "#dc2626"
  positive: "#a34a0a"
  negative: "#1d4ed8"
  selected: "#eff6ff"
  dark-bg: "#111827"
  dark-nav: "#172033"
  dark-panel: "#1d293c"
  dark-raised: "#253449"
  dark-line: "#37465b"
  dark-field-line: "#73849c"
  dark-text: "#f1f5f9"
  dark-muted: "#bac7da"
  dark-primary: "#93c5fd"
  dark-button: "#2563eb"
  dark-on-button: "#ffffff"
  dark-success: "#8ed9b6"
  dark-warn: "#f0c77b"
  dark-danger: "#fda4af"
  dark-positive: "#f7ad69"
  dark-negative: "#9ac7fa"
  dark-selected: "#1e3659"
  shap-bar-positive: "#c95e17"
  shap-bar-negative: "#235fa0"
  dark-shap-bar-positive: "#f7ad69"
  dark-shap-bar-negative: "#60a5fa"
typography:
  headline:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "28px"
    fontWeight: 600
    lineHeight: 1.35
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: 1.5
  body:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.6
  table:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "13px"
    lineHeight: 1.6
  label:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "12px"
    lineHeight: 1.6
  mono:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "max(13px, 0.94em)"
rounded:
  text-action: "4px"
  notice: "6px"
  control: "8px"
  inset: "10px"
  table: "12px"
  panel: "14px"
  login: "16px"
  pill: "9999px"
spacing:
  compact: "4px"
  small: "8px"
  field: "12px"
  group: "16px"
  panel: "20px"
  section: "24px"
  page: "32px"
components:
  button-primary:
    backgroundColor: "{colors.button}"
    textColor: "{colors.on-button}"
    rounded: "{rounded.control}"
    padding: "8px 14px"
  button-primary-hover:
    backgroundColor: "{colors.action-hover}"
    textColor: "{colors.on-button}"
  button-secondary:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    rounded: "{rounded.control}"
    padding: "8px 14px"
  button-text:
    textColor: "{colors.primary}"
    rounded: "{rounded.text-action}"
    padding: "4px 8px"
  input:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    rounded: "{rounded.control}"
    padding: "8px 10px"
  nav-active:
    backgroundColor: "{colors.selected}"
    textColor: "{colors.primary}"
    rounded: "{rounded.control}"
    padding: "10px 12px"
  badge:
    backgroundColor: "{colors.raised}"
    textColor: "{colors.muted}"
    rounded: "{rounded.pill}"
    padding: "2px 8px"
  panel:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    rounded: "{rounded.panel}"
    padding: "20px"
  site-footer:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    padding: "28px 32px"
---

# Design System: NIDR

## Overview

**Creative North Star: "NIDR theo tham chiếu Adminator"**

NIDR — Network Intrusion Detection and Response dùng ngôn ngữ Adminator mà người dùng chọn: điều hướng và header trắng, canvas xám xanh, điểm nhấn xanh dương, các khối nội dung có viền nhẹ. Nhận diện này áp dụng cho ứng dụng Next.js/React hiện tại; token thực thi nằm trong `FE/src/app/globals.css`, font được nạp tại `FE/src/app/layout.tsx`.

Hệ thống ưu tiên đọc bảng, chọn mẫu và đối chiếu bằng chứng. Chiều cao khối theo nội dung; các biến thể chuyên biệt vẫn giữ tỷ lệ chữ phù hợp với công việc. Nền radial và bóng mềm của đăng nhập là quyết định riêng đã được người dùng giữ lại.

**Key Characteristics:**

- Canvas xám xanh và điều hướng trắng; xanh dương cho hành động và trạng thái chọn.
- Inter cho giao diện; JetBrains Mono và số có độ rộng ổn định cho đối chiếu.
- Panel có viền, khoảng cách thoáng; các bảng và khung bằng chứng giữ mật độ đọc.
- Nền tối dùng xanh than và liên kết xanh nhạt; trạng thái luôn có chữ.

## Colors

Frontmatter là bảng token chuẩn; khóa `dark-*` là giá trị ghi đè của cùng vai trò khi `data-theme="dark"`. Các giá trị giữ nguyên định dạng hex của source.

### Primary

- **Xanh hành động** (`button`, `action`, `action-hover`): nút chính, CTA xuất và đăng nhập; chữ trắng giữ ở cả hai theme.
- **Xanh liên kết** (`primary`): link, focus, icon nhấn và tab đang chọn. Nền tối đổi sang xanh nhạt để đọc trên xanh than; không dùng màu link nền tối làm nền nút chữ trắng.
- **Nền chọn xanh nhạt** (`selected`): mục điều hướng hiện tại, hàng được chọn và lựa chọn Batch/Replay.

### Neutral

- **Canvas xám xanh** (`bg`), **điều hướng trắng** (`nav`) và **panel trắng** (`panel`): phân tách shell với vùng làm việc.
- **Nền nâng nhẹ** (`raised`): header bảng, hover và vùng nhập tệp. `line` phân chia khối; `field-line` làm rõ ô nhập.
- **Chữ xanh than** (`text`) và **chữ phụ xanh xám** (`muted`): phân cấp nội dung và chú thích. Bản tối dùng các cặp `dark-*` tương ứng.

### Semantic

- `success`, `warn`, `danger` mô tả kết quả/trạng thái; dùng kèm chữ và icon, không chỉ màu.
- `positive`/`negative` dùng cho chữ đóng góp SHAP. Thanh và chú giải dùng `shap-bar-positive`/`shap-bar-negative`; nền tối có giá trị riêng. Dương cam, âm xanh, luôn giữ dấu số.
- Badge lớp có bảng màu riêng trong source; không ép tám lớp về một bảng xếp hạng mức nghiêm trọng.

**The Semantic Color Rule.** Màu nhãn lớp giúp nhận diện lớp; màu trạng thái mô tả xử lý. Cả hai không xác nhận mức nghiêm trọng hoặc nhãn thật.

## Typography

**Body / heading font:** Inter, system-ui, sans-serif; **Mono font:** JetBrains Mono, ui-monospace, monospace. Next/font nạp hai font với tập ký tự tiếng Việt; biến thực thi là `--font-ui` và `--font-mono`.

- **Headline:** tiêu đề trang dùng token `headline` (28px/600, line-height 1.35).
- **Title:** tiêu đề khối chung (16px/600, line-height 1.5).
- **Body:** giao diện nền (14px, line-height 1.6); **table** (13px); **label** và chú thích (12px).
- **Mono:** công thức `max(13px, 0.94em)` và tabular numerals cho số/ID cần so sánh; không chuyển toàn bộ nội dung sang mono.
- **Biến thể theo ngữ cảnh:** đăng nhập có tiêu đề 26px; peek có nhãn dự đoán 22px và xác suất 27px; tổng quan cảnh báo 24px; số theo dõi 28px, xuống 24px trên mobile. Báo cáo Gemini dùng thân 15px/1.85, phần tóm tắt 16px/1.9; mobile giảm lần lượt còn 14px và 15px. Các selector con có thể ghi đè cỡ nền.

**The Contextual Type Rule.** Cỡ chữ nền không ghi đè các tỷ lệ đã có của số liệu, khung xem nhanh, báo cáo và đăng nhập.

## Layout

- Desktop: shell hai cột, sidebar rộng 248px hoặc 88px khi thu gọn. Sidebar dính ở cạnh; workspace cao `100dvh`, nội dung cuộn trong vùng chính. Header cao tối thiểu 60px, đệm 10px 32px; main đệm 32px 32px 40px, không có khung giấy bao ngoài.
- Nhịp khoảng cách gồm 8/12/16/20/24/32px, chọn theo mật độ. Panel chung đệm 20px; upload đệm 24px, hai cột 1.35:1 cách 24px và căn trên. Chiều cao hai card có thể khác nhau theo nội dung.
- Bảng dự đoán là workspace với bộ lọc, chọn dòng và bảng; peek rộng 334px. Dưới hoặc bằng 1080px, peek xuống dưới bảng. Bộ lọc về hai cột khi không đủ rộng. Bảng tự cuộn trong vùng chứa.
- Theo dõi, cảnh báo và xuất có bề rộng tối đa 1440px; báo cáo Gemini tối đa 1160px. Monitor có bốn ô số liệu thật và hai panel 0.9:1.1; dưới hoặc bằng 1150px đổi sang hai ô mỗi hàng và panel một cột. Xuất ba lựa chọn, xếp dọc ở cùng ngưỡng.
- Cảnh báo có bảng và hồ sơ khi đủ rộng; dưới hoặc bằng 1000px hồ sơ xuống dưới và bỏ giới hạn chiều cao. Desktop giữ header hồ sơ, cuộn body. Upload cũng về một cột ở ngưỡng này.
- Mobile dưới hoặc bằng 760px: hàng thương hiệu + Menu, menu hai cột khi mở; Escape/điều hướng đóng menu. Desktop thu gọn không làm ẩn menu mobile. Main đệm 20px 16px 32px; nút/ô nhập chính có vùng thao tác tối thiểu 44px; bảng rộng không gây tràn toàn trang. Panel chung đệm 16px, upload 18px. Nội dung chi tiết xếp theo chiều dọc.
- Sidebar lưu lựa chọn tại `nidr:sidebar`; theme dùng tùy chọn hiện có. Không đưa thông tin phiên vào phần lưu tùy chọn UI.

## Elevation & Depth

Các khối vận hành chủ yếu phẳng: nền panel, viền một nét và nền raised/selected tạo thứ bậc. Panel, upload, bộ lọc, thống kê và CTA không cần bóng lặp lại. Không ép card vận hành cùng chiều cao khi nội dung khác nhau; hai panel theo dõi vẫn stretch theo bố cục hiện có.

- **Tra cứu nổi:** `0 4px 18px rgba(0, 0, 0, 0.08)` để tách popover khỏi bảng.
- **Đăng nhập:** `0 10px 25px -5px rgba(25, 20, 60, 0.13)`; tối `0 10px 25px -5px rgba(0, 0, 0, 0.45)`. Hai radial xanh dương trên canvas giữ theo lựa chọn người dùng, không mở rộng thành nền cho mọi màn hình vận hành.
- `--shadow-subtle` dùng riêng trên KPI dashboard theo ảnh người dùng; `--shadow-card` chưa có nơi sử dụng. Không xem hai biến đó là yêu cầu thêm bóng ở các nơi khác.

**The Evidence First Rule.** Giữ dữ liệu, dấu số, đơn vị và trạng thái đọc được trước khi thêm trang trí.

## Shapes

Panel chung bo mềm theo `panel`; nút/ô nhập theo `control`. Bảng, thống kê, bộ lọc và hồ sơ cảnh báo dùng góc 12px; khối inset 10px, thông báo 6px, nút chữ 4px, badge hình viên thuốc. Card đăng nhập 16px. Viền panel dùng `line`, ô nhập dùng `field-line`; không đồng nhất tất cả góc bo về một giá trị.

## Components

### Buttons

Nút hành động gọn, có nhãn rõ: nền chính xanh, chữ trắng; phụ nền panel có viền; nút chữ dùng primary. Nút chung cao tối thiểu 40px, đệm 8px 14px. Hover dùng nền tương ứng; active thu nhẹ `scale(0.985)`, disabled giảm opacity và bỏ transform. Hành động xóa/xác nhận phá hủy có màu đỏ và hộp xác nhận phù hợp, không thay bằng nút chính xanh.

### Inputs / Fields

Nền panel, viền field-line, đệm 8px 10px, cao tối thiểu 38px. Label và trợ giúp theo nhóm 6px. Focus bàn phím chung có outline primary 2px cách 3px; ô đăng nhập cao ít nhất 48px, chữ 16px. Giữ lỗi bằng văn bản, trường readonly và trạng thái khóa thực tế. Chọn Batch/Replay có border primary và nền selected khi chọn; vùng thả CSV nền raised và viền đứt, chuyển selected khi kéo tệp.

### Navigation

Điều hướng trái có icon Lucide nét 1.65, kích thước 24px, label 14px. Mục hiện tại dùng nền selected, primary và chữ 600; hover nền raised. Thu gọn đặt icon trên nhãn 12px, tooltip/tên truy cập đầy đủ. Phần cuối sidebar chỉ giữ liên kết Swagger API và dòng đồ án, không còn thẻ mô hình đã chốt hoặc chuỗi kiến trúc model. Tab nội dung có gạch dưới primary và nhãn trạng thái; không dùng tab để khởi tạo giải thích mới. Breadcrumb và thao tác header chỉ hiển thị chức năng thật.

### Cards / Containers

Panel nền panel, viền line và đệm theo vai trò. Hàng bảng thường cao 50px; cảnh báo 60px; cột số và xác suất căn phải, dùng tabular numerals. Checkbox chọn nhiều dòng độc lập với hàng đang xem nhanh; đóng peek giữ lựa chọn. Preview có vùng cuộn và footer đọc toàn bộ kết quả. Không cắt báo cáo dài theo chiều cao một card giả định.

### Chips / Status

Badge có chữ 12px, viền và nền nhẹ; màu là hỗ trợ nhận diện. Trạng thái dự đoán, SHAP, Gemini, cảnh báo, Human review và kết nối độc lập. “Mới”, “Đã tiếp nhận”, “Đã đóng” là trạng thái xử lý cảnh báo, không phải sự thật của nhãn. Gemini lỗi vẫn cho đọc SHAP đã lưu.

### Evidence / Reports

Đường đọc chính là CSV → dự đoán → SHAP → Gemini → rà cảnh báo. Giữ ngữ cảnh run/dòng/mức đọc và tên lớp/feature gốc. SHAP giải thích xác suất toàn pipeline trên 46 feature gốc; giữ phần còn lại, dấu và đơn vị. Trang chi tiết có Toàn pipeline / Dự đoán / SHAP / Gemini và Đầu vào / Đầu ra / Metadata / Lỗi. Human review giữ form, xác nhận đối chiếu và bản nháp riêng; báo cáo/tệp chỉ đọc kết quả đã có. Quy tắc tác vụ đầy đủ ở [SURFACE.md](SURFACE.md).

### Site Footer

Chân trang dùng chung (`SiteFooter`) là dải phẳng dùng nền `panel`, chữ `text`/`muted`, liên kết `primary` và đường phân cách `line`, theo yêu cầu thay footer Navy bằng màu phù hợp với UI sáng. Nền sáng hiện trắng; nền tối tự dùng token panel tối, không giữ một màu Navy cố định cho cả hai theme. Hover liên kết đổi sang `text` và có gạch dưới; focus có outline primary. Bố cục 4 cột tổ chức (NIDR, Đơn vị đào tạo, Nhóm thực hiện, Liên kết nhanh) và dải tên nhóm/năm; tự co về 2 cột ở tablet (≤1100px) và 1 cột ở mobile (≤600px). Nằm trong luồng cuộn tự nhiên, không bo khung/đổ bóng hoặc cố định đè thao tác. Chữ nền 14px/1.7, thông tin phụ 12px, thương hiệu 22px; thông tin nhóm và đường dẫn vẫn giữ nguyên.

Chuyển trạng thái có mục đích: hover/link 150ms ease, nhấn 100ms ease, sidebar 180ms ease-out. Khi reduced motion bật, tắt animation/transition và cuộn mượt; spinner đăng nhập cũng theo quy tắc này.

## Do's and Don'ts

### Do:

- Do giữ thứ tự Normal, BruteForce, DDoS, DoS, Mirai, Recon, Spoofing, Web-Based và tên feature gốc.
- Do giữ dấu đóng góp SHAP, đơn vị điểm phần trăm, xác suất nền/đầu ra và phần đặc trưng còn lại.
- Do dùng dữ liệu BE thật; giá trị thiếu hiển thị dấu — và lý do khi có.
- Do giữ focus rõ, tên truy cập, vùng bấm mobile và chế độ giảm chuyển động.
- Do giữ chiều cao khối theo nội dung và kiểm tra cả nền sáng/tối, desktop/tablet/mobile.

### Don't:

- Don't đưa số liệu kinh doanh, tìm kiếm toàn cục hoặc avatar từ demo Adminator vào NIDR khi chưa có chức năng thật.
- Don't gọi xác suất đầu ra là độ tin cậy đã hiệu chuẩn hoặc coi SHAP là nguyên nhân thực tế.
- Don't dùng trạng thái đóng cảnh báo, kiểm tra tự động hoặc văn bản Gemini để thay xác nhận nhãn thật/Human review.
- Don't gọi SHAP/Gemini mới chỉ vì mở tab, đổi mức đọc, polling hoặc xuất tệp.
- Don't áp lại mô tả tím/framed-sheet, số đo shell cũ hoặc bóng trên mọi panel từ các đợt thiết kế trước.
