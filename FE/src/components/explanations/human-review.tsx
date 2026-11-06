"use client";
import { useEffect, useState } from "react";
import { ClipboardCheck } from "lucide-react";
import { CLASS_NAMES, type ClassName } from "@/types/model";
import {
    getReview,
    reviewPath,
    saveReview,
    type ReviewDraft,
    type ReviewEnvelope,
} from "@/lib/api/reviews";
import { useAction } from "@/lib/use-action";
import { time } from "@/lib/format";
import {
    ConfirmDialog,
    DownloadButton,
    ErrorNotice,
    Loading,
} from "@/components/shared/controls";

const EMPTY: ReviewDraft = {
    reviewer_name: "",
    prediction_assessment: "not_reviewed",
    proposed_label: null,
    explanation_clarity: null,
    evidence_faithfulness: null,
    actionability: null,
    notes: "",
};
const RATINGS = [
    ["explanation_clarity", "Độ rõ ràng của diễn giải"],
    ["evidence_faithfulness", "Mức bám sát bằng chứng SHAP"],
    ["actionability", "Tính hữu ích của gợi ý kiểm tra"],
] as const;

export function HumanReview({
    id,
    row,
    revision,
}: {
    id: string;
    row: number;
    revision?: string;
}) {
    const [envelope, setEnvelope] = useState<ReviewEnvelope | null>(null);
    const [draft, setDraft] = useState<ReviewDraft>(EMPTY);
    const [dirty, setDirty] = useState(false);
    const [confirmed, setConfirmed] = useState(false);
    const [loadError, setLoadError] = useState<unknown>();
    const [loading, setLoading] = useState(true);
    const [reload, setReload] = useState(0);
    const [confirmReload, setConfirmReload] = useState(false);
    const action = useAction();
    useEffect(() => {
        if (dirty) return;
        const controller = new AbortController();
        let active = true;
        getReview(id, row, controller.signal)
            .then((value) => {
                if (!active) return;
                setEnvelope(value);
                setLoading(false);
                setLoadError(undefined);
                // Chỉ giữ các trường người dùng được phép sửa, không gửi lại metadata.
                const next = { ...EMPTY };
                if (value.review) {
                    for (const key of Object.keys(
                        EMPTY,
                    ) as (keyof ReviewDraft)[]) {
                        Object.assign(next, { [key]: value.review[key] });
                    }
                }
                setDraft(next);
                setDirty(false);
                setConfirmed(false);
            })
            .catch((error) => {
                if (active) {
                    setLoadError(error);
                    setLoading(false);
                }
            });
        return () => {
            active = false;
            controller.abort();
        };
    }, [id, row, revision, reload, dirty]);
    function update(values: Partial<ReviewDraft>) {
        setDraft((current) => ({ ...current, ...values }));
        setDirty(true);
        setConfirmed(false);
    }
    function reloadReview() {
        setLoadError(undefined);
        setLoading(true);
        setConfirmed(false);
        setDirty(false);
        setReload((value) => value + 1);
    }
    return (
        <section
            id="human-review"
            data-evidence-signature={envelope?.context.evidence_signature}
            className="human-review"
            aria-labelledby="human-review-title"
        >
            <div className="section-heading">
                <h2 id="human-review-title">
                    <ClipboardCheck className="icon" aria-hidden="true" />
                    Đánh giá thủ công (Human review)
                </h2>
                <button
                    type="button"
                    disabled={action.pending || loading}
                    onClick={() =>
                        dirty ? setConfirmReload(true) : reloadReview()
                    }
                >
                    Tải lại bản đã lưu
                </button>
            </div>
            <p className="muted">
                Đánh giá dự đoán, đối chiếu SHAP và nhận xét diễn giải Gemini.
                Không đủ căn cứ thì chọn Chưa chắc; điểm để trống nghĩa là chưa
                đánh giá.
            </p>
            <ErrorNotice error={loadError || action.error} />
            {Boolean(loadError) && (
                <p className="small muted">
                    Cần BE phiên bản 1.5.0 trở lên để lưu đánh giá. Không lưu
                    hoặc tự gửi lại khi tải dữ liệu thất bại.
                </p>
            )}
            {!envelope ? (
                !loadError && <Loading />
            ) : (
                <>
                    <div className="review-status" role="status">
                        {envelope.review
                            ? `Đã lưu bởi ${envelope.review.reviewer_username} · ${time(envelope.review.updated_at)}`
                            : "Chưa có bản đánh giá đã lưu."}
                        {dirty && " Có thay đổi chưa lưu."}
                    </div>
                    {envelope.stale && (
                        <p className="notice warning">
                            Bản đã lưu dựa trên bằng chứng cũ. Cần đối chiếu lại
                            kết quả hiện tại trước khi lưu mới.
                        </p>
                    )}
                    <form
                        id="human-review-form"
                        onSubmit={(event) => {
                            event.preventDefault();
                            if (!confirmed || loadError) return;
                            void action.run(
                                () =>
                                    saveReview(
                                        id,
                                        row,
                                        draft,
                                        envelope.context.evidence_signature,
                                    ),
                                (value) => {
                                    setEnvelope(value);
                                    setDirty(false);
                                    setConfirmed(false);
                                },
                            );
                        }}
                    >
                        <fieldset
                            disabled={
                                action.pending || loading || Boolean(loadError)
                            }
                        >
                            <div className="review-fields">
                                <label className="field">
                                    Tên người đánh giá
                                    <input
                                        id="reviewer-name"
                                        required
                                        maxLength={128}
                                        value={draft.reviewer_name}
                                        onChange={(event) =>
                                            update({
                                                reviewer_name:
                                                    event.target.value,
                                            })
                                        }
                                    />
                                </label>
                                <label className="field">
                                    Nhận định về nhãn dự đoán
                                    <select
                                        id="review-decision"
                                        value={draft.prediction_assessment}
                                        onChange={(event) =>
                                            update({
                                                prediction_assessment: event
                                                    .target
                                                    .value as ReviewDraft["prediction_assessment"],
                                                proposed_label: null,
                                            })
                                        }
                                    >
                                        <option value="not_reviewed">
                                            Chưa đánh giá
                                        </option>
                                        <option value="agree">
                                            Đồng ý với dự đoán
                                        </option>
                                        <option value="disagree">
                                            Không đồng ý với dự đoán
                                        </option>
                                        <option value="uncertain">
                                            Chưa chắc / thiếu bằng chứng
                                        </option>
                                    </select>
                                </label>
                                {draft.prediction_assessment === "disagree" && (
                                    <label className="field">
                                        Nhãn đề xuất (tùy chọn)
                                        <select
                                            id="review-label"
                                            value={draft.proposed_label || ""}
                                            onChange={(event) =>
                                                update({
                                                    proposed_label:
                                                        (event.target
                                                            .value as ClassName) ||
                                                        null,
                                                })
                                            }
                                        >
                                            <option value="">
                                                Chưa đề xuất nhãn
                                            </option>
                                            {CLASS_NAMES.filter(
                                                (name) =>
                                                    name !==
                                                    envelope.context
                                                        .predicted_class,
                                            ).map((name) => (
                                                <option key={name}>
                                                    {name}
                                                </option>
                                            ))}
                                        </select>
                                    </label>
                                )}
                            </div>
                            <div className="review-ratings">
                                {RATINGS.map(([key, label]) => (
                                    <label className="field" key={key}>
                                        {label}
                                        <select
                                            data-review-rating={key}
                                            value={draft[key] ?? ""}
                                            onChange={(event) =>
                                                update({
                                                    [key]: event.target.value
                                                        ? Number(
                                                              event.target
                                                                  .value,
                                                          )
                                                        : null,
                                                })
                                            }
                                        >
                                            <option value="">
                                                Chưa đánh giá
                                            </option>
                                            {[1, 2, 3, 4, 5].map((score) => (
                                                <option
                                                    key={score}
                                                    value={score}
                                                >
                                                    {score} / 5
                                                </option>
                                            ))}
                                        </select>
                                    </label>
                                ))}
                            </div>
                            <p className="small muted">
                                1: rất thấp · 2: thấp · 3: trung bình · 4: tốt ·
                                5: rất tốt. Chỉ chấm nội dung đã đọc và đủ cơ sở
                                nhận xét.
                            </p>
                            <label className="field">
                                Nhận xét và bằng chứng đối chiếu
                                <textarea
                                    id="review-notes"
                                    rows={4}
                                    maxLength={4000}
                                    value={draft.notes}
                                    onChange={(event) =>
                                        update({ notes: event.target.value })
                                    }
                                    placeholder="Nêu đặc trưng, nội dung diễn giải hoặc nhật ký bạn đã đối chiếu…"
                                />
                            </label>
                            <label className="review-confirm">
                                <input
                                    id="review-confirm"
                                    type="checkbox"
                                    checked={confirmed}
                                    onChange={(event) =>
                                        setConfirmed(event.target.checked)
                                    }
                                />
                                Tôi đã đối chiếu các nội dung được chấm với bằng
                                chứng hiện tại.
                            </label>
                            <button
                                id="save-human-review"
                                className="primary"
                                type="submit"
                                disabled={!confirmed || action.pending}
                            >
                                {action.pending ? "Đang lưu…" : "Lưu đánh giá"}
                            </button>
                        </fieldset>
                    </form>
                    {envelope.review && (
                        <div className="review-download">
                            <DownloadButton
                                path={reviewPath(id, row) + "/export"}
                                name={`human_review_row_${row}_technical.json`}
                            >
                                Tải bản đánh giá đã lưu (JSON)
                            </DownloadButton>
                        </div>
                    )}
                    <p className="scope-note">
                        Lưu riêng trong database, không đổi nhãn model hay trạng
                        thái cảnh báo. Tên người đánh giá do người dùng nhập; hệ
                        thống không xác minh tư cách chuyên gia. Đây không phải
                        nhãn thật đã được kiểm chứng độc lập.
                    </p>
                </>
            )}
            {confirmReload && (
                <ConfirmDialog
                    title="Tải lại bản đã lưu?"
                    text="Các thay đổi đánh giá chưa lưu sẽ được bỏ để đọc bản trên server."
                    accept="Tải lại"
                    onCancel={() => setConfirmReload(false)}
                    onConfirm={() => {
                        setConfirmReload(false);
                        reloadReview();
                    }}
                />
            )}
        </section>
    );
}
