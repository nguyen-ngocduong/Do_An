import type { ClassName, Probabilities } from "./model";
import type { ExplanationStatus } from "./explanation";
import type { AlertStatus } from "./alert";
export interface Prediction {
    run_id: string;
    row_index: number;
    predicted_class: ClassName;
    predicted_probability: number;
    probabilities: Probabilities;
    predict_seconds: number;
    created_at: string;
    explanation_status: ExplanationStatus;
    gemini_status: string;
    alert_id: number | null;
    alert_status: AlertStatus | null;
}
export interface PredictionPage {
    items: Prediction[];
    total: number;
    total_predicted: number;
    offset: number;
    limit: number;
}
export interface InputRow {
    run_id: string;
    row_index: number;
    features: Record<string, number | null>;
}
