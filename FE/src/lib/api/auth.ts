import { ApiError, get, send } from "./client";

export interface SessionInfo {
    username: string;
    expires_at: number | null;
}

export const getSession = (signal?: AbortSignal) =>
    get<SessionInfo>("/api/auth/session", signal);

export async function login(username: string, password: string, remember = false) {
    try {
        return await send<SessionInfo>("/api/auth/login", "POST", { username, password, remember });
    } catch (error) {
        if (
            error instanceof ApiError && error.status === 422 &&
            error.message.includes("body.remember: Yêu cầu có trường không được hỗ trợ.")
        )
            throw new ApiError(
                error.status,
                "BE chưa hỗ trợ Ghi nhớ phiên. Khởi động lại BE để cập nhật.",
            );
        if (error instanceof ApiError && [404, 405].includes(error.status))
            throw new ApiError(
                error.status,
                "Chưa tìm thấy API đăng nhập. Khởi động lại BE ở terminal đang chạy rồi thử lại.",
            );
        throw error;
    }
}

export const logout = () =>
    send<{ message: string }>("/api/auth/logout", "POST", {});

export function safeReturnTo(value: string | null) {
    if (!value || !value.startsWith("/") || value.startsWith("//") || /[\\\r\n]/.test(value))
        return "/dashboard";
    const url = new URL(value, "http://sentinel.local");
    if (
        url.origin !== "http://sentinel.local" ||
        !(url.pathname === "/dashboard" || url.pathname === "/runs" || url.pathname.startsWith("/runs/") || url.pathname === "/alerts")
    )
        return "/dashboard";
    return url.pathname + url.search;
}

export const loginUrl = (next: string) =>
    `/login?${new URLSearchParams({ next: safeReturnTo(next) })}`;
