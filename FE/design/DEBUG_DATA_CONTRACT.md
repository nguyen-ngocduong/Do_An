# Dữ liệu cho màn debug từng bước

Hợp đồng FE/BE 1.2, cập nhật ngày 29/10/2026 trên nhánh `duong`. Giao diện giữ bố cục Langfuse đã chọn trên Miro và đọc dữ liệu của run/mẫu thực tế. Không thay đổi artifact nguồn.

## Nguồn mẫu và thời gian

Mẫu đang minh họa là dòng 14 của `output/xai_shap_runs/shap_20261022_021654_2555e479/selected_input.csv`, gắn với `case_015_Web-Based_correct`. Đủ 46 giá trị được đọc từ CSV và đối chiếu top 5 sau chuyển float32 với JSON SHAP. Chỉ số validation nguồn là 180934; chỉ số CSV nguồn là 282137. Các chỉ số này không thay thế cho chỉ số dòng trong file upload.

Không lấy bản ghi Gemini của dòng 14 trong integration run 50 mẫu để gắn vào đây: dòng đó là DDoS và thuộc một CSV khác. Với mẫu Web-Based hiện tại, chỉ thời gian SHAP `0.762579181999854 s` có nguồn xác nhận. Thời gian Predict, Gemini, tokens và lỗi Gemini hiển thị chưa có bản ghi. Không thay giá trị thiếu bằng 0.

Thời gian ghi trong artifact là phép đo nguồn. Khi có cache, `shap_seconds` và các giá trị `api_seconds` được tái sử dụng có thể vẫn là thời gian cũ; chúng không phải thời gian xử lý hoặc đọc cache của yêu cầu hiện tại. UI cần phân biệt thời gian ghi nhận, thời gian phục vụ yêu cầu và thời gian chờ hàng đợi.

## Trường đang có và trường còn thiếu

| Nội dung | Nguồn BE hiện tại | Cách trình bày / giới hạn |
|---|---|---|
| Thời gian Predict | `GET /api/runs/{run_id}/predictions`, `predict_seconds` | Replay: đo một dòng; Batch: thời gian batch chia đều. Không gọi hai cách đo này là cùng một loại latency |
| SHAP, sai số và thời gian | `GET /api/runs/{run_id}/explanations/{row_index}`, trường `explanation` | Giữ đơn vị xác suất, thời gian ghi nhận và nguồn snapshot |
| Đầu vào 46 đặc trưng | `GET /api/runs/{run_id}/inputs/{row_index}`, trường `features` | Đúng thứ tự model và float32 trước tiền xử lý; thiếu là null; không chứa label. Kiểm tra checksum mảng đã lưu, không suy luận lại |
| Input Gemini | URL `files["llm_input.json"]` trong chi tiết, khi file đã có | Đây là bằng chứng chương trình dựng. Prototype không khẳng định đã có request Gemini cho mẫu Web-Based |
| Diễn giải Gemini | Trường `gemini` và URL file báo cáo/bản nháp | Dùng đúng `audience_level`; bản nháp cần có nhãn |
| Thời gian và tổng tokens Gemini | URL `files["execution.json"]`, `files["gemini_status.json"]` | Tổng ghi nhận có thể gồm nhiều attempt; không tự coi là usage của riêng attempt được chọn |
| Model Gemini cấu hình | `GET /api/model`, `gemini_model` | Phân biệt model cấu hình với model/version phản hồi. Prototype chỉ ghi giá trị mặc định cấu hình, chưa biết model đã gọi cho mẫu này |
| Cấu hình SHAP | `GET /api/model`, `shap_config` | background_size, max_evals, additivity_tolerance từ runtime thật |
| Trạng thái và thông báo lỗi | `gemini_status`, `message` trong trạng thái giải thích | Có thể hiển thị ngay khi BE trả về; không suy ra nguyên nhân từ `queued` |
| HTTP code, error_type, model_version | Có thể có trong `gemini_response_*.json` phía server | File request/response chưa được REST cho tải; prototype ghi chưa được cung cấp |
| Phiên bản prompt / request hash | `request_sha256` có trong response cache phía server; chưa có version prompt riêng | Không dùng hash của model hoặc config thay cho version prompt |
| Cache hit/miss từng bước | BE có tái sử dụng, nhưng chưa trả cờ runtime rõ ràng | Hiển thị chưa có cờ xác nhận; artifact đã lưu không đồng nghĩa cache hit trong lần gọi hiện tại |

Các URL file lấy từ trường `files` do BE cung cấp, theo đúng mức diễn giải. Không đoán đường dẫn runtime. Nếu bổ sung debug API ở bước sau, chỉ trả metadata cần thiết; không trả khóa hoặc thông tin xác thực từ request/exception.

## Nội dung prototype

Mỗi bước có bốn tab Đầu vào / Đầu ra / Metadata / Lỗi. Đầu vào Predict và SHAP chứa 46 giá trị gốc có thể chọn sao chép. Đầu vào Gemini phân biệt bằng chứng sẵn có với `llm_input.json` thực tế chưa tồn tại trong fixture này. Phần lời giải tiếng Việt tiếp tục là ví dụ bố cục.

Ứng dụng dùng textarea chỉ đọc và nút sao chép. Nếu Clipboard API không khả dụng, chọn JSON để người dùng nhấn Ctrl+C/⌘C. Nội dung CSV/API được React render dưới dạng text hoặc JSON chỉ đọc; không chèn HTML từ phản hồi.

Vùng “Đi tới run / dòng” nhận run_id 32 ký tự hex và row_index từ 0, gọi API kiểm tra run và giới hạn dòng. Ứng dụng thực hiện:

1. Kiểm tra run bằng `GET /api/runs/{run_id}`; xử lý ID không hợp lệ và 404 ngay tại ô nhập.
2. Đọc đúng dòng từ các trang dự đoán theo thứ tự dòng; không coi offset của bảng đã lọc là row_index. Nếu dòng chưa dự đoán, hiện trạng thái chờ, không báo model lỗi.
3. Lưu run_id, offset, limit, bộ lọc lớp/trạng thái, audience_level, dòng đang xem và vị trí cuộn trong trạng thái FE hoặc URL trước khi mở chi tiết.
4. Khi trở lại, khôi phục trạng thái này thay vì tạo lần chạy/yêu cầu giải thích mới. URL giữ bộ lọc/phân trang; sessionStorage giữ lựa chọn và vị trí cuộn.

Timeline, thời gian hàng đợi và chi phí không được thêm trong đợt này. Các trường thiếu cần bổ sung hợp đồng BE trước khi FE hiển thị số thật.
