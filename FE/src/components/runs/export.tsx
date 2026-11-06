"use client";
import Link from "next/link";
import { useCallback, useState } from "react";
import {
    Archive,
    CheckCircle2,
    Clock3,
    FileSpreadsheet,
    FileText,
    FolderOpen,
    Image as ImageIcon,
} from "lucide-react";
import { getRun, getSummary } from "@/lib/api/runs";
import { getExplanation, listExplanations } from "@/lib/api/explanations";
import { usePolling } from "@/lib/use-polling";
import { number, rowName, time } from "@/lib/format";
import type { Audience } from "@/types/model";
import {
    AudienceSelect,
    Badge,
    DownloadButton,
    Empty,
    ErrorNotice,
    Loading,
    PageHeading,
    RunTabs,
} from "@/components/shared/controls";

// Tệp nền luôn có trong ZIP; tệp giải thích lấy từ danh sách thật của mẫu.
const ZIP_FILES = [
    ["predictions.csv", "Nhãn, xác suất tám lớp và thời gian suy luận"],
    ["input_features.csv", "Đặc trưng đầu vào của lần chạy"],
    ["protocol.json", "Cấu hình và dấu vết lần chạy"],
    ["run_status.json", "Trạng thái và tiến độ tại lúc xuất"],
    ["explanations.json", "Trạng thái giải thích của các mẫu và mức diễn giải"],
    ["alerts.json", "Các cảnh báo theo mô hình"],
    ["alert_history.json", "Lịch sử tiếp nhận và ghi chú vận hành"],
    ["human_reviews.json", "Đánh giá thủ công đã lưu, kèm dấu vân tay bằng chứng"],
];
const FILE_DESCRIPTIONS: Record<string, string> = {
    "waterfall.png": "Biểu đồ đóng góp SHAP trên đặc trưng gốc",
    "report_vi.md": "Báo cáo tiếng Việt của mẫu; giữ trạng thái và giới hạn",
    "explanation.json": "Dự đoán và bằng chứng SHAP",
    "shap_values.npz": "Mảng giá trị SHAP đã lưu",
    "top5_features.csv": "Năm đặc trưng có đóng góp lớn nhất",
    "playbook.json": "Hướng dẫn kiểm tra tham khảo theo lớp",
    "llm_input.json": "Bằng chứng đã gửi cho Gemini",
    "explanation_vi.json": "Diễn giải Gemini đạt kiểm tra tự động",
    "explanation_vi_draft.json": "Bản nháp Gemini cần sửa",
    "gemini_status.json": "Trạng thái và thông báo lần gọi Gemini",
    "execution.json": "Thông tin thực thi và thời gian xử lý",
};

