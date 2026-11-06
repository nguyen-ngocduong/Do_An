import { afterEach, expect, it, vi } from "vitest";
import { login, safeReturnTo } from "./auth";
import { GET } from "@/app/login/redirect/route";

afterEach(() => vi.unstubAllGlobals());

it("chỉ quay về route trong ứng dụng sau đăng nhập", () => {
    for (const path of [null, "https://external.invalid", "//external.invalid", "/\\external.invalid", "/login", "/api/schema", "/runs\nLocation: https://external.invalid"])
        expect(safeReturnTo(path)).toBe("/dashboard");
    expect(safeReturnTo("/runs/abc/rows/14?audience_level=basic")).toBe("/runs/abc/rows/14?audience_level=basic");
    expect(safeReturnTo("/dashboard?period=30d")).toBe("/dashboard?period=30d");
    expect(safeReturnTo("/alerts?alert=20")).toBe("/alerts?alert=20");
});

it("redirect mã hóa toàn bộ đường dẫn đích, giữ query và ký tự đã escape", () => {
    const next = "/runs/abc/predictions?class=Normal&row=14&audience=basic&context=truoc%26sau%3D1";
    const response = GET(new Request("http://sentinel.local/login/redirect", {
        headers: { "x-login-return-to": next },
    }));
    const target = new URL(response.headers.get("Location")!, "http://sentinel.local");
    expect(response.status).toBe(302);
    expect(target.pathname).toBe("/login");
    expect(target.searchParams.get("next")).toBe(next);
    expect([...target.searchParams.keys()]).toEqual(["next"]);
});

it("BE thiếu endpoint đăng nhập có hướng dẫn restart và không tự gửi lại mật khẩu", async () => {
    const fetcher = vi.fn();
    vi.stubGlobal("fetch", fetcher);
    for (const status of [404, 405]) {
        fetcher.mockResolvedValueOnce(new Response(
            JSON.stringify({ detail: "Not Found" }), { status },
        ));
        await expect(login("tester", "test-only-password")).rejects.toMatchObject({
            status,
            message: "Chưa tìm thấy API đăng nhập. Khởi động lại BE ở terminal đang chạy rồi thử lại.",
        });
    }
    expect(fetcher).toHaveBeenCalledTimes(2);
});

it("tùy chọn ghi nhớ phiên được gửi đúng tới BE", async () => {
    const fetcher = vi.fn().mockImplementation(() => Promise.resolve(new Response(
        JSON.stringify({ username: "tester", expires_at: 1000 }),
    )));
    vi.stubGlobal("fetch", fetcher);
    await login("tester", "test-only-password", true);
    expect(JSON.parse(fetcher.mock.calls[0][1].body).remember).toBe(true);
    await login("tester", "test-only-password");
    expect(JSON.parse(fetcher.mock.calls[1][1].body).remember).toBe(false);
});

it("BE cũ từ chối remember có hướng dẫn cập nhật, không gửi lại khi bỏ lựa chọn của người dùng", async () => {
    const fetcher = vi.fn().mockResolvedValue(new Response(JSON.stringify({
        detail: "Dữ liệu yêu cầu không hợp lệ.",
        errors: [{ field: "body.remember", message: "Yêu cầu có trường không được hỗ trợ." }],
    }), { status: 422 }));
    vi.stubGlobal("fetch", fetcher);
    await expect(login("tester", "test-only-password", true)).rejects.toMatchObject({
        status: 422,
        message: "BE chưa hỗ trợ Ghi nhớ phiên. Khởi động lại BE để cập nhật.",
    });
    expect(fetcher).toHaveBeenCalledTimes(1);
    expect(JSON.parse(fetcher.mock.calls[0][1].body).remember).toBe(true);
});
