import type { Audience, ClassName, Probabilities } from "./model";
import type { Playbook } from "./alert";
export type ExplanationStatus =
    | "not_requested"
    | "queued"
    | "shap_running"
    | "gemini_running"
    | "completed"
    | "partial"
    | "failed"
    | "interrupted";
export interface ShapFeature {
    rank: number;
    feature: string;
    value: number | null;
    missing: boolean;
    shap_value: number;
    impact_percentage_points: number;
    direction: string;
}
export interface ShapExplanation {
    input_row_index: number;
    predicted_class: ClassName;
    explained_class: ClassName;
    predicted_probability: number;
    probabilities: Probabilities;
    top_features: ShapFeature[];
    base_probability: number;
    shap_sum: number;
    other_features_shap_sum: number;
    max_additivity_error_all_classes: number;
    shap_seconds: number;
    seed: number;
}
export interface GeminiExplanation {
    tom_tat: string;
    so_sanh_hai_lop: { dien_giai: string };
    tong_hop_shap: { dien_giai: string };
    giai_thich_dac_trung: { ten_dac_trung: string; dien_giai: string }[];
    de_xuat_kiem_tra: {
        nguon_du_lieu: string;
        noi_dung_can_kiem_tra: string;
        muc_dich: string;
    }[];
    gioi_han: string[];
}
export interface ExplanationState {
    run_id: string;
    row_index: number;
    status: ExplanationStatus;
    use_gemini: boolean;
    gemini_status: string;
    message: string;
    updated_at: string;
    audience_level: Audience;
}
export interface ExplanationDetail extends ExplanationState {
    explanation: ShapExplanation | null;
    gemini: GeminiExplanation | null;
    files: Record<string, string>;
    playbook: Playbook | null;
}
export interface ExplanationRequest {
    row_indices: number[];
    use_gemini: boolean;
    retry_gemini: boolean;
    audience_level: Audience;
}
export interface Execution {
    shap_seconds: number;
    api_seconds: number;
    total_tokens: number | null;
}
export interface GeminiStatus {
    selected_attempt: number | null;
    attempts_saved: number;
    status: string;
    message: string;
}
export const ACTIVE_CASES: ExplanationStatus[] = [
    "queued",
    "shap_running",
    "gemini_running",
];
