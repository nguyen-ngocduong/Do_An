"use client";
import Link from "next/link";
import { useEffect, useRef } from "react";
import { List, Download } from "lucide-react";
import { CLASS_NAMES, type Audience, type ClassName } from "@/types/model";
import { number, percent, statusLabel } from "@/lib/format";
import { ApiError, download, errorText } from "@/lib/api/client";
import { useAction } from "@/lib/use-action";
import { useUi } from "@/store/ui-store";

export function PageHeading({
    title,
    description,
    actions,
}: {
    title: string;
    description?: string;
    actions?: React.ReactNode;
}) {
    return (
        <div className="pagehead">
            <div>
                <h1>{title}</h1>
                <p>{description}</p>
            </div>
            <div className="actions">{actions}</div>
        </div>
    );
}
export function Loading() {
    return (
        <div className="loading" role="status" aria-label="Đang tải dữ liệu">
            <div />
            <div />
            <div />
        </div>
    );
}
export function Empty({
    title,
    description,
    children,
}: {
    title: string;
    description: string;
    children?: React.ReactNode;
}) {
    return (
        <div className="empty-state">
            <List className="icon" />
            <h2>{title}</h2>
            <p>{description}</p>
            {children}
        </div>
    );
}
export function ErrorNotice({
    error,
    retry,
}: {
    error: unknown;
    retry?: () => void;
}) {
    if (!error) return null;
    return (
        <div id="page-message" className="notice error" role="alert">
            {errorText(error)}{" "}
            <div className="actions">
                {error instanceof ApiError && error.status === 401 && (
                    <Link
                        className="button"
                        href="/login"
                    >
                        Đăng nhập lại
                    </Link>
                )}
                {retry && <button onClick={retry}>Thử lại</button>}
            </div>
        </div>
    );
}
export function Badge({ status }: { status?: string }) {
    let tone = "neutral";
    if (["completed", "accepted", "closed"].includes(status || ""))
        tone = "success";
    if (
        [
            "partial",
            "paused",
            "interrupted",
            "needs_text_review",
            "not_configured",
        ].includes(status || "")
    )
        tone = "warning";
    if (
        ["failed", "api_error", "request_error", "invalid_evidence"].includes(
            status || "",
        )
    )
        tone = "danger";
    if (
        [
            "running",
            "queued",
            "shap_running",
            "gemini_running",
            "acknowledged",
        ].includes(status || "")
    )
        tone = "accent";
    return (
        <span data-status={status} className={`badge ${tone}`}>
            {statusLabel(status)}
        </span>
    );
}
export function ClassBadge({
    name,
    probability,
}: {
    name: ClassName;
    probability?: number;
}) {
    return (
        <span className="class-badge" data-class={name}>
            <span>{name}</span>
            {probability !== undefined && <span>{percent(probability)}</span>}
        </span>
    );
}
export function ClassOptions() {
    return (
        <>
            <option value="">Tất cả tám lớp</option>
            {CLASS_NAMES.map((name) => (
                <option key={name}>{name}</option>
            ))}
        </>
    );
}
export function AudienceSelect({
    value,
    onChange,
    id,
}: {
    value: Audience;
    onChange: (value: Audience) => void;
    id?: string;
}) {
    return (
        <select
            id={id}
            value={value}
            onChange={(event) => onChange(event.target.value as Audience)}
        >
            <option value="technical">Kỹ thuật</option>
            <option value="basic">Dễ hiểu</option>
        </select>
    );
}
export function RunTabs({ id, selected }: { id: string; selected: string }) {
    return (
        <nav className="run-tabs" aria-label="Các phần của lần chạy">
            {[
                ["monitor", "Theo dõi"],
                ["predictions", "Dự đoán & giải thích"],
                ["export", "Xuất kết quả"],
            ].map(([key, title]) => (
                <Link
                    key={key}
                    href={`/runs/${id}/${key}`}
                    aria-current={selected === key ? "page" : undefined}
                >
                    {title}
                </Link>
            ))}
        </nav>
    );
}
export function Pagination({
    total,
    offset,
    limit = 20,
    onChange,
}: {
    total: number;
    offset: number;
    limit?: number;
    onChange: (offset: number) => void;
}) {
    return (
        <div className="pagination">
            <span>
                {total
                    ? `${number(offset + 1)}–${number(Math.min(offset + limit, total))} / ${number(total)}`
                    : "0 kết quả"}
            </span>
            <div className="actions">
                <button
                    data-page="prev"
                    disabled={!offset}
                    onClick={() => onChange(Math.max(0, offset - limit))}
                >
                    Trước
                </button>
                <span>
                    Trang {Math.floor(offset / limit) + 1} /{" "}
                    {Math.max(1, Math.ceil(total / limit))}
                </span>
                <button
                    data-page="next"
                    disabled={offset + limit >= total}
                    onClick={() => onChange(offset + limit)}
                >
                    Sau
                </button>
            </div>
        </div>
    );
}
export function KeyValues({ values }: { values: [string, React.ReactNode][] }) {
    return (
        <dl className="key-values">
            {values.map(([key, value]) => (
                <div key={key}>
                    <dt>{key}</dt>
                    <dd>{value ?? "—"}</dd>
                </div>
            ))}
        </dl>
    );
}
export function JsonViewer({
    value,
    title = "JSON",
}: {
    value: unknown;
    title?: string;
}) {
    const field = useRef<HTMLTextAreaElement>(null);
    const ui = useUi();
    async function copy() {
        field.current?.focus();
        field.current?.select();
        try {
            await navigator.clipboard.writeText(JSON.stringify(value, null, 2));
            ui.notify("Đã sao chép JSON.");
        } catch {
            ui.notify("Đã chọn JSON. Nhấn Ctrl+C hoặc ⌘C để sao chép.");
        }
    }
    return (
        <>
            <div className="json-heading">
                <strong>{title}</strong>
                <button onClick={copy}>Sao chép JSON</button>
            </div>
            <textarea
                ref={field}
                className="json-view"
                readOnly
                spellCheck={false}
                aria-label={title}
                value={JSON.stringify(value, null, 2)}
            />
        </>
    );
}
export function DownloadButton({
    path,
    name,
    children,
}: {
    path: string;
    name: string;
    children?: React.ReactNode;
}) {
    const action = useAction();
    const ui = useUi();
    return (
        <>
            <button
                data-filename={name}
                disabled={action.pending}
                onClick={() =>
                    action.run(
                        () => download(path, name),
                        () => ui.notify("Đã tải tệp kết quả."),
                    )
                }
            >
                <Download className="icon" />
                {action.pending ? "Đang chuẩn bị…" : children || name}
            </button>
            <ErrorNotice error={action.error} />
        </>
    );
}
export function ConfirmDialog({
    title,
    text,
    accept = "Xác nhận",
    danger = false,
    onConfirm,
    onCancel,
}: {
    title: string;
    text: string;
    accept?: string;
    danger?: boolean;
    onConfirm: () => void;
    onCancel: () => void;
}) {
    const ref = useRef<HTMLDialogElement>(null);
    useEffect(() => {
        if (ref.current && !ref.current.open) ref.current.showModal();
    }, []);
    return (
        <dialog
            ref={ref}
            id="confirm-dialog"
            onCancel={onCancel}
            aria-labelledby="confirm-title"
        >
            <h2 id="confirm-title">{title}</h2>
            <p>{text}</p>
            <div className="actions">
                <button onClick={onCancel}>Hủy</button>
                <button
                    className={danger ? "danger-primary" : "primary"}
                    id="confirm-accept"
                    onClick={onConfirm}
                >
                    {accept}
                </button>
            </div>
        </dialog>
    );
}
export function Tabs({
    items,
    value,
    onChange,
    name,
}: {
    items: [string, string][];
    value: string;
    onChange: (value: string) => void;
    name: string;
}) {
    return (
        <div
            className="tabs"
            role="tablist"
            aria-label={name}
            onKeyDown={(event) => {
                if (
                    !["ArrowLeft", "ArrowRight", "Home", "End"].includes(
                        event.key,
                    )
                )
                    return;
                let index = items.findIndex(([key]) => key === value);
                if (event.key === "Home") index = 0;
                else if (event.key === "End") index = items.length - 1;
                else
                    index =
                        (index +
                            (event.key === "ArrowRight" ? 1 : -1) +
                            items.length) %
                        items.length;
                event.preventDefault();
                onChange(items[index][0]);
                (
                    event.currentTarget.querySelectorAll("button")[
                        index
                    ] as HTMLButtonElement
                )?.focus();
            }}
        >
            {items.map(([key, title]) => (
                <button
                    key={key}
                    role="tab"
                    data-tab={key}
                    aria-selected={value === key}
                    tabIndex={value === key ? 0 : -1}
                    onClick={() => onChange(key)}
                >
                    {title}
                </button>
            ))}
        </div>
    );
}
