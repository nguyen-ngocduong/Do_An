export class ApiError extends Error {
    constructor(
        public status: number,
        message: string,
    ) {
        super(message);
    }
}
export function query(
    values: Record<string, string | number | boolean | null | undefined>,
) {
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(values)) {
        if (value !== undefined && value !== null && value !== "")
            params.set(key, String(value));
    }
    return params.toString();
}
export function safeApiUrl(path: string) {
    const url = new URL(path, window.location.origin);
    if (
        url.origin !== window.location.origin ||
        !url.pathname.startsWith("/api/")
    )
        throw new Error("Đường dẫn API không thuộc ứng dụng.");
    return url.href;
}
async function response(path: string, options: RequestInit = {}) {
    const result = await fetch(safeApiUrl(path), {
        ...options,
        credentials: "same-origin",
        cache: "no-store",
        signal: options.signal
            ? AbortSignal.any([options.signal, AbortSignal.timeout(30000)])
            : AbortSignal.timeout(30000),
    });
    if (!result.ok) {
        let message = `Yêu cầu chưa hoàn tất (HTTP ${result.status}).`;
        try {
            const body: {
                detail?: unknown;
                errors?: { field: string; message: string }[];
            } = await result.json();
            if (typeof body.detail === "string")
                message =
                    body.detail === "Not Found"
                        ? "Không tìm thấy tài nguyên."
                        : body.detail;
            if (Array.isArray(body.errors))
                message +=
                    " " +
                    body.errors
                        .map((item) => `${item.field}: ${item.message}`)
                        .join("; ");
        } catch {
            /* Dùng mã HTTP khi body không phải JSON. */
        }
        if (result.status === 401 && !path.startsWith("/api/auth/")) {
            message = "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.";
            window.dispatchEvent(new Event("iot:session-expired"));
        }
        throw new ApiError(result.status, message);
    }
    return result;
}
export async function get<T>(path: string, signal?: AbortSignal): Promise<T> {
    return (await response(path, { signal })).json();
}
export async function getText(path: string, signal?: AbortSignal): Promise<string> {
    return (await response(path, { signal })).text();
}
export async function send<T>(
    path: string,
    method: "POST" | "PATCH" | "PUT",
    data: object | FormData,
): Promise<T> {
    const multipart = data instanceof FormData;
    return (
        await response(path, {
            method,
            body: multipart ? data : JSON.stringify(data),
            headers: multipart
                ? undefined
                : { "Content-Type": "application/json" },
        })
    ).json();
}
export async function download(path: string, filename: string) {
    const blob = await (await response(path)).blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
    return blob.size;
}
export async function remove<T>(path: string): Promise<T> {
    return (await response(path, { method: "DELETE" })).json();
}
export function errorText(error: unknown) {
    if (error instanceof TypeError)
        return "Chưa kết nối được tới BE. Kiểm tra server hoặc mạng.";
    if (error instanceof Error && error.name === "TimeoutError")
        return "Server chưa phản hồi trong thời gian chờ.";
    return error instanceof Error
        ? error.message
        : "Không hoàn tất được thao tác.";
}
