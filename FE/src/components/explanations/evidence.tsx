"use client";
import { useId, useState } from "react";
import {
    ChevronDown,
    ChevronUp,
    Sparkles,
    ShieldCheck,
    AlertCircle,
    ClipboardList,
} from "lucide-react";
import type { ClassName, Probabilities } from "@/types/model";
import { CLASS_NAMES } from "@/types/model";
import type { ShapExplanation, ExplanationDetail } from "@/types/explanation";
import type { Playbook } from "@/types/alert";
import { number, percent, seconds } from "@/lib/format";
import { Badge, Empty, KeyValues } from "@/components/shared/controls";

export function ProbabilityView({
    values,
    predictedClass,
}: {
    values: Probabilities;
    predictedClass?: ClassName;
}) {
    return (
        <div className="probabilities">
            {CLASS_NAMES.map((name) => (
                <div
                    className="prob-row"
                    key={name}
                    data-predicted={name === predictedClass || undefined}
                >
                    <span>{name}</span>
                    <div className="meter">
                        <span
                            style={{
                                width: `${Math.max(0, Math.min(100, values[name] * 100))}%`,
                            }}
                        />
                    </div>
                    <strong className="mono">{percent(values[name], 4)}</strong>
                </div>
            ))}
        </div>
    );
}
export function ShapView({
    item,
    compact = false,
    tolerance = 1e-5,
}: {
    item: ShapExplanation | null | undefined;
    compact?: boolean;
    tolerance?: number;
}) {
    if (!item)
        return (
            <Empty
                title="Chưa có SHAP"
                description="Chọn mẫu và yêu cầu giải thích để tính bằng chứng."
            />
        );
    if (compact) {
        const features = item.top_features.slice(0, 3);
        const maxImpact = Math.max(
            ...features.map((feature) => Math.abs(feature.shap_value)),
            0,
        );
        return (
            <>
                <div className="peek-shap-header">
                    <strong>Đóng góp SHAP</strong>
                    <span className="muted">
                        Nền: {percent(item.base_probability, 4)}
                    </span>
                </div>
                <div className="shap-peek-list">
                    {features.map((feature) => (
                        <div
                            className="shap-peek-feature"
                            key={feature.feature}
                        >
                            <div className="shap-peek-row">
                                <strong>{feature.feature}</strong>
                                <span
                                    className={`mono ${feature.shap_value < 0 ? "negative" : "positive"}`}
                                >
                                    {feature.shap_value > 0 ? "+" : ""}
                                    {number(feature.shap_value * 100, 2)} điểm %
                                </span>
                            </div>
                            <div className="shap-peek-track" aria-hidden="true">
                                <span
                                    className={
                                        feature.shap_value < 0
                                            ? "negative-bar"
                                            : "positive-bar"
                                    }
                                    style={{
                                        width: `${maxImpact ? (Math.abs(feature.shap_value) / maxImpact) * 100 : 0}%`,
                                    }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
                <p className="small muted">
                    Tăng/giảm xác suất lớp {item.explained_class} (điểm %).
                    Thanh so với đóng góp lớn nhất trong top 3. Còn 43 đặc trưng
                    khác trong tổng.
                </p>
            </>
        );
    }
    const steps = item.top_features.map((feature) => ({
        name: feature.feature,
        value: feature.value,
        missing: feature.missing,
        impact: feature.shap_value,
    }));
    steps.push({
        name: "41 đặc trưng còn lại",
        value: null,
        missing: false,
        impact: item.other_features_shap_sum,
    });
    let cumulative = item.base_probability;
    const bars = [];
    for (const step of steps) {
        const start = cumulative;
        cumulative += step.impact;
        bars.push({ ...step, start, end: cumulative });
    }
    const min = Math.min(
        0,
        item.base_probability,
        ...bars.map((bar) => Math.min(bar.start, bar.end)),
    );
    const max = Math.max(
        1,
        item.predicted_probability,
        ...bars.map((bar) => Math.max(bar.start, bar.end)),
    );
    const range = max - min;
    const passed = item.max_additivity_error_all_classes <= tolerance;
    return (
        <>
            <div className="section-heading">
                <h2>SHAP trên đặc trưng gốc</h2>
                <span className={`badge ${passed ? "success" : "danger"}`}>
                    {passed ? "Bảo toàn đạt" : "Bảo toàn không đạt"}
                </span>
            </div>
            <p className="muted">
                PermutationExplainer · Toàn pipeline · 46 đặc trưng · lớp{" "}
                {item.explained_class}
            </p>
            <div className="shap-legend">
                Đóng góp dương tăng đầu ra; đóng góp âm giảm đầu ra (điểm phần
                trăm).
            </div>
            <div className="waterfall-stepped">
                {bars.map((bar) => (
                    <div className="waterfall-row" key={bar.name}>
                        <div className="waterfall-label">
                            <strong>{bar.name}</strong>
                            {bar.name !== "41 đặc trưng còn lại" && (
                                <small className="muted mono">
                                    Giá trị:{" "}
                                    {bar.missing
                                        ? "Thiếu"
                                        : number(bar.value, 4)}
                                </small>
                            )}
                        </div>
                        <div className="waterfall-track">
                            <span
                                className={`waterfall-bar ${bar.impact < 0 ? "negative-bar" : "positive-bar"}`}
                                style={{
                                    left: `${((Math.min(bar.start, bar.end) - min) / range) * 100}%`,
                                    width: `${(Math.abs(bar.impact) / range) * 100}%`,
                                }}
                            />
                        </div>
                        <span
                            className={`mono ${bar.impact < 0 ? "negative" : "positive"}`}
                        >
                            {bar.impact > 0 ? "+" : ""}
                            {number(bar.impact * 100, 2)}
                        </span>
                    </div>
                ))}
            </div>
            <KeyValues
                values={[
                    ["Xác suất nền", percent(item.base_probability, 6)],
                    [
                        "Tổng SHAP (46 đặc trưng)",
                        `${number(item.shap_sum * 100, 6)} điểm %`,
                    ],
                    [
                        "41 đặc trưng ngoài top 5",
                        `${number(item.other_features_shap_sum * 100, 6)} điểm %`,
                    ],
                    ["Xác suất đầu ra", percent(item.predicted_probability, 6)],
                    [
                        "Sai số bảo toàn lớn nhất",
                        item.max_additivity_error_all_classes.toExponential(3),
                    ],
                    ["Thời gian SHAP ghi nhận", seconds(item.shap_seconds)],
                ]}
            />
            <p className="scope-note">
                SHAP giải thích đầu ra mô hình so với nền tham chiếu; chưa chứng
                minh nguyên nhân hoặc xác nhận tấn công.
            </p>
        </>
    );
}
export function GeminiView({
    detail,
    compact = false,
}: {
    detail: ExplanationDetail | null | undefined;
    compact?: boolean;
}) {
    const result = detail?.gemini;
    if (!result)
        return (
            <div className="notice">
                <Badge status={detail?.gemini_status || "not_requested"} />
                <p>
                    {detail?.message ||
                        "Chưa có diễn giải cho mẫu ở mức đang chọn. Chỉ gọi Gemini khi bạn gửi yêu cầu."}
                </p>
            </div>
        );
    if (compact)
        return (
            <GeminiPreview
                key={`${detail.run_id}:${detail.row_index}:${detail.audience_level}`}
                detail={detail}
            />
        );
    const accepted = detail.gemini_status === "accepted";
    return (
        <article
            className="reading gemini-report"
            aria-label="Diễn giải chi tiết Gemini"
        >
            <header className="gemini-report-header">
                <div>
                    <Sparkles className="icon" aria-hidden="true" />
                    <h2>Diễn giải Gemini</h2>
                </div>
                <span className="badge">
                    {detail.audience_level === "basic" ? "Dễ hiểu" : "Kỹ thuật"}
                </span>
            </header>
            <div
                className={`gemini-report-status ${accepted ? "accepted" : "draft"}`}
            >
                {accepted ? (
                    <ShieldCheck className="icon" aria-hidden="true" />
                ) : (
                    <AlertCircle className="icon" aria-hidden="true" />
                )}
                <div>
                    <strong>
                        {accepted
                            ? "Đạt kiểm tra tự động · Chưa được chuyên gia đánh giá"
                            : "BẢN NHÁP CẦN SỬA · Chưa đạt kiểm tra"}
                    </strong>
                    {detail.message && (
                        <details className="gemini-check-detail">
                            <summary>Thông tin kiểm tra</summary>
                            <p>{detail.message}</p>
                        </details>
                    )}
                </div>
            </div>
            <div className="gemini-report-layout">
                <div className="gemini-report-main">
                    <section className="gemini-summary-section">
                        <h3>Nhận định chung</h3>
                        <p>{result.tom_tat}</p>
                    </section>
                    <section className="gemini-evidence-section">
                        <h3>So sánh hai lớp đứng đầu</h3>
                        <p>{result.so_sanh_hai_lop.dien_giai}</p>
                        <h3>Tổng hợp bằng chứng SHAP</h3>
                        <p>{result.tong_hop_shap.dien_giai}</p>
                    </section>
                    <section className="gemini-features-section">
                        <h3>Giải thích từng đặc trưng</h3>
                        <dl className="gemini-features">
                            {result.giai_thich_dac_trung.map((feature) => (
                                <div key={feature.ten_dac_trung}>
                                    <dt>
                                        <code>{feature.ten_dac_trung}</code>
                                    </dt>
                                    <dd>{feature.dien_giai}</dd>
                                </div>
                            ))}
                        </dl>
                    </section>
                    <section className="gemini-limits">
                        <h3>Giới hạn của diễn giải</h3>
                        <ul>
                            {result.gioi_han.map((text) => (
                                <li key={text}>{text}</li>
                            ))}
                        </ul>
                    </section>
                </div>
                <aside
                    className="gemini-report-guidance"
                    aria-label="Gợi ý kiểm tra từ Gemini"
                >
                    <div className="gemini-guidance-title">
                        <ClipboardList className="icon" aria-hidden="true" />
                        <h3>Gợi ý kiểm tra có điều kiện</h3>
                    </div>
                    {result.de_xuat_kiem_tra.map((suggestion, index) => (
                        <section key={index}>
                            <h4>{suggestion.nguon_du_lieu}</h4>
                            <p>{suggestion.noi_dung_can_kiem_tra}</p>
                            <p className="gemini-check-purpose">
                                <strong>Mục đích:</strong> {suggestion.muc_dich}
                            </p>
                        </section>
                    ))}
                </aside>
            </div>
        </article>
    );
}

function GeminiPreview({ detail }: { detail: ExplanationDetail }) {
    const [expanded, setExpanded] = useState(false);
    const contentId = useId();
    return (
        <section className="gemini-preview" aria-label="Tóm tắt Gemini">
            <div id={contentId}>
                {expanded ? (
                    <GeminiView detail={detail} />
                ) : (
                    <>
                        <Badge status={detail.gemini_status} />
                        <h3>Diễn giải Gemini</h3>
                        <p className="gemini-preview-summary">
                            {detail.gemini?.tom_tat}
                        </p>
                        <p className="small muted">
                            {detail.gemini_status === "accepted"
                                ? "Đạt kiểm tra tự động; chưa được chuyên gia đánh giá."
                                : "Bản nháp cần kiểm tra và chỉnh sửa."}
                        </p>
                    </>
                )}
            </div>
            <button
                className="gemini-more"
                aria-expanded={expanded}
                aria-controls={contentId}
                onClick={() => setExpanded(!expanded)}
            >
                {expanded ? "Thu gọn" : "Xem thêm"}
                {expanded ? (
                    <ChevronUp className="icon" aria-hidden="true" />
                ) : (
                    <ChevronDown className="icon" aria-hidden="true" />
                )}
            </button>
        </section>
    );
}
export function PlaybookView({
    value,
}: {
    value: Playbook | null | undefined;
}) {
    if (!value) return null;
    return (
        <section className="reading">
            <h2>{value.title}</h2>
            <p className="scope-note">{value.scope_note}</p>
            <h3>Cần kiểm tra</h3>
            <ul>
                {value.checks.map((text) => (
                    <li key={text}>{text}</li>
                ))}
            </ul>
            <h3>Hướng xử lý tham khảo</h3>
            <ol>
                {value.response_steps.map((text) => (
                    <li key={text}>{text}</li>
                ))}
            </ol>
            <p className="small muted">
                Phiên bản {value.version} · Không thực thi thao tác mạng tự
                động.
            </p>
            <div className="source-links">
                {value.sources.map((source) =>
                    /^https?:\/\//.test(source.url) ? (
                        <a
                            key={source.url}
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            {source.title} ↗{" "}
                        </a>
                    ) : (
                        <span key={source.url}>{source.title}</span>
                    ),
                )}
            </div>
        </section>
    );
}
