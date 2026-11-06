"use client";
import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Check, FileText, Upload, X } from "lucide-react";
import { createRun } from "@/lib/api/runs";
import { useAction } from "@/lib/use-action";
import { useUi } from "@/store/ui-store";
import { CLASS_NAMES } from "@/types/model";
import { number } from "@/lib/format";
import {
    ClassBadge,
    DownloadButton,
    ErrorNotice,
    Loading,
    PageHeading,
} from "@/components/shared/controls";

export function UploadRun() {
    const ui = useUi();
    const router = useRouter();
    const action = useAction();
    const fileInput = useRef<HTMLInputElement>(null);
    const [file, setFile] = useState<File | null>(null);
    const [mode, setMode] = useState("batch");
    const [interval, setInterval] = useState("1");
    const [dragging, setDragging] = useState(false);
    const metadata = ui.metadata.data;

    function clearFile() {
        setFile(null);
        if (fileInput.current) fileInput.current.value = "";
        document.getElementById("choose-csv")?.focus();
    }
    return (
        <>
            <PageHeading
                title="Tạo lần chạy"
                description="Tải CSV đặc trưng gốc. Server tái sử dụng model và tiền xử lý đã đóng băng."
            />
            <div className="upload-layout">
                <form
                    id="create-form"
                    className="panel upload-panel"
                    onSubmit={(event) => {
                        event.preventDefault();
                        void action.run(
                            async () => {
                                if (
                                    !file ||
                                    !file.name.toLowerCase().endsWith(".csv") ||
                                    !file.size ||
                                    file.size >
                                        (metadata?.model.limits.upload_bytes ||
                                            10 * 1024 * 1024)
                                )
                                    throw new Error(
                                        "Chọn file .csv không rỗng, dung lượng tối đa 10 MiB.",
                                    );
                                const data = new FormData();
                                data.append("file", file);
                                data.append("mode", mode);
                                data.append(
                                    "interval_seconds",
                                    mode === "replay" ? interval : "1",
                                );
                                return createRun(data);
                            },
                            (run) => router.push(`/runs/${run.id}/monitor`),
                        );
                    }}
                >
                    <h2>Dữ liệu đầu vào</h2>
                    <div
                        className={`dropzone ${dragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
                        onDragOver={(event) => {
                            event.preventDefault();
                            setDragging(true);
                        }}
                        onDragLeave={() => setDragging(false)}
                        onDrop={(event) => {
                            event.preventDefault();
                            setDragging(false);
                            setFile(event.dataTransfer.files[0] || null);
                        }}
                    >
                        <div className="upload-drop-title">
                            <Upload className="icon" aria-hidden="true" />
                            <strong>Chọn hoặc thả file CSV vào đây</strong>
                        </div>
                        <p className="muted small">
                            Tối đa{" "}
                            {number(metadata?.model.limits.csv_rows || 1000)}{" "}
                            dòng / 10 MiB. Cột label là tùy chọn.
                        </p>
                        <input
                            ref={fileInput}
                            id="csv-file"
                            className="visually-hidden"
                            tabIndex={-1}
                            type="file"
                            accept=".csv,text/csv"
                            aria-label="File CSV đầu vào"
                            onChange={(event) =>
                                setFile(event.target.files?.[0] || null)
                            }
                        />
                        <div className="file-picker">
                            <button
                                type="button"
                                id="choose-csv"
                                onClick={() => fileInput.current?.click()}
                            >
                                <Upload className="icon" aria-hidden="true" />
                                {file ? "Đổi file" : "Chọn file"}
                            </button>
                            <span className="muted small" aria-live="polite">
                                {file
                                    ? "File đã sẵn sàng để kiểm tra"
                                    : "Chưa có file nào được chọn"}
                            </span>
                        </div>
                        {file && (
                            <div className="selected-file">
                                <FileText className="icon" aria-hidden="true" />
                                <div>
                                    <strong>{file.name}</strong>
                                    <span className="muted small">
                                        {number(file.size / 1024, 1)} KiB
                                    </span>
                                </div>
                                <button
                                    type="button"
                                    className="icon-button"
                                    aria-label="Bỏ file đã chọn"
                                    title="Bỏ file đã chọn"
                                    onClick={clearFile}
                                >
                                    <X className="icon" aria-hidden="true" />
                                </button>
                            </div>
                        )}
                    </div>
                    <fieldset className="mode-fieldset">
                        <legend>Chế độ dự đoán</legend>
                        <div className="radio-row">
                            {[
                                [
                                    "batch",
                                    "Theo lô · Batch",
                                    "Dự đoán toàn bộ file. Không có tạm dừng hoặc dừng Batch.",
                                ],
                                [
                                    "replay",
                                    "Phát lại · Replay",
                                    "Suy luận từng dòng CSV; có tạm dừng, tiếp tục và dừng.",
                                ],
                            ].map(([value, title, description]) => (
                                <label className="radio-option" key={value}>
                                    <span className="mode-title">
                                        <input
                                            type="radio"
                                            name="mode"
                                            value={value}
                                            checked={mode === value}
                                            onChange={() => setMode(value)}
                                        />
                                        <strong>{title}</strong>
                                        {mode === value && (
                                            <Check
                                                className="icon mode-check"
                                                aria-hidden="true"
                                            />
                                        )}
                                    </span>
                                    <p>{description}</p>
                                </label>
                            ))}
                        </div>
                    </fieldset>
                    {mode === "replay" && (
                        <label className="field replay-interval">
                            <span>Nhịp phát lại (giây)</span>
                            <input
                                id="interval"
                                type="number"
                                min="0.05"
                                max="60"
                                step="0.05"
                                value={interval}
                                onChange={(event) =>
                                    setInterval(event.target.value)
                                }
                                required
                            />
                            <small>
                                0,05–60 giây; thời gian thực tế phụ thuộc
                                server.
                            </small>
                        </label>
                    )}
                    <div id="upload-error" hidden={!action.error}>
                        <ErrorNotice error={action.error} />
                    </div>
                    <div className="actions">
                        <button
                            className="primary"
                            id="create-submit"
                            type="submit"
                            disabled={action.pending}
                        >
                            {action.pending
                                ? "Đang kiểm tra CSV…"
                                : "Bắt đầu dự đoán"}
                            <ArrowRight className="icon" aria-hidden="true" />
                        </button>
                    </div>
                    <p className="scope-note">
                        Phát lại từ CSV là mô phỏng. Chỉ gọi SHAP/Gemini sau khi
                        bạn chọn dòng và gửi yêu cầu.
                    </p>
                </form>
                <section className="panel upload-contract">
                    <h2>Đầu vào</h2>
                    <p className="muted">
                        Đủ tên đặc trưng; thứ tự được server sắp theo model.
                        Không đưa nhãn thật vào đầu vào model hoặc prompt.
                    </p>
                    <ErrorNotice
                        error={ui.metadata.error}
                        retry={ui.metadata.refresh}
                    />
                    {metadata ? (
                        <>
                            <details className="schema-details">
                                <summary>
                                    {metadata.schema.feature_names.length} đặc
                                    trưng theo thứ tự model
                                </summary>
                                <ol className="schema-list mono">
                                    {metadata.schema.feature_names.map(
                                        (name) => (
                                            <li key={name}>{name}</li>
                                        ),
                                    )}
                                </ol>
                            </details>
                            <h3>Tám lớp đầu ra</h3>
                            <div className="class-badges">
                                {CLASS_NAMES.map((name) => (
                                    <ClassBadge key={name} name={name} />
                                ))}
                            </div>
                        </>
                    ) : (
                        <Loading />
                    )}
                    <DownloadButton
                        path="/api/input-template"
                        name="input_template.csv"
                    >
                        CSV mẫu
                    </DownloadButton>
                </section>
            </div>
        </>
    );
}
