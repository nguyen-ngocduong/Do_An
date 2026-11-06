import { get, send } from "./client";
import type { ClassName } from "@/types/model";

export interface ReviewDraft {
    reviewer_name: string;
    prediction_assessment: "not_reviewed" | "agree" | "disagree" | "uncertain";
    proposed_label: ClassName | null;
    explanation_clarity: number | null;
    evidence_faithfulness: number | null;
    actionability: number | null;
    notes: string;
}
export interface ReviewContext {
    run_id: string;
    row_index: number;
    audience_level: "technical";
    predicted_class: ClassName;
    predicted_probability: number;
    evidence_signature: string;
    file_sha256: Record<string, string>;
}
export interface ReviewEnvelope {
    context: ReviewContext;
    review:
        | (ReviewDraft & {
              reviewer_username: string;
              updated_at: string;
              evidence_signature: string;
          })
        | null;
    stale: boolean;
}
export const reviewPath = (id: string, row: number) =>
    `/api/runs/${id}/human-reviews/${row}`;
export const getReview = (id: string, row: number, signal: AbortSignal) =>
    get<ReviewEnvelope>(reviewPath(id, row), signal);
export const saveReview = (
    id: string,
    row: number,
    draft: ReviewDraft,
    signature: string,
) =>
    send<ReviewEnvelope>(reviewPath(id, row), "PUT", {
        ...draft,
        evidence_signature: signature,
    });
