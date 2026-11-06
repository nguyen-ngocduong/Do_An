import type { ClassName } from "./model";
import type { RunInfo } from "./run";
import type { AlertStatus } from "./alert";

export type DashboardPeriod = "today" | "7d" | "30d" | "all";
export interface DashboardRunOption {
    id: string;
    filename: string;
    created_at: string;
}
export interface DashboardDay {
    date: string;
    normal_rows: number;
    suspected_rows: number;
    total_rows: number;
}
export interface DashboardSummary {
    generated_at: string;
    period: DashboardPeriod;
    timezone: string;
    start_date: string | null;
    end_date: string;
    trend_start_date: string;
    trend_end_date: string;
    audience_level: "technical";
    selected_run: DashboardRunOption | null;
    metrics: {
        predicted_rows: number;
        normal_rows: number;
        suspected_rows: number;
        suspected_percentage: number | null;
        pending_alerts: number;
        shap_rows: number;
        run_count: number;
    };
    class_counts: Record<ClassName, number>;
    daily_activity: DashboardDay[];
    alert_counts: Record<AlertStatus, number>;
    explanation_counts: Record<string, number>;
    gemini_counts: Record<string, number>;
    review_counts: Record<
        "not_reviewed" | "agree" | "disagree" | "uncertain",
        number
    >;
    saved_reviews: number;
    proposed_labels: number;
    recent_runs: RunInfo[];
    recent_alerts: {
        id: number;
        run_id: string;
        row_index: number;
        status: AlertStatus;
        created_at: string;
        predicted_class: ClassName;
        predicted_probability: number;
        filename: string;
    }[];
    run_options: DashboardRunOption[];
    available_run_count: number;
}
