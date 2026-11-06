import { ApiError, get, query } from "./client";
import type { DashboardPeriod, DashboardSummary } from "@/types/dashboard";

export async function getDashboard(
    period: DashboardPeriod,
    runId: string,
    signal: AbortSignal,
) {
    try {
        return await get<DashboardSummary>(
            `/api/dashboard?${query({ period, run_id: runId })}`,
            signal,
        );
    } catch (error) {
        if (error instanceof ApiError && error.status === 404 && !runId)
            throw new ApiError(
                404,
                "BE đang chạy chưa có API Tổng quan. Khởi động lại BE để nạp phiên bản 1.7.0 trở lên.",
            );
        throw error;
    }
}
