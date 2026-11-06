import { afterEach, expect, it, vi } from "vitest";
import { getAlertOverview } from "./alerts";

afterEach(() => vi.unstubAllGlobals());

it("tổng quan lấy đủ số từ API, cùng lớp/lần chạy và không bị giới hạn trang 20 dòng", async () => {
    const totals: Record<string, number> = {
        all: 258,
        new: 49,
        acknowledged: 10,
        closed: 199,
    };
    const fetcher = vi.fn(async (input: string, options?: RequestInit) => {
        expect(options?.method).toBeUndefined();
        const url = new URL(input);
        const status = url.searchParams.get("status") || "all";
        return new Response(
            JSON.stringify({
                items: [],
                total: totals[status],
                offset: 0,
                limit: 1,
            }),
        );
    });
    vi.stubGlobal("fetch", fetcher);
    const id = "a".repeat(32);
    expect(
        await getAlertOverview(id, "DDoS", new AbortController().signal),
    ).toEqual({
        total: 258,
        new_count: 49,
        acknowledged_count: 10,
        closed_count: 199,
    });
    expect(fetcher).toHaveBeenCalledTimes(4);
    for (const [input, options] of fetcher.mock.calls) {
        const url = new URL(input);
        expect(url.pathname).toBe("/api/alerts");
        expect(url.searchParams.get("run_id")).toBe(id);
        expect(url.searchParams.get("predicted_class")).toBe("DDoS");
        expect(url.searchParams.get("limit")).toBe("1");
        expect(options?.method).toBeUndefined();
    }
});

it("lỗi tải tổng quan không biến thành số 0 hoặc tự gửi thao tác ghi", async () => {
    const fetcher = vi
        .fn()
        .mockResolvedValue(
            new Response(
                JSON.stringify({ detail: "Chưa tải được thống kê." }),
                { status: 503 },
            ),
        );
    vi.stubGlobal("fetch", fetcher);
    await expect(
        getAlertOverview("", "", new AbortController().signal),
    ).rejects.toMatchObject({ status: 503 });
    expect(fetcher).toHaveBeenCalledTimes(4);
});
