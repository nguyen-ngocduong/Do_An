import { get, query } from "./client";
import type { PredictionPage, InputRow } from "@/types/prediction";
import type { Audience } from "@/types/model";
export interface PredictionFilters {
    offset?: number;
    limit?: number;
    predicted_class?: string;
    explanation_status?: string;
    audience_level?: Audience;
}
export const getPredictions = (
    id: string,
    filters: PredictionFilters,
    signal: AbortSignal,
) =>
    get<PredictionPage>(
        `/api/runs/${id}/predictions?${query({ ...filters })}`,
        signal,
    );
export const getInput = (id: string, row: number, signal: AbortSignal) =>
    get<InputRow>(`/api/runs/${id}/inputs/${row}`, signal);
