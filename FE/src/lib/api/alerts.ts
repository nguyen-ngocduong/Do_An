import { get, query, send } from "./client";
import type {
    AlertDetail,
    AlertOverview,
    AlertPage,
    AlertStatus,
} from "@/types/alert";
import type { Audience } from "@/types/model";
export interface AlertFilters {
    offset?: number;
    run_id?: string;
    status?: string;
    predicted_class?: string;
    audience_level?: Audience;
    limit?: number;
}
export const listAlerts = (filters: AlertFilters, signal: AbortSignal) =>
    get<AlertPage>(
        `/api/alerts?${query({ ...filters, limit: filters.limit ?? 20 })}`,
        signal,
    );
export async function getAlertOverview(
    runId: string,
    predictedClass: string,
    signal: AbortSignal,
): Promise<AlertOverview> {
    const scope = { run_id: runId, predicted_class: predictedClass, limit: 1 };
    const [all, pending, acknowledged, closed] = await Promise.all([
        listAlerts(scope, signal),
        listAlerts({ ...scope, status: "new" }, signal),
        listAlerts({ ...scope, status: "acknowledged" }, signal),
        listAlerts({ ...scope, status: "closed" }, signal),
    ]);
    return {
        total: all.total,
        new_count: pending.total,
        acknowledged_count: acknowledged.total,
        closed_count: closed.total,
    };
}
export const getAlert = (id: number, audience: Audience, signal: AbortSignal) =>
    get<AlertDetail>(`/api/alerts/${id}?audience_level=${audience}`, signal);
export const updateAlert = (
    id: number,
    audience: Audience,
    status: AlertStatus,
    note: string,
) =>
    send<AlertDetail>(`/api/alerts/${id}?audience_level=${audience}`, "PATCH", {
        status,
        note,
    });
