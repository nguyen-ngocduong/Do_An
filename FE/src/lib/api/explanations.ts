import { ApiError, get, send } from "./client";
import type { Audience } from "@/types/model";
import type {
    ExplanationDetail,
    ExplanationRequest,
    ExplanationState,
} from "@/types/explanation";
export async function getExplanation(
    id: string,
    row: number,
    audience: Audience,
    signal: AbortSignal,
) {
    try {
        return await get<ExplanationDetail>(
            `/api/runs/${id}/explanations/${row}?audience_level=${audience}`,
            signal,
        );
    } catch (error) {
        if (error instanceof ApiError && error.status === 404) return null;
        throw error;
    }
}
export const requestExplanations = (id: string, data: ExplanationRequest) =>
    send<{ items: ExplanationState[] }>(
        `/api/runs/${id}/explanations`,
        "POST",
        data,
    );
export const listExplanations = (
    id: string,
    audience: Audience,
    signal: AbortSignal,
) =>
    get<{ items: ExplanationState[]; total: number }>(
        `/api/runs/${id}/explanations?limit=1000&audience_level=${audience}`,
        signal,
    );
