import { afterEach, expect, it, vi } from "vitest";
import { getDashboard } from "./dashboard";
afterEach(() => vi.unstubAllGlobals());
it("lấy tổng quan bằng một GET với đúng khoảng/run, không tải từng trang để cộng", async () => {
    const fetcher = vi.fn(async (input: string, options?: RequestInit) => {
        expect(new URL(input).pathname).toBe("/api/dashboard");
        expect(options?.method).toBeUndefined();
        return new Response(
            JSON.stringify({ metrics: { predicted_rows: 171 } }),
        );
    });
    vi.stubGlobal("fetch", fetcher);
    const result = await getDashboard(
        "30d",
        "a".repeat(32),
        new AbortController().signal,
    );
    expect(result.metrics.predicted_rows).toBe(171);
    expect(fetcher).toHaveBeenCalledTimes(1);
    const [url] = fetcher.mock.calls[0];
    expect(new URL(url).searchParams.get("period")).toBe("30d");
    expect(new URL(url).searchParams.get("run_id")).toBe("a".repeat(32));
});
it("BE cũ có chỉ dẫn cập nhật, không tự gọi lại hoặc dựng số 0", async () => {
    const fetcher = vi.fn(
        async () =>
            new Response(JSON.stringify({ detail: "Not Found" }), {
                status: 404,
            }),
    );
    vi.stubGlobal("fetch", fetcher);
    await expect(
        getDashboard("7d", "", new AbortController().signal),
    ).rejects.toMatchObject({
        status: 404,
        message: expect.stringContaining("1.7.0"),
    });
    expect(fetcher).toHaveBeenCalledTimes(1);
});
