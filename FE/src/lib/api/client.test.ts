import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, get, query, safeApiUrl, send } from "./client";
afterEach(() => vi.unstubAllGlobals());
describe("API cùng origin", () => {
    it("từ chối URL ngoài origin, traversal và đường dẫn ngoài API", () => {
        for (const path of [
            "https://external.invalid/api/data",
            "//external.invalid/api/x",
            "/api/../BE/.env",
            "/docs",
        ])
            expect(() => safeApiUrl(path)).toThrow();
        expect(new URL(safeApiUrl("/api/runs?a=1")).pathname).toBe("/api/runs");
    });
    it("mã hóa query, giữ số 0 và bỏ giá trị thiếu", () => {
        expect(
            query({ row: 0, audience: "basic", blank: "", absent: undefined }),
        ).toBe("row=0&audience=basic");
    });
    it("upload multipart không tự gán Content-Type, không retry POST", async () => {
        const fetcher = vi
            .fn()
            .mockResolvedValue(
                new Response(JSON.stringify({ id: "a" }), { status: 202 }),
            );
        vi.stubGlobal("fetch", fetcher);
        const data = new FormData();
        data.append("file", new File(["a\n1"], "test.csv"));
        await send("/api/runs", "POST", data);
        expect(fetcher).toHaveBeenCalledTimes(1);
        expect(fetcher.mock.calls[0][1]).toMatchObject({
            method: "POST",
            body: data,
            credentials: "same-origin",
            cache: "no-store",
        });
        expect(fetcher.mock.calls[0][1].headers).toBeUndefined();
    });
    it("401 được giữ mã và diễn giải bằng tiếng Việt", async () => {
        vi.stubGlobal(
            "fetch",
            vi.fn().mockResolvedValue(new Response("", { status: 401 })),
        );
        await expect(get("/api/schema")).rejects.toMatchObject({
            status: 401,
            message: expect.stringContaining("đăng nhập lại"),
        });
    });
    it("422 giữ lỗi từng trường và không retry", async () => {
        const fetcher = vi
            .fn()
            .mockResolvedValue(
                new Response(
                    JSON.stringify({
                        detail: "Dữ liệu không hợp lệ",
                        errors: [
                            { field: "row_indices", message: "Quá 50 dòng" },
                        ],
                    }),
                    { status: 422 },
                ),
            );
        vi.stubGlobal("fetch", fetcher);
        await expect(
            send("/api/runs/a/explanations", "POST", {}),
        ).rejects.toBeInstanceOf(ApiError);
        expect(fetcher).toHaveBeenCalledTimes(1);
    });
});
