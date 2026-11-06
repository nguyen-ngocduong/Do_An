"use client";
import Link from "next/link";
import { useCallback, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
    ArrowUpRight,
    ChartColumn,
    ListChecks,
    FileSpreadsheet,
    ListFilter,
    Plus,
    RefreshCw,
    ShieldAlert,
    TriangleAlert,
} from "lucide-react";
import { getDashboard } from "@/lib/api/dashboard";
import { query } from "@/lib/api/client";
import { usePolling } from "@/lib/use-polling";
import { number, percent, rowName } from "@/lib/format";
import type {
    DashboardPeriod,
    DashboardRunOption,
    DashboardSummary,
} from "@/types/dashboard";
import {
    Badge,
    ClassBadge,
    Empty,
    ErrorNotice,
    Loading,
    PageHeading,
} from "@/components/shared/controls";
import { ActivityChart, ClassDistribution, dayLabel } from "./charts";
import { DashboardPipeline } from "./dashboard-pipeline";
import type { RunInfo } from "@/types/run";

const PERIODS: { value: DashboardPeriod; label: string }[] = [
    { value: "today", label: "Hôm nay" },
    { value: "7d", label: "7 ngày gần nhất" },
    { value: "30d", label: "30 ngày gần nhất" },
    { value: "all", label: "Toàn bộ lịch sử" },
];
function timestamp(value: string) {
    return new Date(value).toLocaleString("vi-VN", {
        timeZone: "Asia/Ho_Chi_Minh",
    });
}

