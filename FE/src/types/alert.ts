import type { ClassName } from "./model";
import type { Prediction } from "./prediction";
import type { ExplanationStatus } from "./explanation";
export type AlertStatus = "new" | "acknowledged" | "closed";
export interface Playbook {
    title: string;
    version: string;
    class_name: ClassName;
    scope_note: string;
    checks: string[];
    response_steps: string[];
    sources: { title: string; url: string }[];
}
export interface AlertInfo {
    id: number;
    run_id: string;
    row_index: number;
    predicted_class: ClassName;
    predicted_probability: number;
    status: AlertStatus;
    note: string;
    created_at: string;
    updated_at: string;
    explanation_status: ExplanationStatus;
    gemini_status: string;
}
export interface AlertDetail extends AlertInfo {
    prediction: Prediction;
    playbook: Playbook;
    history: {
        id: number;
        status: AlertStatus;
        actor: string;
        note: string;
        created_at: string;
    }[];
}
export interface AlertPage {
    items: AlertInfo[];
    total: number;
    offset: number;
    limit: number;
}
export interface AlertOverview {
    total: number;
    new_count: number;
    acknowledged_count: number;
    closed_count: number;
}
