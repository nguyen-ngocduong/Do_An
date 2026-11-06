"use client";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { Check, Sparkles, X, FileChartColumn, Search } from "lucide-react";
import { getRun } from "@/lib/api/runs";
import { getPredictions } from "@/lib/api/predictions";
import { getExplanation, requestExplanations } from "@/lib/api/explanations";
import { query } from "@/lib/api/client";
import { audienceValue, pageOffset } from "@/lib/navigation";
import { usePolling } from "@/lib/use-polling";
import { toggleSelection, selectPage } from "@/lib/selection";
import { useAction } from "@/lib/use-action";
import { useUi } from "@/store/ui-store";
import { ACTIVE_CASES } from "@/types/explanation";
import {
    number,
    percent,
    rowName,
    statusLabel,
    seconds,
    time,
} from "@/lib/format";
import {
    AudienceSelect,
    Badge,
    ClassOptions,
    Empty,
    ErrorNotice,
    Loading,
    PageHeading,
    Pagination,
    RunTabs,
    Tabs,
} from "@/components/shared/controls";
import {
    GeminiView,
    ProbabilityView,
    ShapView,
} from "@/components/explanations/evidence";

export function PredictionBrowser({ id }: { id: string }) {
    const params = useSearchParams();
    const router = useRouter();
    const pathname = usePathname();
    const ui = useUi();
    const { saveTable, getTable } = ui;
    const [initial] = useState(() => ui.getTable(id));
    const [selected, setSelected] = useState(initial.selected);
    const [peekOpen, setPeekOpen] = useState(initial.peekOpen);
    const [peekTab, setPeekTab] = useState(initial.peekTab);
    const [useGemini, setUseGemini] = useState(false);
    const [lookupRun, setLookupRun] = useState(id);
    const [lookupRow, setLookupRow] = useState("0");
    const [quickRow, setQuickRow] = useState("");
    const tableRef = useRef<HTMLDivElement>(null);
    const restored = useRef(false);
    const selectAll = useRef<HTMLInputElement>(null);
    const audience = audienceValue(params.get("audience"));
    const predictedClass = params.get("class") || "";
    const status = params.get("status") || "";
    const offset = pageOffset(params.get("offset"));
    const load = useCallback(
        async (signal: AbortSignal) => {
            const [run, page] = await Promise.all([
                getRun(id, signal),
                getPredictions(
                    id,
                    {
                        offset,
                        limit: 20,
                        predicted_class: predictedClass,
                        explanation_status: status,
                        audience_level: audience,
                    },
                    signal,
                ),
            ]);
            return { run, page };
        },
        [id, offset, predictedClass, status, audience],
    );
    const poll = usePolling(
        `predictions:${id}:${offset}:${predictedClass}:${status}:${audience}`,
        load,
    );
    const peekIndex = params.has("row")
        ? pageOffset(params.get("row"))
        : (initial.peekIndex ?? poll.data?.page.items[0]?.row_index ?? null);
    const loadPeek = useCallback(
        async (signal: AbortSignal) => {
            if (!peekOpen || peekIndex === null) return null;
            const page = await getPredictions(
                id,
                { limit: 1000, audience_level: audience },
                signal,
            );
            const prediction = page.items.find(
                (item) => item.row_index === peekIndex,
            );
            if (!prediction) return null;
            const detail =
                prediction.explanation_status === "not_requested"
                    ? null
                    : await getExplanation(id, peekIndex, audience, signal);
            return { prediction, detail };
        },
        [id, peekIndex, peekOpen, audience],
    );
    const peek = usePolling(
        `peek:${id}:${peekIndex}:${peekOpen}:${audience}`,
        loadPeek,
    );
    const action = useAction();
    const lookupAction = useAction();
    const currentQuery = params.toString();
    const setQuery = useCallback(
        (changes: Record<string, string | number>) => {
            const values = new URLSearchParams(currentQuery);
            for (const [key, value] of Object.entries(changes)) {
                if (value === "") values.delete(key);
                else values.set(key, String(value));
            }
            router.replace(`${pathname}?${values}`, { scroll: false });
        },
        [currentQuery, pathname, router],
    );
    const saveSnapshot = useCallback(() => {
        // Bỏ sự kiện cuộn đến muộn từ trang vừa rời khỏi.
        if (window.location.pathname !== pathname) return;
        const saved = getTable(id);
        const main = document.getElementById("main-content");
        saveTable(id, {
            selected,
            peekIndex,
            peekOpen,
            peekTab,
            scrollTop: restored.current
                ? main?.scrollTop || window.scrollY
                : saved.scrollTop,
            scrollLeft: restored.current
                ? tableRef.current?.scrollLeft || 0
                : saved.scrollLeft,
        });
    }, [
        saveTable,
        id,
        selected,
        peekIndex,
        peekOpen,
        peekTab,
        getTable,
        pathname,
    ]);
    // Next có thể giữ state trang khi quay lại. Reset cờ ở cleanup để khôi phục
    // vị trí mới nhất trong store, thay vì chỉ dùng vị trí lúc render đầu.
    useEffect(
        () => () => {
            restored.current = false;
        },
        [],
    );
    useEffect(() => {
        if (poll.data && !restored.current) {
            const saved = getTable(id);
            const main = document.getElementById("main-content");
            if (main) main.scrollTop = saved.scrollTop;
            if (tableRef.current)
                tableRef.current.scrollLeft = saved.scrollLeft;
            if (innerWidth <= 760) window.scrollTo(0, saved.scrollTop);
            restored.current = true;
        }
        saveSnapshot();
        const main = document.getElementById("main-content");
        main?.addEventListener("scroll", saveSnapshot);
        window.addEventListener("scroll", saveSnapshot);
        return () => {
            main?.removeEventListener("scroll", saveSnapshot);
            window.removeEventListener("scroll", saveSnapshot);
        };
    }, [poll.data, id, getTable, saveSnapshot]);
    const items = poll.data?.page.items || [];
    const checkedCount = items.filter((item) =>
        selected.includes(item.row_index),
    ).length;
    useEffect(() => {
        if (selectAll.current)
            selectAll.current.indeterminate =
                checkedCount > 0 && checkedCount < items.length;
    }, [checkedCount, items.length]);
    function toggleRow(row: number) {
        const limit = ui.metadata.data?.model.limits.explanation_rows || 50;
        if (!selected.includes(row) && selected.length >= limit)
            ui.notify("Mỗi yêu cầu tối đa 50 dòng.");
        setSelected(toggleSelection(selected, row, limit));
    }
    const returnUrl = `${pathname}?${query({ class: predictedClass, status, audience, offset, row: peekIndex })}`;
    const detailUrl = (row: number) =>
        `/runs/${id}/rows/${row}?${query({ audience, return: returnUrl })}`;
    const states = [
        "not_requested",
        ...ACTIVE_CASES,
        "completed",
        "partial",
        "failed",
        "interrupted",
    ];
    return (
        <>
            <PageHeading
                title="Dự đoán"
                description={
                    poll.data
                        ? `${poll.data.run.filename} · ${poll.data.run.processed_rows} / ${poll.data.run.total_rows} dòng đã dự đoán · ${statusLabel(poll.data.run.status)}`
                        : "Đang đọc lần chạy…"
                }
            />
            <RunTabs id={id} selected="predictions" />
            <ErrorNotice
                error={action.error || lookupAction.error || poll.error}
                retry={poll.refresh}
            />
            <div
                className={`explorer prediction-explorer ${peekOpen ? "with-peek" : ""}`}
            >
                <div className="prediction-workspace">
                    <div className="filters prediction-filters">
                        <label>
                            Lớp dự đoán
                            <select
                                id="class-filter"
                                value={predictedClass}
                                onChange={(event) =>
                                    setQuery({
                                        class: event.target.value,
                                        offset: 0,
                                    })
                                }
                            >
                                <ClassOptions />
                            </select>
                        </label>
                        <label>
                            Trạng thái giải thích
                            <select
                                id="status-filter"
                                value={status}
                                onChange={(event) =>
                                    setQuery({
                                        status: event.target.value,
                                        offset: 0,
                                    })
                                }
                            >
                                <option value="">
                                    Mọi trạng thái giải thích
                                </option>
                                {states.map((value) => (
                                    <option key={value} value={value}>
                                        {statusLabel(value)}
                                    </option>
                                ))}
                            </select>
                        </label>
                        <label>
                            Mức diễn giải
                            <AudienceSelect
                                id="audience-filter"
                                value={audience}
                                onChange={(audience) =>
                                    setQuery({ audience, offset: 0 })
                                }
                            />
                        </label>
                        <form
                            className="prediction-jump"
                            onSubmit={(event) => {
                                event.preventDefault();
                                void lookupAction.run(
                                    async () => {
                                        const row = Number(
                                            quickRow.trim().replace(/^#/, ""),
                                        );
                                        if (
                                            !/^#?\d+$/.test(quickRow.trim()) ||
                                            !Number.isSafeInteger(row)
                                        ) {
                                            throw new Error(
                                                "Nhập chỉ số dòng hợp lệ, ví dụ #000014.",
                                            );
                                        }
                                        if (
                                            !poll.data ||
                                            row >= poll.data.run.processed_rows
                                        ) {
                                            throw new Error(
                                                "Dòng này chưa có kết quả dự đoán. Kiểm tra chỉ số hoặc chờ lần chạy hoàn tất.",
                                            );
                                        }
                                        return row;
                                    },
                                    (row) => {
                                        setPeekOpen(true);
                                        setQuery({
                                            row,
                                            offset: Math.floor(row / 20) * 20,
                                            class: "",
                                            status: "",
                                        });
                                    },
                                );
                            }}
                        >
                            <label htmlFor="prediction-jump-row">
                                Đi tới dòng
                            </label>
                            <div className="prediction-jump-field">
                                <input
                                    id="prediction-jump-row"
                                    inputMode="numeric"
                                    placeholder="#000014"
                                    value={quickRow}
                                    onChange={(event) =>
                                        setQuickRow(event.target.value)
                                    }
                                />
                                <button
                                    type="submit"
                                    aria-label="Đi tới dòng dự đoán"
                                    disabled={lookupAction.pending}
                                >
                                    <Search
                                        className="icon"
                                        aria-hidden="true"
                                    />
                                </button>
                            </div>
                        </form>
                    </div>
                    <details className="lookup">
                        <summary>Đi tới run / dòng</summary>
                        <form
                            className="filters"
                            onSubmit={(event) => {
                                event.preventDefault();
                                void lookupAction.run(
                                    async () => {
                                        const run = await getRun(lookupRun);
                                        const row = Number(lookupRow);
                                        if (
                                            !Number.isSafeInteger(row) ||
                                            row < 0 ||
                                            row >= run.total_rows
                                        )
                                            throw new Error(
                                                `CSV chỉ có ${run.total_rows} dòng, chỉ số từ 0.`,
                                            );
                                        return row;
                                    },
                                    (row) =>
                                        router.push(
                                            `/runs/${lookupRun}/rows/${row}?${query({ audience, return: returnUrl })}`,
                                        ),
                                );
                            }}
                        >
                            <label className="run-input">
                                ID lần chạy
                                <input
                                    required
                                    pattern="[a-f0-9]{32}"
                                    value={lookupRun}
                                    onChange={(event) =>
                                        setLookupRun(event.target.value)
                                    }
                                />
                            </label>
                            <label className="row-input">
                                Chỉ số dòng (từ 0)
                                <input
                                    type="number"
                                    min="0"
                                    step="1"
                                    required
                                    value={lookupRow}
                                    onChange={(event) =>
                                        setLookupRow(event.target.value)
                                    }
                                />
                            </label>
                            <button disabled={lookupAction.pending}>
                                Mở mẫu
                            </button>
                        </form>
                    </details>
                    <div
                        id="bulk-action"
                        className="bulk-action"
                        hidden={!selected.length}
                    >
                        <div className="bulk-summary">
                            <span className="bulk-count">
                                <Check className="icon" aria-hidden="true" />
                            </span>
                            <div>
                                <strong>Đã chọn {selected.length} dòng</strong>
                                <p>Tối đa 50 dòng mỗi yêu cầu</p>
                            </div>
                        </div>
                        <div className="bulk-options">
                            <label
                                className={`gemini-option ${useGemini ? "enabled" : ""}`}
                            >
                                <input
                                    id="use-gemini"
                                    type="checkbox"
                                    checked={useGemini}
                                    onChange={(event) =>
                                        setUseGemini(event.target.checked)
                                    }
                                />
                                <Sparkles className="icon" aria-hidden="true" />
                                <strong>Dùng Gemini</strong>
                            </label>
                            <div className="bulk-audience">
                                <span>Mức diễn giải</span>
                                <strong>Kỹ thuật</strong>
                            </div>
                            <button
                                className="text-button bulk-clear"
                                aria-label="Bỏ chọn tất cả dòng"
                                onClick={() => setSelected([])}
                            >
                                <X className="icon" aria-hidden="true" />
                                Bỏ chọn
                            </button>
                            <button
                                className="primary"
                                id="explain-selected"
                                disabled={action.pending || !selected.length}
                                onClick={() =>
                                    action.run(
                                        () =>
                                            requestExplanations(id, {
                                                row_indices: [...selected].sort(
                                                    (a, b) => a - b,
                                                ),
                                                use_gemini: useGemini,
                                                audience_level: "technical",
                                                retry_gemini: false,
                                            }),
                                        () => {
                                            setSelected([]);
                                            ui.notify(
                                                "Đã tiếp nhận yêu cầu; theo dõi trạng thái trên bảng.",
                                            );
                                            if (audience !== "technical") {
                                                setQuery({
                                                    audience: "technical",
                                                });
                                            } else {
                                                poll.refresh();
                                                peek.refresh();
                                            }
                                        },
                                    )
                                }
                            >
                                {action.pending
                                    ? "Đang gửi…"
                                    : `Giải thích ${selected.length} dòng`}
                            </button>
                        </div>
                    </div>
                    <div className="explorer-table">
                        <div className="table-caption">
                            <strong>
                                {poll.data
                                    ? `${number(poll.data.page.total)} kết quả khớp / ${number(poll.data.page.total_predicted)} đã dự đoán`
                                    : "Đang tải…"}
                            </strong>
                            <span className="muted">
                                Tám lớp · chỉ số dòng từ 0
                            </span>
                        </div>
                        <div
                            className="table-wrap"
                            id="prediction-table"
                            ref={tableRef}
                            onScroll={saveSnapshot}
                        >
                            {!poll.data ? (
                                <Loading />
                            ) : !items.length ? (
                                <Empty
                                    title="Chưa có kết quả phù hợp"
                                    description="Thử đổi bộ lọc hoặc xem tiến độ dự đoán."
                                />
                            ) : (
                                <table>
                                    <thead>
                                        <tr>
                                            <th>
                                                <input
                                                    ref={selectAll}
                                                    className="row-check"
                                                    type="checkbox"
                                                    aria-label="Chọn các dòng trong trang"
                                                    checked={
                                                        checkedCount ===
                                                        items.length
                                                    }
                                                    onChange={(event) =>
                                                        setSelected(
                                                            selectPage(
                                                                selected,
                                                                items.map(
                                                                    (item) =>
                                                                        item.row_index,
                                                                ),
                                                                event.target
                                                                    .checked,
                                                            ),
                                                        )
                                                    }
                                                />
                                            </th>
                                            <th>Chỉ số dòng</th>
                                            <th>Nhãn dự đoán</th>
                                            <th className="numeric-cell">
                                                Xác suất đầu ra
                                            </th>
                                            <th>Thời điểm xử lý</th>
                                            <th>Giải thích</th>
                                            <th>Xem</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {items.map((item) => (
                                            <tr
                                                key={item.row_index}
                                                data-row={item.row_index}
                                                className={
                                                    selected.includes(
                                                        item.row_index,
                                                    )
                                                        ? "selected"
                                                        : ""
                                                }
                                            >
                                                <td>
                                                    <input
                                                        className="row-check"
                                                        type="checkbox"
                                                        data-select-row={
                                                            item.row_index
                                                        }
                                                        aria-label={`Chọn dòng ${item.row_index}`}
                                                        checked={selected.includes(
                                                            item.row_index,
                                                        )}
                                                        onChange={() =>
                                                            toggleRow(
                                                                item.row_index,
                                                            )
                                                        }
                                                    />
                                                </td>
                                                <td>
                                                    <Link
                                                        className="mono"
                                                        scroll={false}
                                                        href={detailUrl(
                                                            item.row_index,
                                                        )}
                                                    >
                                                        {rowName(
                                                            item.row_index,
                                                        )}
                                                    </Link>
                                                </td>
                                                <td>
                                                    <span
                                                        className="class-cell"
                                                        data-class={
                                                            item.predicted_class
                                                        }
                                                    >
                                                        <span
                                                            className="class-dot"
                                                            data-class={
                                                                item.predicted_class
                                                            }
                                                            aria-hidden="true"
                                                        />
                                                        {item.predicted_class}
                                                    </span>
                                                </td>
                                                <td className="numeric-cell">
                                                    <div
                                                        className="prediction-probability"
                                                        data-class={
                                                            item.predicted_class
                                                        }
                                                    >
                                                        <span className="mono">
                                                            {percent(
                                                                item.predicted_probability,
                                                            )}
                                                        </span>
                                                        <span
                                                            className="meter"
                                                            aria-hidden="true"
                                                        >
                                                            <span
                                                                style={{
                                                                    width: `${Math.max(0, Math.min(100, item.predicted_probability * 100))}%`,
                                                                }}
                                                            />
                                                        </span>
                                                    </div>
                                                </td>
                                                <td className="prediction-timing">
                                                    <time
                                                        dateTime={
                                                            item.created_at
                                                        }
                                                        title={item.created_at}
                                                    >
                                                        {time(item.created_at)}
                                                    </time>
                                                    <small className="muted">
                                                        {poll.data?.run.mode ===
                                                        "batch"
                                                            ? "Bình quân batch"
                                                            : "Suy luận dòng"}
                                                        :{" "}
                                                        {seconds(
                                                            item.predict_seconds,
                                                        )}
                                                    </small>
                                                </td>
                                                <td>
                                                    <Badge
                                                        status={
                                                            item.explanation_status
                                                        }
                                                    />
                                                </td>
                                                <td>
                                                    <button
                                                        className="text-button"
                                                        data-peek-row={
                                                            item.row_index
                                                        }
                                                        aria-label={`Xem nhanh dòng ${item.row_index}`}
                                                        onClick={() => {
                                                            setPeekOpen(true);
                                                            setQuery({
                                                                row: item.row_index,
                                                            });
                                                        }}
                                                    >
                                                        Xem nhanh
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                        {poll.data && (
                            <Pagination
                                total={poll.data.page.total}
                                offset={offset}
                                onChange={(offset) => setQuery({ offset })}
                            />
                        )}
                    </div>
                </div>
                {peekOpen && (
                    <aside
                        id="peek"
                        className="peek-pane"
                        aria-label="Khung xem nhanh"
                    >
                        <div className="peek-head">
                            <div className="peek-identity">
                                <strong>
                                    <span
                                        className="peek-dot"
                                        aria-hidden="true"
                                    />
                                    {peekIndex === null
                                        ? "Chọn một dòng"
                                        : `Dòng ${rowName(peekIndex)}`}
                                </strong>
                                <span className="small muted">
                                    Mẫu CSV · Chỉ số dòng từ 0
                                </span>
                            </div>
                            <button
                                id="close-peek"
                                className="icon-button"
                                aria-label="Đóng khung xem nhanh"
                                title="Đóng khung xem nhanh"
                                onClick={() => setPeekOpen(false)}
                            >
                                <X className="icon" aria-hidden="true" />
                            </button>
                        </div>
                        <ErrorNotice error={peek.error} retry={peek.refresh} />
                        {peek.data ? (
                            <>
                                <div className="peek-body">
                                    <div className="peek-outcome">
                                        <div>
                                            <span
                                                className={`peek-category ${peek.data.prediction.predicted_class === "Normal" ? "normal" : "attack"}`}
                                            >
                                                {peek.data.prediction
                                                    .predicted_class ===
                                                "Normal"
                                                    ? "Dự đoán Normal"
                                                    : "Nhãn khác Normal"}
                                            </span>
                                            <strong>
                                                {
                                                    peek.data.prediction
                                                        .predicted_class
                                                }
                                            </strong>
                                        </div>
                                        <div className="peek-probability">
                                            <strong className="mono">
                                                {percent(
                                                    peek.data.prediction
                                                        .predicted_probability,
                                                )}
                                            </strong>
                                            <span>Xác suất đầu ra</span>
                                        </div>
                                    </div>
                                    <div className="peek-xai-status">
                                        <span>Giải thích XAI</span>
                                        <Badge
                                            status={
                                                peek.data.detail?.status ||
                                                peek.data.prediction
                                                    .explanation_status
                                            }
                                        />
                                    </div>
                                    <Tabs
                                        items={[
                                            ["predict", "Dự đoán"],
                                            ["shap", "SHAP"],
                                            ["gemini", "Gemini"],
                                        ]}
                                        value={peekTab}
                                        onChange={setPeekTab}
                                        name="Xem nhanh"
                                    />
                                    <div role="tabpanel">
                                        {peekTab === "predict" ? (
                                            <>
                                                <div className="peek-probability-heading">
                                                    <span>Nhãn phân loại</span>
                                                    <span>Xác suất</span>
                                                </div>
                                                <ProbabilityView
                                                    predictedClass={
                                                        peek.data.prediction
                                                            .predicted_class
                                                    }
                                                    values={
                                                        peek.data.prediction
                                                            .probabilities
                                                    }
                                                />
                                            </>
                                        ) : peekTab === "shap" ? (
                                            <ShapView
                                                item={
                                                    peek.data.detail
                                                        ?.explanation
                                                }
                                                compact
                                            />
                                        ) : (
                                            <GeminiView
                                                detail={peek.data.detail}
                                                compact
                                            />
                                        )}
                                    </div>
                                </div>
                                <div className="peek-footer">
                                    <Link
                                        id="peek-full-results"
                                        className="button accent-button"
                                        href={
                                            detailUrl(
                                                peek.data.prediction.row_index,
                                            ) + "&stage=overview"
                                        }
                                    >
                                        <FileChartColumn
                                            className="icon"
                                            aria-hidden="true"
                                        />
                                        Xem toàn bộ kết quả
                                    </Link>
                                </div>
                            </>
                        ) : peekIndex === null ? (
                            <Empty
                                title="Chọn một dòng để xem nhanh"
                                description="Checkbox chọn mẫu cần giải thích độc lập với khung này."
                            />
                        ) : (
                            <Loading />
                        )}
                    </aside>
                )}
            </div>
            <p className="scope-note">
                Chọn tối đa 50 dòng đã dự đoán để giải thích, gồm cả Normal.
                Đang xếp hàng nghĩa là đã tiếp nhận, chưa phải lỗi API key.
            </p>
        </>
    );
}
