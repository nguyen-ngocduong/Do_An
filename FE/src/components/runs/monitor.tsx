"use client";
import Link from "next/link";
import { useCallback, useState } from "react";
import {
    ArrowUpRight,
    FileSpreadsheet,
    ListChecks,
    MessageSquareText,
    ShieldCheck,
    TriangleAlert,
} from "lucide-react";
import { controlRun, getRun, getSummary } from "@/lib/api/runs";
import { getPredictions } from "@/lib/api/predictions";
import { usePolling } from "@/lib/use-polling";
import { useAction } from "@/lib/use-action";
import { CLASS_NAMES } from "@/types/model";
import { number, percent, rowName } from "@/lib/format";
import {
    Badge,
    ConfirmDialog,
    ErrorNotice,
    InfoPopover,
    Loading,
    PageHeading,
    RunTabs,
} from "@/components/shared/controls";
export function RunMonitor({ id }: { id: string }) {
    const load = useCallback(
        async (signal: AbortSignal) => {
            const [run, summary] = await Promise.all([
                getRun(id, signal),
                getSummary(id, signal),
            ]);
            const recent = await getPredictions(
                id,
                { offset: Math.max(0, run.processed_rows - 5), limit: 5 },
                signal,
            );
            return { run, summary, recent };
        },
        [id],
    );
    const poll = usePolling(`monitor:${id}`, load);
    const action = useAction();
    const [confirm, setConfirm] = useState(false);
    const control = (command: "pause" | "resume" | "stop") =>
        action.run(() => controlRun(id, command), poll.refresh);
    const value = poll.data;
    const progress =
        value && value.run.total_rows > 0
            ? value.run.processed_rows / value.run.total_rows
            : 0;
    const metrics = value ? [
        {
            title: "Đã dự đoán",
            count: value.run.processed_rows,
            description: `Trên ${number(value.run.total_rows)} dòng CSV`,
            icon: ListChecks,
            tone: "accent",
        },
        {
            title: "Normal",
            count: value.summary.normal_rows,
            description: "Nhãn mô hình dự đoán",
            icon: ShieldCheck,
            tone: "success",
        },
        {
            title: "Nhãn khác Normal",
            count: value.summary.suspected_attack_rows,
            description: "Cần kiểm tra thêm",
            icon: TriangleAlert,
            tone: "warning",
        },
        {
            title: "Chưa yêu cầu giải thích",
            count: value.summary.explanation_counts.not_requested ?? 0,
            description: "Mức Kỹ thuật",
            icon: MessageSquareText,
            tone: "neutral",
        },
    ] : [];
    return (
        <>
            <PageHeading
                title="Theo dõi lần chạy"
                info="Dự đoán và giải thích có trạng thái riêng; số liệu được đọc trực tiếp từ server theo thời gian thực."
            />
            <RunTabs id={id} selected="monitor" />
            <ErrorNotice
                error={action.error || poll.error}
                retry={poll.refresh}
            />
            {!value ? (
                <Loading />
            ) : (
                <div className="run-monitor">
                    <section
                        id="run-overview"
                        className="panel monitor-overview"
                        data-status={value.run.status}
                        aria-label="Thông tin và tiến độ lần chạy"
                    >
                        <div className="monitor-run-header">
                            <div className="monitor-file">
                                <FileSpreadsheet
                                    className="monitor-file-icon"
                                    aria-hidden="true"
                                />
                                <div>
                                    <strong className="break-word">
                                        {value.run.filename}
                                    </strong>
                                    <div className="monitor-id-wrap">
                                        <span className="mono small muted" title={id}>
                                            ID: {id.slice(0, 10)}…{id.slice(-6)}
                                        </span>
                                        <InfoPopover
                                            title="ID lần chạy"
                                            description={`ID của file CSV đưa vào xử lý: ${id}`}
                                        />
                                    </div>
                                </div>
                            </div>
                            <div className="actions">
                                <Badge status={value.run.status} />
                                <span>
                                    {value.run.mode === "replay"
                                        ? `Replay · ${number(value.run.interval_seconds, 2)} s / nhịp`
                                        : "Batch · Theo lô"}
                                </span>
                                {value.run.mode === "replay" &&
                                    ["queued", "running"].includes(
                                        value.run.status,
                                    ) && (
                                        <button
                                            data-control="pause"
                                            disabled={action.pending}
                                            onClick={() => control("pause")}
                                        >
                                            Tạm dừng
                                        </button>
                                    )}
                                {[
                                    "paused",
                                    "stopped",
                                    "interrupted",
                                    "failed",
                                ].includes(value.run.status) && (
                                    <button
                                        data-control="resume"
                                        disabled={action.pending}
                                        onClick={() => control("resume")}
                                    >
                                        Tiếp tục
                                    </button>
                                )}
                                {value.run.mode === "replay" &&
                                    ["queued", "running", "paused"].includes(
                                        value.run.status,
                                    ) && (
                                        <button
                                            className="danger-button"
                                            data-control="stop"
                                            disabled={action.pending}
                                            onClick={() => setConfirm(true)}
                                        >
                                            Dừng phát lại
                                        </button>
                                    )}
                            </div>
                        </div>
                        <div className="monitor-progress">
                            <div className="monitor-progress-label">
                                <span>
                                    {number(value.run.processed_rows)} /{" "}
                                    {number(value.run.total_rows)} dòng đã dự đoán
                                </span>
                                <strong className="mono">
                                    {percent(progress, 1)}
                                </strong>
                            </div>
                            <progress
                                aria-label="Tiến độ dự đoán"
                                value={value.run.processed_rows}
                                max={Math.max(1, value.run.total_rows)}
                            />
                        </div>
                        {value.run.message && (
                            <div className="notice">{value.run.message}</div>
                        )}
                    </section>
                    <div
                        className="monitor-stats"
                        aria-label="Thống kê lần chạy"
                    >
                        {metrics.map(
                            ({ title, count, description, icon: Icon, tone }) => (
                                <div
                                    className="monitor-stat"
                                    data-tone={tone}
                                    key={title}
                                >
                                    <div className="monitor-stat-heading">
                                        <div className="monitor-stat-title-wrap">
                                            <span>{title}</span>
                                            <InfoPopover
                                                title={title}
                                                description={description}
                                            />
                                        </div>
                                        <Icon className="icon" aria-hidden="true" />
                                    </div>
                                    <strong className="mono">
                                        {number(count)}
                                    </strong>
                                </div>
                            ),
                        )}
                    </div>
                    <div className="monitor-panels">
                        <section
                            className="panel monitor-distribution"
                            aria-labelledby="distribution-title"
                        >
                            <div className="monitor-card-heading">
                                <div className="dashboard-heading-title-wrap">
                                    <h2 id="distribution-title">
                                        Phân bố nhãn dự đoán
                                    </h2>
                                    <InfoPopover
                                        title="Phân bố nhãn dự đoán"
                                        description="Số dòng theo tám lớp đầu ra của mô hình. Nhãn khác Normal tạo cảnh báo theo model; cần kiểm tra thêm để xác nhận sự kiện thực tế."
                                    />
                                </div>
                            </div>
                            <ul className="monitor-class-list">
                                {CLASS_NAMES.map((name) => {
                                    const count = value.summary.class_counts[name];
                                    const share =
                                        value.summary.processed_rows > 0
                                            ? count / value.summary.processed_rows
                                             : 0;
                                    return (
                                        <li key={name} className="monitor-class-row">
                                            <span className="monitor-class-name">
                                                <span
                                                    className="class-dot"
                                                    data-class={name}
                                                    aria-hidden="true"
                                                />
                                                {name}
                                            </span>
                                            <div className="meter" aria-hidden="true">
                                                <span
                                                    style={{ width: `${share * 100}%` }}
                                                />
                                            </div>
                                            <strong className="mono">
                                                {number(count)}
                                            </strong>
                                            <span className="mono muted">
                                                {percent(share, 1)}
                                            </span>
                                        </li>
                                    );
                                })}
                            </ul>
                        </section>
                        <section
                            className="panel monitor-recent"
                            aria-labelledby="recent-title"
                        >
                            <div className="monitor-card-heading">
                                <div className="dashboard-heading-title-wrap">
                                    <h2 id="recent-title">Kết quả mới nhất</h2>
                                    <InfoPopover
                                        title="Kết quả mới nhất"
                                        description="Tối đa năm dòng vừa được dự đoán gần nhất."
                                    />
                                </div>
                                <Link
                                    className="monitor-table-link"
                                    href={`/runs/${id}/predictions`}
                                >
                                    Xem bảng dự đoán
                                    <ArrowUpRight
                                        className="icon"
                                        aria-hidden="true"
                                    />
                                </Link>
                            </div>
                            <div className="table-wrap">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Dòng CSV</th>
                                            <th>Nhãn dự đoán</th>
                                            <th>Xác suất</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {value.recent.items.length === 0 && (
                                            <tr>
                                                <td colSpan={3} className="monitor-empty">
                                                    Chưa có kết quả. Các dòng sẽ xuất
                                                    hiện sau khi được dự đoán.
                                                </td>
                                            </tr>
                                        )}
                                        {value.recent.items.map((item) => (
                                            <tr key={item.row_index}>
                                                <td>
                                                    <Link
                                                        href={`/runs/${id}/rows/${item.row_index}`}
                                                    >
                                                        {rowName(
                                                            item.row_index,
                                                        )}
                                                    </Link>
                                                </td>
                                                <td>{item.predicted_class}</td>
                                                <td className="mono">
                                                    {percent(
                                                        item.predicted_probability,
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </section>
                    </div>
                </div>
            )}
            {confirm && (
                <ConfirmDialog
                    title="Dừng phát lại?"
                    text="Giữ các kết quả đã xử lý. Dòng đang suy luận có thể hoàn tất trước khi dừng."
                    accept="Dừng phát lại"
                    onCancel={() => setConfirm(false)}
                    onConfirm={() => {
                        setConfirm(false);
                        void control("stop");
                    }}
                />
            )}
        </>
    );
}