export function RunExport({ id }: { id: string }) {
    const [audience, setAudience] = useState<Audience>("technical");
    const [chosenRow, setChosenRow] = useState("");
    const load = useCallback(
        async (signal: AbortSignal) => {
            const [run, summary, explanations] = await Promise.all([
                getRun(id, signal),
                getSummary(id, signal, audience),
                listExplanations(id, audience, signal),
            ]);
            const available = explanations.items.filter((item) =>
                ["completed", "partial"].includes(item.status),
            );
            const selected =
                available.find(
                    (item) => String(item.row_index) === chosenRow,
                ) || available[0];
            const detail = selected
                ? await getExplanation(id, selected.row_index, audience, signal)
                : null;
            return { run, summary, available, detail };
        },
        [id, audience, chosenRow],
    );
    const poll = usePolling(`export:${id}:${audience}:${chosenRow}`, load);
    const data = poll.data;
    const files = Object.entries(data?.detail?.files || {});
    const csvPath = `/api/runs/${id}/export?format=csv`;
    const zipPath = `/api/runs/${id}/export?format=zip`;

    return (
        <div className="export-page">
            <PageHeading
                title="Xuất kết quả & Báo cáo"
                description="Tải dự đoán, bằng chứng SHAP và báo cáo Gemini đã lưu của lần chạy."
            />
            <RunTabs id={id} selected="export" />
            <ErrorNotice error={poll.error} retry={poll.refresh} />
            {!data ? (
                <Loading />
            ) : (
                <>
                    <div className="export-snapshot" id="export-snapshot">
                        {data.run.status === "completed" ? (
                            <CheckCircle2
                                className="snapshot-icon"
                                aria-hidden="true"
                            />
                        ) : (
                            <Clock3
                                className="snapshot-icon"
                                aria-hidden="true"
                            />
                        )}
                        <div>
                            <div className="export-snapshot-title">
                                <Badge
                                    status={data.summary.prediction_status}
                                />
                                <strong>
                                    Đã dự đoán{" "}
                                    {number(data.summary.processed_rows)} /{" "}
                                    {number(data.summary.total_rows)} dòng
                                </strong>
                            </div>
                            <p>
                                {data.run.filename} · Cập nhật{" "}
                                {time(data.run.updated_at)}
                            </p>
                        </div>
                        <span className="export-snapshot-note">
                            Snapshot tại thời điểm tải
                        </span>
                    </div>
                    <div className="export-options">
                        <section className="export-card" data-format="csv">
                            <div className="export-card-top">
                                <FileSpreadsheet
                                    className="export-format-icon"
                                    aria-hidden="true"
                                />
                                <span className="export-extension">.CSV</span>
                            </div>
                            <h2>Dự đoán CSV</h2>
                            <p>
                                Nhãn dự đoán, xác suất tám lớp, chỉ số dòng và
                                thời gian suy luận của từng mẫu.
                            </p>
                            <dl className="export-facts">
                                <div>
                                    <dt>Dòng đã lưu</dt>
                                    <dd>
                                        {number(data.summary.processed_rows)}{" "}
                                        dòng
                                    </dd>
                                </div>
                                <div>
                                    <dt>Định dạng</dt>
                                    <dd>UTF-8 · Phân tách dấu phẩy</dd>
                                </div>
                                <div>
                                    <dt>Phạm vi</dt>
                                    <dd>Toàn lần chạy</dd>
                                </div>
                            </dl>
                            <div className="export-card-action">
                                <DownloadButton
                                    path={csvPath}
                                    name={`${id}_predictions.csv`}
                                >
                                    Tải CSV
                                </DownloadButton>
                            </div>
                        </section>
                        <section
                            className="export-card export-card-featured"
                            data-format="zip"
                        >
                            <span className="export-recommended">
                                Đầy đủ tệp đã lưu
                            </span>
                            <div className="export-card-top">
                                <Archive
                                    className="export-format-icon"
                                    aria-hidden="true"
                                />
                                <span className="export-extension">.ZIP</span>
                            </div>
                            <h2>Gói báo cáo ZIP</h2>
                            <p>
                                Gom đầu vào, dự đoán, bằng chứng SHAP, báo cáo
                                từng mẫu và lịch sử cảnh báo đã có.
                            </p>
                            <dl className="export-facts">
                                <div>
                                    <dt>Nội dung</dt>
                                    <dd>Dữ liệu + bằng chứng + báo cáo</dd>
                                </div>
                                <div>
                                    <dt>Mức diễn giải</dt>
                                    <dd>Các mức đã lưu</dd>
                                </div>
                                <div>
                                    <dt>Tạo gói</dt>
                                    <dd>Khi bạn bấm tải</dd>
                                </div>
                            </dl>
                            <div className="export-card-action">
                                <DownloadButton
                                    path={zipPath}
                                    name={`${id}_reports.zip`}
                                >
                                    Chuẩn bị & tải ZIP
                                </DownloadButton>
                            </div>
                        </section>
                        <section className="export-card" data-format="case">
                            <div className="export-card-top">
                                <FileText
                                    className="export-format-icon"
                                    aria-hidden="true"
                                />
                                <span className="export-extension">
                                    .MD / .PNG
                                </span>
                            </div>
                            <h2>Báo cáo giải thích từng mẫu</h2>
                            <p>
                                Đọc báo cáo tiếng Việt, tải biểu đồ SHAP hoặc dữ
                                liệu giải thích của mẫu cần đối chiếu.
                            </p>
                            <dl className="export-facts">
                                <div>
                                    <dt>Mẫu có kết quả</dt>
                                    <dd>
                                        {number(data.available.length)} mẫu ở
                                        mức đang chọn
                                    </dd>
                                </div>
                                <div>
                                    <dt>Biểu đồ</dt>
                                    <dd>Waterfall SHAP</dd>
                                </div>
                                <div>
                                    <dt>Báo cáo</dt>
                                    <dd>Markdown tiếng Việt</dd>
                                </div>
                            </dl>
                            <a
                                className="button export-card-action"
                                href="#export-files"
                            >
                                <FolderOpen
                                    className="icon"
                                    aria-hidden="true"
                                />
                                Chọn mẫu & xem tệp
                            </a>
                        </section>
                    </div>
                    <section
                        className="export-catalog"
                        id="export-files"
                        aria-labelledby="export-files-title"
                    >
                        <div className="export-catalog-heading">
                            <div>
                                <h2 id="export-files-title">
                                    <FolderOpen
                                        className="icon"
                                        aria-hidden="true"
                                    />
                                    Danh mục tệp kết quả
                                </h2>
                                <p>
                                    Tệp nền trong ZIP và tệp thực tế của mẫu
                                    đang chọn.
                                </p>
                            </div>
                            <span className="badge neutral">
                                {ZIP_FILES.length} tệp nền trong ZIP
                            </span>
                        </div>
                        <div className="table-wrap">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Tên tệp</th>
                                        <th>Nội dung</th>
                                        <th>Phạm vi</th>
                                        <th>Tải xuống</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {ZIP_FILES.map(([name, description]) => (
                                        <tr key={name}>
                                            <td className="mono">
                                                <FileText
                                                    className="icon"
                                                    aria-hidden="true"
                                                />
                                                {name}
                                            </td>
                                            <td className="wrap">
                                                {description}
                                            </td>
                                            <td>
                                                <span className="badge neutral">
                                                    Toàn lần chạy
                                                </span>
                                            </td>
                                            <td>
                                                {name === "predictions.csv" ? (
                                                    <DownloadButton
                                                        path={csvPath}
                                                        name="predictions.csv"
                                                    >
                                                        Tải CSV
                                                    </DownloadButton>
                                                ) : (
                                                    <span className="muted">
                                                        Trong gói ZIP
                                                    </span>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <div className="export-case-filters filters">
                            <label>
                                Mức diễn giải
                                <AudienceSelect
                                    id="export-audience"
                                    value={audience}
                                    onChange={(value) => {
                                        setAudience(value);
                                        setChosenRow("");
                                    }}
                                />
                            </label>
                            <label>
                                Mẫu đã giải thích
                                <select
                                    id="export-case"
                                    value={data.detail?.row_index ?? ""}
                                    disabled={!data.available.length}
                                    onChange={(event) =>
                                        setChosenRow(event.target.value)
                                    }
                                >
                                    {!data.available.length && (
                                        <option value="">Chưa có mẫu</option>
                                    )}
                                    {data.available.map((item) => (
                                        <option
                                            key={item.row_index}
                                            value={item.row_index}
                                        >
                                            Dòng {rowName(item.row_index)}
                                        </option>
                                    ))}
                                </select>
                            </label>
                            {data.detail && (
                                <Link
                                    className="button"
                                    href={`/runs/${id}/rows/${data.detail.row_index}?audience=${audience}`}
                                >
                                    Mở giải thích mẫu
                                </Link>
                            )}
                        </div>
                        {!files.length ? (
                            <Empty
                                title="Chưa có tệp giải thích ở mức này"
                                description="Chọn mức khác hoặc quay lại bảng dự đoán để yêu cầu SHAP/Gemini."
                            />
                        ) : (
                            <div className="table-wrap" id="export-case-files">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>
                                                Tệp của dòng{" "}
                                                {rowName(
                                                    data.detail!.row_index,
                                                )}
                                            </th>
                                            <th>Nội dung</th>
                                            <th>Trạng thái mẫu</th>
                                            <th>Tải xuống</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {files.map(([name, path]) => (
                                            <tr key={name}>
                                                <td className="mono">
                                                    {name.endsWith(".png") ? (
                                                        <ImageIcon
                                                            className="icon"
                                                            aria-hidden="true"
                                                        />
                                                    ) : (
                                                        <FileText
                                                            className="icon"
                                                            aria-hidden="true"
                                                        />
                                                    )}
                                                    {name}
                                                </td>
                                                <td className="wrap">
                                                    {FILE_DESCRIPTIONS[name] ||
                                                        "Tệp kết quả đã lưu"}
                                                </td>
                                                <td>
                                                    <Badge
                                                        status={
                                                            data.detail?.status
                                                        }
                                                    />
                                                </td>
                                                <td>
                                                    <DownloadButton
                                                        path={path}
                                                        name={name}
                                                    >
                                                        Tải về
                                                    </DownloadButton>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </section>
                    <p className="scope-note">
                        Snapshot có thể chưa đủ mọi mẫu nếu tác vụ đang chạy.
                        ZIP gồm các mức diễn giải đã lưu; bộ chọn mức/mẫu chỉ
                        đổi danh mục tệp bên dưới. Báo cáo có thể gồm trạng thái
                        hoặc bản nháp cần sửa. Xuất kết quả không chạy lại
                        model, SHAP hay gọi Gemini. Chưa hỗ trợ xuất PDF.
                    </p>
                </>
            )}
        </div>
    );
}
