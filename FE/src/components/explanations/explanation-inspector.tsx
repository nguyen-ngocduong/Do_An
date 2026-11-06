"use client";
import Link from "next/link";
import Image from "next/image";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { Activity, GitBranch, MessageSquare, Workflow } from "lucide-react";
import { getRun } from "@/lib/api/runs";
import { getInput, getPredictions } from "@/lib/api/predictions";
import { getExplanation, requestExplanations } from "@/lib/api/explanations";
import { get, query } from "@/lib/api/client";
import { usePolling } from "@/lib/use-polling";
import { useAction } from "@/lib/use-action";
import { safeReturn } from "@/lib/navigation";
import type { Audience } from "@/types/model";
import { percent, rowName, seconds } from "@/lib/format";
import { useUi } from "@/store/ui-store";
import {
    ACTIVE_CASES,
    type Execution,
    type GeminiStatus,
} from "@/types/explanation";
import {
    Badge,
    ConfirmDialog,
    Empty,
    ErrorNotice,
    JsonViewer,
    KeyValues,
    Loading,
    PageHeading,
    Tabs,
} from "@/components/shared/controls";
import {
    GeminiView,
    PlaybookView,
    ProbabilityView,
    ShapView,
} from "./evidence";
import { CaseFiles } from "./case-files";
import { HumanReview } from "./human-review";
import { SectionOutline } from "./section-outline";