export function Dashboard() {
    const params = useSearchParams();
    const period =
        PERIODS.find((item) => item.value === params.get("period"))?.value ??
        "7d";
    const runId = params.get("run_id") || "";
    const load = useCallback(
        (signal: AbortSignal) => getDashboard(period, runId, signal),
        [period, runId],
    );
    const poll = usePolling(`dashboard:${period}:${runId}`, load, 15000);
    const data = poll.data;
    const options = [...(data?.run_options || [])];
    if (runId && !options.some((run) => run.id === runId))
        options.unshift(
            data?.selected_run || {
                id: runId,
                filename: "Lần chạy đang chọn",
                created_at: "",
            },
        );
    return (
        <div className="nid-dashboard">
            <PageHeading
                title="Tổng quan giám sát an ninh"
                description="Theo dõi dữ liệu mạng IoT đã xử lý, dự đoán AI, cảnh báo và bằng chứng SHAP."
                actions={
                    <Link className="button primary" href="/runs/new">
                        <Plus className="icon" aria-hidden="true" />
                        Tạo lần chạy
                    </Link>
                }
            />
            <div className="panel dashboard-toolbar">
                <DashboardFilters
                    key={`${period}:${runId}`}
                    period={period}
                    runId={runId}
                    options={options}
                    limited={(data?.available_run_count || 0) > 100}
                />
                <div className="dashboard-update">
                    <div>
                        <button
                            className="text-button"
                            id="dashboard-refresh"
                            onClick={poll.refresh}
                        >
                            <RefreshCw className="icon" aria-hidden="true" />
                            Làm mới
                        </button>
                        {data && (
                            <time dateTime={data.generated_at}>
                                {timestamp(data.generated_at)}
                            </time>
                        )}
                    </div>
                    <span>Tự làm mới 15 giây · UTC+7</span>
                </div>
            </div>
            <p className="dashboard-scope">
                {data &&
                    `${number(data.metrics.run_count)} lần chạy có hoạt động · `}
                Theo thời gian xử lý mẫu UTC+7; trạng thái hiện tại của nhóm mẫu
                đã chọn.
            </p>
            <ErrorNotice error={poll.error} retry={poll.refresh} />
            {!data ? (
                !poll.error && <Loading />
            ) : (
                <>
                    <DashboardMetrics data={data} />
                    {data.metrics.predicted_rows === 0 && (
                        <Empty
                            title="Chưa có mẫu trong khoảng đã chọn"
                            description="Tải CSV mới hoặc đổi thời gian/lần chạy để xem dữ liệu đã lưu."
                        >
                            <Link className="button" href="/runs/new">
                                Tải CSV
                            </Link>
                        </Empty>
                    )}
                    <div className="dashboard-charts">
                        <section
                            className="panel dashboard-chart-card"
                            aria-labelledby="dashboard-activity-title"
                        >
                            <div className="dashboard-card-heading">
                                <div>
                                    <h2 id="dashboard-activity-title">
                                        Số mẫu đã xử lý
                                    </h2>
                                    <p>Theo phạm vi bộ lọc đang chọn</p>
                                </div>
                            </div>
                            <ActivityChart
                                days={data.daily_activity}
                                classCounts={data.class_counts}
                                dateRange={`${dayLabel(data.trend_start_date)} – ${dayLabel(data.trend_end_date)}${period === "all" ? " · 30 ngày gần nhất" : ""}`}
                            />
                        </section>
                        <section
                            className="panel dashboard-chart-card"
                            aria-labelledby="dashboard-classes-title"
                        >
                            <div className="dashboard-card-heading">
                                <div>
                                    <h2 id="dashboard-classes-title">
                                        Phân bố nhãn dự đoán
                                    </h2>
                                    <p>
                                        Tám lớp mô hình · Tổng cộng{" "}
                                        {number(data.metrics.predicted_rows)}{" "}
                                        mẫu
                                    </p>
                                </div>
                            </div>
                            <ClassDistribution counts={data.class_counts} />
                            <p className="dashboard-distribution-note">
                                Phân bố nhãn do mô hình dự đoán; chưa xác nhận
                                tấn công thực tế.
                            </p>
                        </section>
                    </div>
                    <div className="dashboard-recent">
                        <section
                            className="panel dashboard-table-panel"
                            aria-labelledby="dashboard-alerts-title"
                        >
                            <div className="dashboard-card-heading">
                                <h2 id="dashboard-alerts-title">
                                    Cảnh báo gần nhất
                                </h2>
                                <Link
                                    href={`/alerts?${query({ run_id: runId })}`}
                                >
                                    Trung tâm cảnh báo{" "}
                                    <ArrowUpRight
                                        className="icon"
                                        aria-hidden="true"
                                    />
                                </Link>
                            </div>
                            {data.recent_alerts.length ? (
                                <div className="table-wrap">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Mẫu</th>
                                                <th>Dự đoán</th>
                                                <th>Tiếp nhận</th>
                                                <th>Xem</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {data.recent_alerts.map((alert) => (
                                                <tr key={alert.id}>
                                                    <td
                                                        className="mono"
                                                        title={alert.filename}
                                                    >
                                                        {rowName(
                                                            alert.row_index,
                                                        )}
                                                    </td>
                                                    <td>
                                                        <ClassBadge
                                                            name={
                                                                alert.predicted_class
                                                            }
                                                            probability={
                                                                alert.predicted_probability
                                                            }
                                                        />
                                                    </td>
                                                    <td>
                                                        <Badge
                                                            status={
                                                                alert.status
                                                            }
                                                        />
                                                    </td>
                                                    <td>
                                                        <Link
                                                            aria-label={`Mở cảnh báo ${rowName(alert.row_index)} của ${alert.filename}`}
                                                            href={`/alerts?${query({ alert: alert.id, run_id: alert.run_id })}`}
                                                        >
                                                            Mở
                                                        </Link>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            ) : (
                                <p className="dashboard-empty">
                                    Chưa có cảnh báo trong nhóm mẫu đã chọn.
                                </p>
                            )}
                        </section>
                        <section
                            className="panel dashboard-table-panel"
                            aria-labelledby="dashboard-runs-title"
                        >
                            <div className="dashboard-card-heading">
                                <h2 id="dashboard-runs-title">
                                    Lần chạy gần nhất
                                </h2>
                                <Link href="/runs">
                                    Lịch sử{" "}
                                    <ArrowUpRight
                                        className="icon"
                                        aria-hidden="true"
                                    />
                                </Link>
                            </div>
                            {data.recent_runs.length ? (
                                <div className="table-wrap">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>File CSV</th>
                                                <th>Tiến độ</th>
                                                <th>Trạng thái</th>
                                                <th>Xem</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {data.recent_runs.map((run) => (
                                                <tr key={run.id}>
                                                    <td className="wrap">
                                                        <div className="dashboard-run-file">
                                                            <FileSpreadsheet
                                                                className="icon"
                                                                aria-hidden="true"
                                                            />
                                                            <div>
                                                                <strong>
                                                                    {
                                                                        run.filename
                                                                    }
                                                                </strong>
                                                                <small className="muted dashboard-run-date">
                                                                    {run.mode ===
                                                                    "batch"
                                                                        ? "Batch"
                                                                        : "Replay"}{" "}
                                                                    · Tạo{" "}
                                                                    {timestamp(
                                                                        run.created_at,
                                                                    )}
                                                                </small>
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td className="mono">
                                                        {number(
                                                            run.processed_rows,
                                                        )}{" "}
                                                        /{" "}
                                                        {number(run.total_rows)}
                                                        <div
                                                            className="meter dashboard-run-progress"
                                                            aria-label={`Tiến độ ${run.processed_rows} trên ${run.total_rows} dòng`}
                                                        >
                                                            <span
                                                                style={{
                                                                    width: `${run.total_rows ? Math.min(100, (100 * run.processed_rows) / run.total_rows) : 0}%`,
                                                                }}
                                                            />
                                                        </div>
                                                    </td>
                                                    <td>
                                                        <Badge
                                                            status={run.status}
                                                        />
                                                    </td>
                                                    <td>
                                                        <Link
                                                            href={`/runs/${run.id}/monitor`}
                                                            aria-label={`Mở lần chạy ${run.filename}`}
                                                        >
                                                            Mở
                                                        </Link>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            ) : (
                                <p className="dashboard-empty">
                                    Chưa có lần chạy phù hợp bộ lọc.
                                </p>
                            )}
                            {data.recent_runs.length === 1 && (
                                <LatestRunSummary run={data.recent_runs[0]} />
                            )}
                        </section>
                    </div>
                    <DashboardPipeline data={data} />
                </>
            )}
        </div>
    );
}

function LatestRunSummary({ run }: { run: RunInfo }) {
    return (
        <div className="latest-run-summary">
            <h3>Thông tin toàn bộ lần chạy</h3>
            <dl>
                <div>
                    <dt>Số dòng CSV</dt>
                    <dd>{number(run.total_rows)}</dd>
                </div>
                <div>
                    <dt>Đã dự đoán</dt>
                    <dd>{number(run.processed_rows)}</dd>
                </div>
                <div>
                    <dt>Chưa xử lý</dt>
                    <dd>
                        {number(
                            Math.max(0, run.total_rows - run.processed_rows),
                        )}
                    </dd>
                </div>
                <div>
                    <dt>Chế độ</dt>
                    <dd>{run.mode === "batch" ? "Batch" : "Replay"}</dd>
                </div>
            </dl>
            <p>Cập nhật lần cuối {timestamp(run.updated_at)}</p>
        </div>
    );
}

function DashboardFilters({
    period,
    runId,
    options,
    limited,
}: {
    period: DashboardPeriod;
    runId: string;
    options: DashboardRunOption[];
    limited: boolean;
}) {
    const router = useRouter();
    const [selectedPeriod, setPeriod] = useState(period);
    const [selectedRun, setRun] = useState(runId);
    return (
        <form
            id="dashboard-filters"
            className="dashboard-filters"
            onSubmit={(event) => {
                event.preventDefault();
                router.replace(
                    `/dashboard?${query({ period: selectedPeriod, run_id: selectedRun })}`,
                    { scroll: false },
                );
            }}
        >
            <label>
                Khoảng thời gian
                <select
                    name="period"
                    value={selectedPeriod}
                    onChange={(event) =>
                        setPeriod(event.target.value as DashboardPeriod)
                    }
                >
                    {PERIODS.map((option) => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    ))}
                </select>
            </label>
            <label>
                Lần chạy
                <select
                    name="run_id"
                    value={selectedRun}
                    onChange={(event) => setRun(event.target.value)}
                >
                    <option value="">Tất cả lần chạy</option>
                    {options.map((run) => (
                        <option key={run.id} value={run.id}>
                            {run.filename}
                            {run.created_at
                                ? ` · ${timestamp(run.created_at)}`
                                : ""}
                        </option>
                    ))}
                </select>
                {limited && (
                    <small className="muted">
                        Hiện 100 lần chạy gần nhất và lần chạy đang chọn.
                    </small>
                )}
            </label>
            <button className="primary" type="submit">
                <ListFilter className="icon" aria-hidden="true" />
                Áp dụng
            </button>
        </form>
    );
}

function DashboardMetrics({ data }: { data: DashboardSummary }) {
    const metrics = data.metrics;
    const items = [
        {
            label: "Mẫu đã dự đoán",
            value: metrics.predicted_rows,
            detail: `${number(metrics.normal_rows)} mẫu Normal`,
            unit: "mẫu mạng",
            icon: ListChecks,
            tone: "accent",
        },
        {
            label: "Mẫu nghi vấn",
            value: metrics.suspected_rows,
            detail:
                metrics.suspected_percentage === null
                    ? "Chưa có mẫu để tính tỷ lệ"
                    : `${number(metrics.suspected_percentage, 1)}% số mẫu · khác Normal`,
            icon: TriangleAlert,
            unit: "khác Normal",
            tone: "warning",
        },
        {
            label: "Cảnh báo chờ tiếp nhận",
            value: metrics.pending_alerts,
            detail: `${number(data.alert_counts.acknowledged)} đã tiếp nhận · ${number(data.alert_counts.closed)} đã đóng`,
            icon: ShieldAlert,
            unit: "cần tiếp nhận",
            tone: "danger",
        },
        {
            label: "Mẫu đã có SHAP",
            value: metrics.shap_rows,
            detail: metrics.predicted_rows
                ? `${percent(metrics.shap_rows / metrics.predicted_rows, 1)} số mẫu có bằng chứng`
                : "Bằng chứng đã lưu",
            icon: ChartColumn,
            unit: "có bằng chứng",
            tone: "success",
        },
    ];
    return (
        <dl id="dashboard-metrics" className="monitor-stats dashboard-metrics">
            {items.map((item) => (
                <div
                    className="monitor-stat"
                    data-tone={item.tone}
                    key={item.label}
                >
                    <dt className="monitor-stat-heading">
                        {item.label}
                        <span className="dashboard-metric-icon">
                            <item.icon className="icon" aria-hidden="true" />
                        </span>
                    </dt>
                    <div className="dashboard-metric-value">
                        <dd>{number(item.value)}</dd>
                        <span>{item.unit}</span>
                    </div>
                    <small>{item.detail}</small>
                </div>
            ))}
        </dl>
    );
}
