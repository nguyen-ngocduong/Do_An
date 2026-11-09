"use client";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import { Trash2 } from "lucide-react";
import { deleteRun, listRuns } from "@/lib/api/runs";
import { useAction } from "@/lib/use-action";
import { useUi } from "@/store/ui-store";
import type { RunInfo } from "@/types/run";
import { usePolling } from "@/lib/use-polling";
import { pageOffset } from "@/lib/navigation";
import { number, time } from "@/lib/format";
import {
    Badge,
    ConfirmDialog,
    Empty,
    ErrorNotice,
    Loading,
    PageHeading,
    Pagination,
} from "@/components/shared/controls";
export function RunHistory() {
    const params = useSearchParams();
    const router = useRouter();
    const offset = pageOffset(params.get("offset"));
    const load = useCallback(
        (signal: AbortSignal) => listRuns(offset, signal),
        [offset],
    );
    const poll = usePolling(`history:${offset}`, load);
    const action = useAction();
    const ui = useUi();
    const [toDelete, setToDelete] = useState<RunInfo | null>(null);
    const [cleanupWarning, setCleanupWarning] = useState("");
    const confirmDelete = () => {
        if (!toDelete) return;
        const id = toDelete.id;
        setToDelete(null);
        setCleanupWarning("");
        void action.run(
            () => deleteRun(id),
            (result) => {
                ui.forgetRun(id);
                if (result.files_deleted) ui.notify(result.message);
                else setCleanupWarning(result.message);
                if (poll.data?.items.length === 1 && offset > 0)
                    router.replace(`/runs?offset=${Math.max(0, offset - 20)}`);
                poll.refresh();
            },
        );
    };
    return (
        <>
            <PageHeading
                title="Lịch sử lần chạy"
                info="Các file CSV và kết quả đã lưu trên server."
            />
            <ErrorNotice error={poll.error} retry={poll.refresh} />
            <ErrorNotice error={action.error} />
            {cleanupWarning && (
                <p className="notice warning" role="status">
                    {cleanupWarning}
                </p>
            )}
            {action.pending && (
                <p className="muted" role="status">
                    Đang xóa lần chạy…
                </p>
            )}
            {toDelete && (
                <ConfirmDialog
                    title="Xóa lần chạy?"
                    text={`Xóa “${toDelete.filename}” (tạo lúc ${time(toDelete.created_at)}) cùng dữ liệu CSV đã tải lên, dự đoán, SHAP, Gemini, cảnh báo và đánh giá thủ công của lần chạy này. Không thể hoàn tác.`}
                    accept="Xóa lần chạy"
                    danger
                    onConfirm={confirmDelete}
                    onCancel={() => setToDelete(null)}
                />
            )}
            {!poll.data ? (
                <Loading />
            ) : !poll.data.items.length ? (
                <Empty
                    title={
                        poll.data.total
                            ? "Trang này không còn lần chạy"
                            : "Chưa có lần chạy"
                    }
                    description={
                        poll.data.total
                            ? "Các lần chạy còn lại nằm ở trang trước."
                            : "Tải một CSV gồm 46 đặc trưng gốc để bắt đầu dự đoán, sau đó chọn mẫu cần giải thích."
                    }
                >
                    <Link
                        className="button primary"
                        href={poll.data.total ? "/runs" : "/runs/new"}
                    >
                        {poll.data.total ? "Về trang đầu" : "Tải CSV đầu tiên"}
                    </Link>
                </Empty>
            ) : (
                <>
                    <div className="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>Tệp CSV</th>
                                    <th>Chế độ</th>
                                    <th className="numeric-cell">Tiến độ</th>
                                    <th>Trạng thái</th>
                                    <th>Thời gian tạo</th>
                                    <th className="numeric-cell">Thao tác</th>
                                </tr>
                            </thead>
                            <tbody>
                                {poll.data.items.map((run) => (
                                    <tr key={run.id}>
                                        <td className="wrap">
                                            <strong>{run.filename}</strong>
                                        </td>
                                        <td>
                                            {run.mode === "replay"
                                                ? "Replay"
                                                : "Batch"}
                                        </td>
                                        <td className="mono numeric-cell">
                                            {number(run.processed_rows)} /{" "}
                                            {number(run.total_rows)}
                                        </td>
                                        <td>
                                            <Badge status={run.status} />
                                        </td>
                                        <td>{time(run.created_at)}</td>
                                        <td>
                                            <div className="history-actions">
                                                <Link
                                                    href={`/runs/${run.id}/predictions`}
                                                >
                                                    Mở kết quả
                                                </Link>
                                                <button
                                                    className="text-button danger-button"
                                                    data-delete-run={run.id}
                                                    aria-label={`Xóa ${run.filename}, tạo lúc ${time(run.created_at)}`}
                                                    title={
                                                        [
                                                            "queued",
                                                            "running",
                                                            "paused",
                                                        ].includes(run.status)
                                                            ? "Chờ dự đoán hoàn tất hoặc dừng Replay trước khi xóa"
                                                            : "Xóa lần chạy và kết quả đã lưu"
                                                    }
                                                    disabled={
                                                        action.pending ||
                                                        [
                                                            "queued",
                                                            "running",
                                                            "paused",
                                                        ].includes(run.status)
                                                    }
                                                    onClick={() =>
                                                        setToDelete(run)
                                                    }
                                                >
                                                    <Trash2
                                                        className="icon"
                                                        aria-hidden="true"
                                                    />
                                                    Xóa
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    <Pagination
                        total={poll.data.total}
                        offset={offset}
                        onChange={(value) =>
                            router.replace(`/runs?offset=${value}`)
                        }
                    />
                </>
            )}
        </>
    );
}
