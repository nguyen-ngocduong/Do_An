import type { ClassName } from "./model";
export type RunStatus =
    | "queued"
    | "running"
    | "paused"
    | "stopped"
    | "interrupted"
    | "failed"
    | "completed";
export interface RunInfo {
    id: string;
    filename: string;
    mode: "batch" | "replay";
    interval_seconds: number;
    status: RunStatus;
    total_rows: number;
    processed_rows: number;
    created_at: string;
    updated_at: string;
    message: string;
    signature: string;
}
export interface RunList {
    items: RunInfo[];
    total: number;
}
export interface RunDeleted {
    run_id: string;
    files_deleted: boolean;
    message: string;
}
export interface RunSummary {
    run_id: string;
    prediction_status: RunStatus;
    total_rows: number;
    processed_rows: number;
    class_counts: Record<ClassName, number>;
    normal_rows: number;
    suspected_attack_rows: number;
    pending_rows: number;
    explanation_counts: Record<string, number>;
    gemini_counts: Record<string, number>;
    alert_counts: Record<string, number>;
}
