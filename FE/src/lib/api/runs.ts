import { ApiError, get, query, remove, send } from "./client";
import type { RunDeleted, RunInfo, RunList, RunSummary } from "@/types/run";
import type { Audience } from "@/types/model";
export const listRuns = (offset: number, signal: AbortSignal) =>
    get<RunList>(`/api/runs?${query({ offset, limit: 20 })}`, signal);
export const getRun = (id: string, signal?: AbortSignal) =>
    get<RunInfo>(`/api/runs/${id}`, signal);
export const getSummary = (
    id: string,
    signal: AbortSignal,
    audience: Audience = "technical",
) =>
    get<RunSummary>(
        `/api/runs/${id}/summary?audience_level=${audience}`,
        signal,
    );
export const createRun = (data: FormData) =>
    send<RunInfo>("/api/runs", "POST", data);
export const controlRun = (id: string, action: "pause" | "resume" | "stop") =>
    send<RunInfo>(`/api/runs/${id}/control`, "POST", { action });
export async function deleteRun(id: string) {
    try {
        return await remove<RunDeleted>(`/api/runs/${id}`);
    } catch (error) {
        if (error instanceof ApiError && error.status === 405)
            throw new ApiError(
                405,
                "Server đang chạy chưa hỗ trợ xóa lịch sử. Khởi động lại BE để nạp phiên bản mới.",
            );
        throw error;
    }
}
