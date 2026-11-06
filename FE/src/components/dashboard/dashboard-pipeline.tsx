"use client";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { number, statusLabel } from "@/lib/format";
import type { DashboardSummary } from "@/types/dashboard";

export function DashboardPipeline({ data }: { data: DashboardSummary }) {
    const total = data.metrics.predicted_rows;
    const shapRows = data.metrics.shap_rows;
    const geminiAccepted = data.gemini_counts.accepted || 0;
    const savedReviews = data.saved_reviews || 0;

    const shapPercent = total > 0 ? Math.min(100, (shapRows / total) * 100) : 0;
    const geminiPercent =
        total > 0 ? Math.min(100, (geminiAccepted / total) * 100) : 0;
    const reviewPercent =
        total > 0 ? Math.min(100, (savedReviews / total) * 100) : 0;

    const targetRun = data.selected_run || data.recent_runs[0] || null;
    const targetRunLabel = data.selected_run
        ? "Xem lần chạy đã chọn"
        : data.recent_runs.length > 0
          ? "Xem lần chạy gần nhất"
          : null;

    const explanations = data.explanation_counts;
    const active =
        (explanations.queued || 0) +
        (explanations.shap_running || 0) +
        (explanations.gemini_running || 0);
    const problem =
        (explanations.partial || 0) +
        (explanations.failed || 0) +
        (explanations.interrupted || 0);
    const gemini = Object.entries(data.gemini_counts).filter(
        ([, count]) => count > 0,
    );
    const reviews = data.review_counts;

    return (
        <section
            className="panel dashboard-pipeline"
            aria-labelledby="dashboard-pipeline-title"
        >
            <div className="dashboard-card-heading">
                <div>
                    <h2 id="dashboard-pipeline-title">
                        Giải thích và đánh giá
                    </h2>
                    <p>
                        Từ bằng chứng đến diễn giải, rồi đến nhận xét của bạn.
                    </p>
                </div>
                {targetRun && targetRunLabel && (
                    <Link
                        href={`/runs/${targetRun.id}/predictions`}
                        className="pipeline-run-link"
                    >
                        {targetRunLabel}
                        <ArrowUpRight className="icon" aria-hidden="true" />
                    </Link>
                )}
            </div>

            <div className="dashboard-pipeline-columns">
                <section className="dashboard-pipeline-card">
                    <h3>Bằng chứng SHAP</h3>
                    <p className="pipeline-desc">
                        Xem những đặc trưng đã ảnh hưởng đến kết quả dự đoán.
                    </p>
                    <div className="pipeline-stat">
                        <span>Đã có bằng chứng</span>
                        <strong>
                            {number(shapRows)} / {number(total)}
                        </strong>
                    </div>
                    <div
                        className="meter pipeline-meter"
                        role="progressbar"
                        aria-label={`Bằng chứng SHAP: ${number(shapRows)} trên ${number(total)} mẫu`}
                        aria-valuetext={`${number(shapRows)} / ${number(total)} mẫu`}
                        aria-valuenow={shapPercent}
                        aria-valuemin={0}
                        aria-valuemax={100}
                    >
                        <span style={{ width: `${shapPercent}%` }} />
                    </div>
                </section>

                <section className="dashboard-pipeline-card">
                    <h3>Diễn giải Gemini</h3>
                    <p className="pipeline-desc">
                        Đọc phần diễn giải bằng tiếng Việt từ bằng chứng SHAP.
                    </p>
                    <div className="pipeline-stat">
                        <span>Đạt kiểm tra tự động</span>
                        <strong>
                            {number(geminiAccepted)} / {number(total)}
                        </strong>
                    </div>
                    <div
                        className="meter pipeline-meter"
                        role="progressbar"
                        aria-label={`Diễn giải Gemini: ${number(geminiAccepted)} trên ${number(total)} mẫu`}
                        aria-valuetext={`${number(geminiAccepted)} / ${number(total)} mẫu`}
                        aria-valuenow={geminiPercent}
                        aria-valuemin={0}
                        aria-valuemax={100}
                    >
                        <span style={{ width: `${geminiPercent}%` }} />
                    </div>
                </section>

                <section className="dashboard-pipeline-card">
                    <h3>Đánh giá của bạn</h3>
                    <p className="pipeline-desc">
                        Lưu nhận xét của bạn sau khi đối chiếu kết quả và bằng
                        chứng.
                    </p>
                    <div className="pipeline-stat">
                        <span>Phiếu đã lưu</span>
                        <strong>
                            {number(savedReviews)} / {number(total)}
                        </strong>
                    </div>
                    <div
                        className="meter pipeline-meter"
                        role="progressbar"
                        aria-label={`Đánh giá của bạn: ${number(savedReviews)} trên ${number(total)} mẫu`}
                        aria-valuetext={`${number(savedReviews)} / ${number(total)} mẫu`}
                        aria-valuenow={reviewPercent}
                        aria-valuemin={0}
                        aria-valuemax={100}
                    >
                        <span style={{ width: `${reviewPercent}%` }} />
                    </div>
                </section>
            </div>

            <details className="dashboard-pipeline-details">
                <summary>Xem chi tiết tất cả trạng thái</summary>
                <div className="dashboard-pipeline-details-grid">
                    <div>
                        <h4>Tác vụ giải thích</h4>
                        <dl>
                            <div>
                                <dt>Chưa yêu cầu</dt>
                                <dd>
                                    {number(explanations.not_requested || 0)}
                                </dd>
                            </div>
                            <div>
                                <dt>Đang chờ / xử lý</dt>
                                <dd>{number(active)}</dd>
                            </div>
                            <div>
                                <dt>Hoàn tất</dt>
                                <dd>{number(explanations.completed || 0)}</dd>
                            </div>
                            <div>
                                <dt>Một phần / lỗi / gián đoạn</dt>
                                <dd>{number(problem)}</dd>
                            </div>
                        </dl>
                    </div>
                    <div>
                        <h4>Diễn giải Gemini</h4>
                        <dl>
                            {(gemini.length
                                ? gemini
                                : [["not_requested", 0] as const]
                            ).map(([status, count]) => (
                                <div key={status}>
                                    <dt>{statusLabel(status)}</dt>
                                    <dd>{number(count)}</dd>
                                </div>
                            ))}
                        </dl>
                        <p className="small muted">
                            Đạt kiểm tra tự động chưa phải đánh giá của chuyên
                            gia.
                        </p>
                    </div>
                    <div>
                        <h4>Đánh giá thủ công</h4>
                        <dl>
                            <div>
                                <dt>Chưa đánh giá dự đoán</dt>
                                <dd>{number(reviews.not_reviewed || 0)}</dd>
                            </div>
                            <div>
                                <dt>Đồng ý / Không đồng ý</dt>
                                <dd>
                                    {number(reviews.agree || 0)} /{" "}
                                    {number(reviews.disagree || 0)}
                                </dd>
                            </div>
                            <div>
                                <dt>Chưa chắc</dt>
                                <dd>{number(reviews.uncertain || 0)}</dd>
                            </div>
                            <div>
                                <dt>Đề xuất nhãn khác</dt>
                                <dd>{number(data.proposed_labels || 0)}</dd>
                            </div>
                        </dl>
                    </div>
                </div>
            </details>

            <p className="scope-note">
                Kết quả AI cần người dùng kiểm tra. Phiếu đánh giá không tự xác
                nhận nhãn thực tế.
            </p>
        </section>
    );
}
