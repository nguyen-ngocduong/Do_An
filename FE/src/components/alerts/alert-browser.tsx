"use client";
import Link from "next/link";
import {
    ArrowUpRight,
    Bell,
    CheckCheck,
    CheckCircle2,
    ChevronRight,
    CircleAlert,
    ClipboardPenLine,
    Info,
    ListFilter,
    Save,
    Search,
    Sparkles,
    X,
} from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useState } from "react";
import {
    getAlert,
    getAlertOverview,
    listAlerts,
    updateAlert,
} from "@/lib/api/alerts";
import { query } from "@/lib/api/client";
import { usePolling } from "@/lib/use-polling";
import { useAction } from "@/lib/use-action";
import { audienceValue, pageOffset } from "@/lib/navigation";
import { number, percent, rowName, time } from "@/lib/format";
import { useUi } from "@/store/ui-store";
import type { Audience } from "@/types/model";
import type { AlertDetail, AlertStatus } from "@/types/alert";
import {
    Badge,
    ClassOptions,
    ClassBadge,
    ConfirmDialog,
    Empty,
    ErrorNotice,
    Loading,
    PageHeading,
    Pagination,
} from "@/components/shared/controls";
import { PlaybookView } from "@/components/explanations/evidence";

export function AlertBrowser() {
    const params = useSearchParams();
    const router = useRouter();
    const runId = params.get("run_id") || "";
    const status = params.get("status") || "";
    const className = params.get("class") || "";
    const audience = audienceValue(params.get("audience"));
    const offset = pageOffset(params.get("offset"));
    const [dirty, setDirty] = useState(false);
    const load = useCallback(
        (signal: AbortSignal) =>
            listAlerts(
                {
                    run_id: runId,
                    status,
                    predicted_class: className,
                    audience_level: audience,
                    offset,
                },
                signal,
            ),
        [runId, status, className, audience, offset],
    );
    const list = usePolling(
        `alerts:${runId}:${status}:${className}:${audience}:${offset}`,
        load,
    );
    const loadOverview = useCallback(
        (signal: AbortSignal) => getAlertOverview(runId, className, signal),
        [runId, className],
    );
    const overview = usePolling(
        `alert-overview:${runId}:${className}`,
        loadOverview,
        15000,
    );
    const metrics = [
        {
            label: "Tổng cảnh báo",
            value: overview.data?.total,
            icon: Bell,
            tone: "primary",
        },
        {
            label: "Chờ tiếp nhận",
            value: overview.data?.new_count,
            icon: CircleAlert,
            tone: "warning",
        },
        {
            label: "Đã tiếp nhận",
            value: overview.data?.acknowledged_count,
            icon: ClipboardPenLine,
            tone: "primary",
        },
        {
            label: "Đã đóng",
            value: overview.data?.closed_count,
            icon: CheckCheck,
            tone: "success",
        },
    ];
    const selectedId =
        params.get("alert") === "closed"
            ? 0
            : pageOffset(params.get("alert")) || list.data?.items[0]?.id || 0;
    const loadDetail = useCallback(
        (signal: AbortSignal) =>
            selectedId
                ? getAlert(selectedId, audience, signal)
                : Promise.resolve(null),
        [selectedId, audience],
    );
    const detail = usePolling(`alert:${selectedId}:${audience}`, loadDetail);
    function change(values: Record<string, string | number>) {
        if (
            dirty &&
            !window.confirm("Ghi chú chưa lưu. Bỏ thay đổi để chuyển nội dung?")
        )
            return;
        setDirty(false);
        const next = new URLSearchParams(params);
        for (const [key, value] of Object.entries(values)) {
            if (value === "") next.delete(key);
            else next.set(key, String(value));
        }
        router.replace(`/alerts?${next}`, { scroll: false });
    }
    return (
        <div className="alert-page">
            <PageHeading
                title="Trung tâm cảnh báo"
                description="Các nhãn khác Normal do mô hình dự đoán; cần người vận hành kiểm tra thêm."
            />
            <dl
                id="alert-overview"
                className="alert-overview"
                aria-label="Thống kê cảnh báo"
            >
                {metrics.map((metric) => (
                    <div key={metric.label} data-tone={metric.tone}>
                        <dt>
                            {metric.label}
                            <metric.icon className="icon" aria-hidden="true" />
                        </dt>
                        <dd>{number(metric.value)}</dd>
                    </div>
                ))}
            </dl>
            <p className="alert-overview-scope">
                Thống kê theo lớp và lần chạy đã chọn, gồm mọi trạng thái tiếp
                nhận.
            </p>
            <form
                key={`${runId}:${status}:${className}:${audience}`}
                id="alert-filters"
                className="filters alert-filters"
                onSubmit={(event) => {
                    event.preventDefault();
                    const form = new FormData(event.currentTarget);
                    change({
                        run_id: String(form.get("run_id")).trim(),
                        status: String(form.get("status")),
                        class: String(form.get("class")),
                        audience: String(form.get("audience")),
                        offset: 0,
                        alert: "",
                    });
                }}
            >
                <label>
                    Trạng thái tiếp nhận
                    <select name="status" defaultValue={status}>
                        <option value="">Tất cả trạng thái</option>
                        <option value="new">Mới</option>
                        <option value="acknowledged">Đã tiếp nhận</option>
                        <option value="closed">Đã đóng</option>
                    </select>
                </label>
                <label>
                    Lớp dự đoán
                    <select name="class" defaultValue={className}>
                        <ClassOptions />
                    </select>
                </label>
                <label>
                    Mức diễn giải
                    <select name="audience" defaultValue={audience}>
                        <option value="technical">Kỹ thuật</option>
                        <option value="basic">Dễ hiểu</option>
                    </select>
                </label>
                <label className="field-wide">
                    ID lần chạy (tùy chọn)
                    <span className="search-field">
                        <Search className="icon" aria-hidden="true" />
                        <input
                            name="run_id"
                            defaultValue={runId}
                            pattern="[a-f0-9]{32}"
                            placeholder="Tất cả lần chạy"
                            spellCheck={false}
                        />
                    </span>
                </label>
                <button type="submit" className="accent-button">
                    <ListFilter className="icon" aria-hidden="true" />
                    Lọc
                </button>
            </form>
            <ErrorNotice
                error={list.error || overview.error}
                retry={() => {
                    list.refresh();
                    overview.refresh();
                }}
            />
            <div
                className={`alert-workspace ${selectedId ? "with-detail" : ""}`}
            >
                <section id="alert-list" className="alert-list-panel">
                    {!list.data ? (
                        <Loading />
                    ) : !list.data.items.length ? (
                        <Empty
                            title="Chưa có cảnh báo phù hợp"
                            description="Thử đổi bộ lọc hoặc tạo lần chạy mới. Nhãn Normal không tạo cảnh báo."
                        />
                    ) : (
                        <>
                            <div className="alert-list-heading">
                                <h2>
                                    Danh sách cảnh báo{" "}
                                    <span className="badge accent">
                                        {number(list.data.total)}
                                    </span>
                                </h2>
                                <span className="small muted">Theo bộ lọc</span>
                            </div>
                            <div className="table-wrap">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Mã mẫu</th>
                                            <th>Dự đoán</th>
                                            <th>Tiếp nhận</th>
                                            <th className="alert-action-heading">
                                                Thao tác
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {list.data.items.map((item) => (
                                            <tr
                                                key={item.id}
                                                className={
                                                    item.id === selectedId
                                                        ? "selected"
                                                        : ""
                                                }
                                            >
                                                <td>
                                                    <strong className="mono">
                                                        {rowName(
                                                            item.row_index,
                                                        )}
                                                    </strong>
                                                </td>
                                                <td>
                                                    <ClassBadge
                                                        name={
                                                            item.predicted_class
                                                        }
                                                        probability={
                                                            item.predicted_probability
                                                        }
                                                    />
                                                </td>
                                                <td>
                                                    <Badge
                                                        status={item.status}
                                                    />
                                                </td>
                                                <td>
                                                    <button
                                                        className="text-button"
                                                        data-alert={item.id}
                                                        aria-pressed={
                                                            item.id ===
                                                            selectedId
                                                        }
                                                        aria-controls="alert-detail"
                                                        aria-label={`Xem cảnh báo dòng ${rowName(item.row_index)}, mã cảnh báo ${item.id}`}
                                                        onClick={() =>
                                                            change({
                                                                alert: item.id,
                                                            })
                                                        }
                                                    >
                                                        {item.id === selectedId
                                                            ? "Đang xem"
                                                            : "Mở"}
                                                        <ChevronRight
                                                            className="icon"
                                                            aria-hidden="true"
                                                        />
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </>
                    )}
                    <Pagination
                        total={list.data?.total || 0}
                        offset={offset}
                        onChange={(offset) => change({ offset, alert: "" })}
                    />
                </section>
                <section
                    id="alert-detail"
                    className="panel alert-detail-panel"
                    hidden={!selectedId}
                    aria-label="Chi tiết cảnh báo"
                >
                    <ErrorNotice error={detail.error} retry={detail.refresh} />
                    {!selectedId ? (
                        <Empty
                            title="Chọn một cảnh báo"
                            description="Xem bằng chứng, ghi chú và lịch sử xử lý ở đây."
                        />
                    ) : !detail.data ? (
                        <Loading />
                    ) : (
                        <AlertEditor
                            key={`${selectedId}:${audience}`}
                            detail={detail.data}
                            audience={audience}
                            returnUrl={`/alerts?${params}`}
                            onClose={() => change({ alert: "closed" })}
                            onDirty={setDirty}
                            onSaved={() => {
                                list.refresh();
                                detail.refresh();
                                overview.refresh();
                            }}
                        />
                    )}
                </section>
            </div>
        </div>
    );
}
function AlertEditor({
    detail,
    audience,
    returnUrl,
    onDirty,
    onSaved,
    onClose,
}: {
    detail: AlertDetail;
    audience: Audience;
    returnUrl: string;
    onClose: () => void;
    onDirty: (value: boolean) => void;
    onSaved: () => void;
}) {
    const [note, setNote] = useState(detail.note);
    const [closing, setClosing] = useState(false);
    const action = useAction();
    const ui = useUi();
    function save(status: AlertStatus) {
        if (status === "closed" && !note.trim()) {
            ui.notify(
                "Ghi lý do đóng trong ô ghi chú trước khi đóng cảnh báo.",
            );
            return;
        }
        action.run(
            () => updateAlert(detail.id, audience, status, note),
            () => {
                onDirty(false);
                onSaved();
                ui.notify("Đã lưu trạng thái và ghi chú cảnh báo.");
            },
        );
    }
    return (
        <>
            <div className="alert-detail-heading">
                <div>
                    <h2>
                        Chi tiết cảnh báo{" "}
                        <span className="mono">
                            {rowName(detail.row_index)}
                        </span>
                    </h2>
                    <Badge status={detail.status} />
                </div>
                <button
                    className="icon-button"
                    id="close-alert"
                    aria-label="Đóng chi tiết cảnh báo"
                    title="Đóng chi tiết cảnh báo"
                    onClick={onClose}
                >
                    <X className="icon" aria-hidden="true" />
                </button>
            </div>
            <div className="alert-detail-body">
                <div
                    className="alert-prediction"
                    data-class={detail.predicted_class}
                >
                    <div className="alert-prediction-row">
                        <span className="alert-sample-label">
                            <CircleAlert className="icon" aria-hidden="true" />
                            <small>Dòng {rowName(detail.row_index)}</small>
                        </span>
                        {ui.metadata.data?.model.model_id && (
                            <span className="alert-model">
                                {ui.metadata.data.model.model_id}
                            </span>
                        )}
                    </div>
                    <div className="alert-prediction-main">
                        <h3>{detail.predicted_class}</h3>
                        <div className="alert-output-probability">
                            <strong className="mono">
                                {percent(detail.predicted_probability)}
                            </strong>
                            <span>Xác suất đầu ra</span>
                        </div>
                    </div>
                    <details className="alert-run-context">
                        <summary>Thông tin lần chạy</summary>
                        <dl>
                            <div>
                                <dt>Mã cảnh báo</dt>
                                <dd>{number(detail.id)}</dd>
                            </div>
                            <div>
                                <dt>ID lần chạy</dt>
                                <dd className="mono break-word">
                                    {detail.run_id}
                                </dd>
                            </div>
                        </dl>
                    </details>
                </div>
                <div className="alert-explanation-statuses">
                    <span>
                        XAI <Badge status={detail.explanation_status} />
                    </span>
                    <span>
                        Gemini <Badge status={detail.gemini_status} />
                    </span>
                </div>
                <Link
                    className="button accent-button alert-evidence-link"
                    href={`/runs/${detail.run_id}/rows/${detail.row_index}?${query({ audience, return: returnUrl })}`}
                >
                    <Sparkles className="icon" aria-hidden="true" />
                    <span>Xem dự đoán, SHAP và Gemini</span>
                    <ArrowUpRight className="icon" aria-hidden="true" />
                </Link>
                <label className="field">
                    <span className="alert-note-heading">
                        <span>
                            <ClipboardPenLine
                                className="icon"
                                aria-hidden="true"
                            />
                            Ghi chú người vận hành
                        </span>
                        <small>{number(note.length)} / 2.000</small>
                    </span>
                    <textarea
                        id="alert-note"
                        maxLength={2000}
                        placeholder="Kết quả kiểm tra hoặc lý do đóng cảnh báo…"
                        value={note}
                        onChange={(event) => {
                            setNote(event.target.value);
                            onDirty(true);
                        }}
                    />
                    <small>
                        Tối đa 2.000 ký tự. Đóng cảnh báo cần có lý do; vẫn có
                        thể mở lại.
                    </small>
                </label>
                <ErrorNotice error={action.error} />
                <div className="actions alert-editor-actions">
                    <button
                        data-alert-status={detail.status}
                        disabled={action.pending}
                        onClick={() => save(detail.status)}
                    >
                        <Save className="icon" aria-hidden="true" />
                        Lưu ghi chú
                    </button>
                    {detail.status !== "acknowledged" ? (
                        <button
                            className="primary"
                            data-alert-status="acknowledged"
                            disabled={action.pending}
                            onClick={() => save("acknowledged")}
                        >
                            <CheckCircle2 className="icon" aria-hidden="true" />
                            {detail.status === "closed"
                                ? "Mở lại cảnh báo"
                                : "Tiếp nhận"}
                        </button>
                    ) : (
                        <button
                            className="primary"
                            data-alert-status="closed"
                            disabled={action.pending}
                            onClick={() => {
                                if (!note.trim()) save("closed");
                                else setClosing(true);
                            }}
                        >
                            Đóng cảnh báo
                        </button>
                    )}
                </div>
                <p className="scope-note">
                    <Info className="icon" aria-hidden="true" />
                    Tiếp nhận/đóng là trạng thái xử lý vận hành, chưa xác nhận
                    dự đoán đúng.
                </p>
                <details className="alert-disclosure">
                    <summary>Hướng dẫn kiểm tra theo lớp</summary>
                    <PlaybookView value={detail.playbook} />
                </details>
                <details className="alert-disclosure alert-history">
                    <summary>
                        Lịch sử xử lý{" "}
                        <span className="small muted">
                            ({number(detail.history.length)})
                        </span>
                    </summary>
                    <ol className="timeline alert-timeline">
                        {detail.history.map((item) => (
                            <li key={item.id}>
                                <time dateTime={item.created_at}>
                                    {time(item.created_at)}
                                </time>
                                <div>
                                    <Badge status={item.status} /> ·{" "}
                                    {item.actor}
                                </div>
                                <p>
                                    {item.note || "Không có ghi chú bổ sung."}
                                </p>
                            </li>
                        ))}
                    </ol>
                </details>
            </div>
            {closing && (
                <ConfirmDialog
                    title="Đóng cảnh báo?"
                    text="Ghi nhận xử lý vận hành và lý do đóng. Thao tác này không xác nhận nhãn thật; bạn có thể mở lại."
                    accept="Đóng cảnh báo"
                    onCancel={() => setClosing(false)}
                    onConfirm={() => {
                        setClosing(false);
                        save("closed");
                    }}
                />
            )}
        </>
    );
}
