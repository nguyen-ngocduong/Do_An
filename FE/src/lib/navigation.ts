export function audienceValue(value: string | null) {
    return value === "basic" ? ("basic" as const) : ("technical" as const);
}
export function pageOffset(value: string | null) {
    const result = Number(value);
    return Number.isSafeInteger(result) && result >= 0 ? result : 0;
}
export const validRunId = (value: string) => /^[a-f0-9]{32}$/.test(value);
export function safeReturn(value: string | null, fallback: string) {
    if (
        !value ||
        !/^\/(runs\/[a-f0-9]{32}\/predictions|alerts)(\?|$)/.test(value)
    )
        return fallback;
    return value;
}