const stages = [
    {
        key: "overview",
        title: "Toàn pipeline",
        hint: "Dự đoán → SHAP → Gemini",
        icon: Workflow,
    },
    {
        key: "predict",
        title: "Dự đoán",
        hint: "DT / RF / HGB → XGBoost",
        icon: Activity,
    },
    { key: "shap", title: "SHAP", hint: "46 đặc trưng gốc", icon: GitBranch },
    {
        key: "gemini",
        title: "Gemini",
        hint: "Diễn giải tiếng Việt",
        icon: MessageSquare,
    },
];
const tabs: [string, string][] = [
    ["input", "Đầu vào"],
    ["output", "Đầu ra"],
    ["metadata", "Metadata"],
    ["error", "Lỗi"],
];
export function ExplanationInspector({
    id,
    index,
}: {
    id: string;
    index: number;
}) {
    const params = useSearchParams();
    const router = useRouter();
    const pathname = usePathname();
    const ui = useUi();
    const audience: Audience = "technical";
    useEffect(() => {
        if (params.get("audience") === "basic") {
            const values = new URLSearchParams(params.toString());
            values.set("audience", "technical");
            router.replace(`${pathname}?${values}`, { scroll: false });
        }
    }, [params, router, pathname]);
    const stage = stages.some((item) => item.key === params.get("stage"))
        ? params.get("stage")!
        : "shap";
    const tab = tabs.some(([key]) => key === params.get("tab"))
        ? params.get("tab")!
        : "output";
    const back = safeReturn(params.get("return"), `/runs/${id}/predictions`);
    const [useGemini, setUseGemini] = useState(false);
    const [confirmRetry, setConfirmRetry] = useState(false);
    const action = useAction();
    const model = ui.metadata.data?.model;
    const load = useCallback(
        async (signal: AbortSignal) => {
            const run = await getRun(id, signal);
            if (index >= run.total_rows)
                throw new Error("Chỉ số dòng nằm ngoài CSV của lần chạy.");
            const [inputs, predictions, detail] = await Promise.all([
                getInput(id, index, signal),
                getPredictions(
                    id,
                    { limit: 1000, audience_level: audience },
                    signal,
                ),
                getExplanation(id, index, audience, signal),
            ]);
            const readFile = <T,>(name: string) =>
                detail?.files[name]
                    ? get<T>(detail.files[name], signal)
                    : Promise.resolve(null);
            const [execution, geminiStatus, llmInput] = await Promise.all([
                readFile<Execution>("execution.json"),
                readFile<GeminiStatus>("gemini_status.json"),
                readFile<unknown>("llm_input.json"),
            ]);
            return {
                run,
                inputs,
                prediction: predictions.items.find(
                    (item) => item.row_index === index,
                ),
                detail,
                execution,
                geminiStatus,
                llmInput,
            };
        },
        [id, index, audience],
    );
    const state = usePolling(`case:${id}:${index}:${audience}`, load);
    const value = state.data;
    const detail = value?.detail;
    const prediction = value?.prediction;
    const busy =
        action.pending ||
        Boolean(detail && ACTIVE_CASES.includes(detail.status));
    function change(values: Record<string, string>) {
        const next = new URLSearchParams(params);
        for (const [key, value] of Object.entries(values)) next.set(key, value);
        router.replace(`${pathname}?${next}`, { scroll: false });
    }
    function request(retry: boolean) {
        setConfirmRetry(false);
        action.run(
            () =>
                requestExplanations(id, {
                    row_indices: [index],
                    use_gemini: retry || useGemini,
                    retry_gemini: retry,
                    audience_level: audience,
                }),
            () => {
                state.refresh();
                ui.notify("Đã tiếp nhận yêu cầu giải thích mẫu.");
            },
        );
    }
    function output() {
        if (stage === "predict" || stage === "overview")
            return (
                <>
                    <h2>
                        {stage === "predict"
                            ? "Xác suất đầu ra tám lớp"
                            : "Toàn pipeline"}
                    </h2>
                    <div className="actions">
                        <Badge status={value?.run.status} />
                        <Badge status={detail?.status || "not_requested"} />
                        {detail && <Badge status={detail.gemini_status} />}
                    </div>
                    {prediction ? (
                        <ProbabilityView values={prediction.probabilities} />
                    ) : (
                        <Empty
                            title="Chưa có dự đoán"
                            description="Dòng chưa được phát hoặc tác vụ đang chờ xử lý."
                        />
                    )}
                    <p className="scope-note">
                        Đây là đầu ra mô hình; chưa xác nhận sự kiện thực tế. Mở
                        trang này không chạy lại dự đoán hoặc Gemini.
                    </p>
                </>
            );
        if (stage === "shap")
            return (
                <>
                    <ShapView
                        item={detail?.explanation}
                        tolerance={model?.shap_config.additivity_tolerance}
                    />
                    {detail?.files["waterfall.png"] && (
                        <details className="waterfall-details">
                            <summary>
                                Biểu đồ waterfall đầy đủ (tệp PNG nguồn)
                            </summary>
                            <Image
                                unoptimized
                                width={1200}
                                height={800}
                                className="waterfall"
                                src={detail.files["waterfall.png"]}
                                loading="lazy"
                                alt={`Waterfall SHAP dòng ${index}, lớp ${detail.explanation?.explained_class}`}
                            />
                        </details>
                    )}
                </>
            );
        return (
            <div className="gemini-stage">
                <GeminiView detail={detail} />
                {detail?.playbook && (
                    <details className="gemini-playbook">
                        <summary>Hướng dẫn kiểm tra theo lớp</summary>
                        <PlaybookView value={detail.playbook} />
                    </details>
                )}
            </div>
        );
    }
    function metadata() {
        if (stage === "predict")
            return (
                <KeyValues
                    values={[
                        ["Model", model?.model_id],
                        ["Cấu trúc", "DT / RF / HGB → XGBoost"],
                        ["Số lần nạp trong process", model?.model_load_count],
                        [
                            "Thời gian ghi nhận",
                            seconds(prediction?.predict_seconds),
                        ],
                        [
                            "Phạm vi phép đo",
                            value?.run.mode === "batch"
                                ? "Thời gian batch chia đều số dòng"
                                : "Suy luận riêng dòng Replay",
                        ],
                        ["Số luồng CPU", model?.threads],
                        ["Bundle SHA256", model?.checks.bundle_sha256],
                        ["Cache runtime", "—; API chưa trả cờ hit/miss"],
                    ]}
                />
            );
        if (stage === "shap")
            return (
                <>
                    <KeyValues
                        values={[
                            [
                                "Lớp được giải thích",
                                detail?.explanation?.explained_class,
                            ],
                            ["Phạm vi", "Toàn pipeline; 46 đặc trưng gốc"],
                            [
                                "Đơn vị",
                                "Xác suất; SHAP × 100 là điểm phần trăm",
                            ],
                            [
                                "Thời gian SHAP ghi nhận",
                                seconds(detail?.explanation?.shap_seconds),
                            ],
                            ["Số dòng nền", model?.shap_config.background_size],
                            ["max_evals", model?.shap_config.max_evals],
                            ["Seed", detail?.explanation?.seed],
                            [
                                "Sai số bảo toàn lớn nhất",
                                detail?.explanation?.max_additivity_error_all_classes.toExponential(
                                    3,
                                ),
                            ],
                            ["Ngưỡng", model?.shap_config.additivity_tolerance],
                            ["Cache runtime", "—; không suy ra từ artifact"],
                        ]}
                    />
                    <p className="scope-note">
                        Thời gian artifact có thể được giữ khi dùng cache; chưa
                        phải latency yêu cầu hiện tại.
                    </p>
                </>
            );
        if (stage === "gemini")
            return (
                <>
                    <KeyValues
                        values={[
                            ["Model đang cấu hình", model?.gemini_model],
                            ["Model/version phản hồi", "—; API chưa cung cấp"],
                            [
                                "Mức diễn giải",
                                audience === "basic" ? "Dễ hiểu" : "Kỹ thuật",
                            ],
                            ["Trạng thái", detail?.gemini_status],
                            [
                                "Attempt được chọn",
                                value?.geminiStatus?.selected_attempt,
                            ],
                            [
                                "Số attempt đã lưu",
                                value?.geminiStatus?.attempts_saved,
                            ],
                            [
                                "Thời gian API ghi nhận (tổng)",
                                seconds(value?.execution?.api_seconds),
                            ],
                            [
                                "Tổng tokens ghi nhận",
                                value?.execution?.total_tokens,
                            ],
                            [
                                "Prompt version / request hash",
                                "—; API chưa cung cấp",
                            ],
                            ["Cache runtime", "—; API chưa trả cờ hit/miss"],
                        ]}
                    />
                    <p className="scope-note">
                        Tổng thời gian/tokens có thể gồm nhiều attempt; không
                        phải phép đo của lần mở trang.
                    </p>
                </>
            );
        return (
            <>
                <KeyValues
                    values={[
                        ["ID lần chạy", id],
                        ["Chỉ số dòng", index],
                        ["Tệp đầu vào", value?.run.filename],
                        ["Thời gian tạo", value?.run.created_at],
                        ["Đã nạp model", model?.model_load_count],
                    ]}
                />
                <JsonViewer
                    value={model?.checks.versions || {}}
                    title="Phiên bản thư viện server"
                />
            </>
        );
    }
    let content;
    if (tab === "input")
        content =
            stage === "gemini" ? (
                value?.llmInput ? (
                    <JsonViewer
                        value={value.llmInput}
                        title="Bằng chứng thực tế gửi vào Gemini"
                    />
                ) : (
                    <Empty
                        title="Chưa có tệp đầu vào Gemini"
                        description="Tệp chỉ xuất hiện sau khi server dựng bằng chứng cho yêu cầu."
                    />
                )
            ) : (
                <>
                    <JsonViewer
                        value={value?.inputs.features || {}}
                        title="46 đặc trưng đã lưu · trước tiền xử lý"
                    />
                    <p className="scope-note">
                        Giá trị float32 đúng thứ tự model; null là thiếu. Không
                        chứa label hoặc nhãn thật.
                    </p>
                </>
            );
    else if (tab === "metadata") content = metadata();
    else if (tab === "error")
        content = (
            <>
                <h2>
                    Trạng thái{" "}
                    {stage === "gemini"
                        ? "Gemini"
                        : stage === "predict"
                          ? "dự đoán"
                          : "giải thích"}
                </h2>
                <Badge
                    status={
                        stage === "gemini"
                            ? detail?.gemini_status
                            : stage === "predict"
                              ? value?.run.status
                              : detail?.status || "not_requested"
                    }
                />
                <p>
                    {stage === "predict"
                        ? value?.run.message || "Chưa ghi nhận thông báo lỗi."
                        : detail?.message ||
                          "Chưa có yêu cầu hoặc chưa ghi nhận thông báo lỗi."}
                </p>
                <p className="scope-note">
                    Chờ xử lý không đồng nghĩa thiếu API key. SHAP vẫn xem được
                    khi Gemini chưa hoàn tất.
                </p>
            </>
        );
    else content = output();
    const second =
        prediction &&
        Object.entries(prediction.probabilities).sort((a, b) => b[1] - a[1])[1];
    return (
        <>
            <PageHeading
                title={`Giải thích dòng ${rowName(index)}`}
                description="Chỉ số dòng bắt đầu từ 0 trong CSV đã upload."
                actions={
                    <Link className="button" scroll={false} href={back}>
                        Về bảng · {rowName(index)}
                    </Link>
                }
            />
            <ErrorNotice error={state.error} retry={state.refresh} />
            <ErrorNotice error={action.error} />
            {!value ? (
                <Loading />
            ) : (
                <div id="sample-outcome" className="sample-head">
                    <div className="sample-data">
                        <div>
                            <small>Nhãn dự đoán</small>
                            <strong>
                                {prediction?.predicted_class || "Chưa có"}
                            </strong>
                        </div>
                        <div>
                            <small>Xác suất đầu ra</small>
                            <strong className="mono">
                                {percent(prediction?.predicted_probability)}
                            </strong>
                        </div>
                        <div>
                            <small>Lớp đứng thứ hai</small>
                            <strong>
                                {second
                                    ? `${second[0]} · ${percent(second[1])}`
                                    : "—"}
                            </strong>
                        </div>
                    </div>
                    {prediction?.alert_id && (
                        <Link
                            className="button"
                            href={`/alerts?${query({ run_id: id, alert: prediction.alert_id, audience })}`}
                        >
                            Mở cảnh báo
                        </Link>
                    )}
                </div>
            )}
            <div className="filters explanation-toolbar">
                <label className="button inline-check">
                    <input
                        id="detail-use-gemini"
                        type="checkbox"
                        checked={useGemini}
                        onChange={(event) => setUseGemini(event.target.checked)}
                    />
                    Dùng Gemini
                </label>
                <button
                    id="explain-one"
                    className="primary"
                    disabled={!prediction || busy}
                    onClick={() => request(false)}
                >
                    {busy
                        ? "Đang xử lý…"
                        : detail?.explanation
                          ? "Yêu cầu / dùng lại kết quả"
                          : "Giải thích mẫu"}
                </button>
                {detail?.explanation && (
                    <button
                        id="retry-gemini"
                        disabled={busy}
                        onClick={() => setConfirmRetry(true)}
                    >
                        Gọi lại Gemini
                    </button>
                )}
            </div>
            <p className="small muted">
                Mẫu được giải thích ở mức Kỹ thuật. Bấm “Giải thích mẫu” để gửi
                yêu cầu.
            </p>
            <div className="trace">
                <nav className="trace-tree" aria-label="Các bước xử lý">
                    <strong>Các bước xử lý</strong>
                    {stages.map((item) => (
                        <button
                            key={item.key}
                            data-stage={item.key}
                            aria-current={
                                stage === item.key ? "step" : undefined
                            }
                            onClick={() => change({ stage: item.key })}
                        >
                            <item.icon className="icon" />
                            {item.title}
                            <small>{item.hint}</small>
                        </button>
                    ))}
                    <SectionOutline
                        key={`${id}:${index}:${stage}:${tab}`}
                        sections={[
                            {
                                id: "stage-content",
                                label: `Bước ${stages.find((item) => item.key === stage)?.title}`,
                            },
                            { id: "case-files", label: "Tệp kết quả" },
                            ...(prediction
                                ? [
                                      {
                                          id: "human-review",
                                          label: "Đánh giá thủ công",
                                      },
                                  ]
                                : []),
                        ]}
                    />
                </nav>
                <section className="trace-content">
                    <Tabs
                        items={tabs}
                        value={tab}
                        onChange={(tab) => change({ tab })}
                        name="Dữ liệu bước xử lý"
                    />
                    <div id="stage-content" role="tabpanel">
                        {value ? content : <Loading />}
                    </div>
                    <CaseFiles
                        key={`${id}:${index}`}
                        files={detail?.files || {}}
                        revision={detail?.updated_at}
                    />
                    {prediction && (
                        <HumanReview
                            key={`review:${id}:${index}`}
                            id={id}
                            row={index}
                            revision={detail?.updated_at}
                        />
                    )}
                </section>
            </div>
            {confirmRetry && (
                <ConfirmDialog
                    title="Gọi lại Gemini?"
                    text="Dùng lại SHAP, lưu lịch sử cũ và tạo yêu cầu Gemini mới ở mức đang chọn. Có thể phát sinh chi phí API."
                    accept="Gọi lại Gemini"
                    onCancel={() => setConfirmRetry(false)}
                    onConfirm={() => request(true)}
                />
            )}
        </>
    );
}
