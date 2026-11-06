export const CLASS_NAMES = [
    "Normal",
    "BruteForce",
    "DDoS",
    "DoS",
    "Mirai",
    "Recon",
    "Spoofing",
    "Web-Based",
] as const;
export type ClassName = (typeof CLASS_NAMES)[number];
export type Audience = "basic" | "technical";
export type Probabilities = Record<ClassName, number>;
export interface ModelInfo {
    model_id: string;
    model_load_count: number;
    gemini_configured: boolean;
    gemini_model: string;
    threads: number;
    checks: { bundle_sha256: string; versions: Record<string, string> };
    limits: {
        csv_rows: number;
        upload_bytes: number;
        explanation_rows: number;
    };
    shap_config: {
        background_size: number;
        max_evals: number;
        additivity_tolerance: number;
    };
}
export interface InputSchema {
    feature_names: string[];
    class_names: ClassName[];
}
