import { afterEach, expect, it, vi } from "vitest";
import { deleteRun } from "./runs";

afterEach(() => vi.unstubAllGlobals());

const id = "a".repeat(32);

it("xóa gửi DELETE đúng một lần, dùng phiên hiện tại và không gửi body", async () => {
    const result = {
        run_id: id,
        files_deleted: true,
        message: "Đã xóa lần chạy.",
    };
    const fetcher = vi
        .fn()
        .mockResolvedValue(new Response(JSON.stringify(result)));
    vi.stubGlobal("fetch", fetcher);
    expect(await deleteRun(id)).toEqual(result);
    expect(fetcher).toHaveBeenCalledTimes(1);
    expect(fetcher.mock.calls[0][0]).toContain(`/api/runs/${id}`);
    expect(fetcher.mock.calls[0][1]).toMatchObject({
        method: "DELETE",
        credentials: "same-origin",
        cache: "no-store",
    });
    expect(fetcher.mock.calls[0][1].body).toBeUndefined();
});

it("server cũ có hướng dẫn cập nhật, không đổi sang POST hoặc tự gửi lại", async () => {
    const fetcher = vi
        .fn()
        .mockResolvedValue(new Response("", { status: 405 }));
    vi.stubGlobal("fetch", fetcher);
    await expect(deleteRun(id)).rejects.toMatchObject({
        status: 405,
        message: expect.stringContaining("Khởi động lại BE"),
    });
    expect(fetcher).toHaveBeenCalledTimes(1);
});

it("tác vụ còn chạy trả 409, giữ nguyên lỗi và không tự xóa lại", async () => {
    const fetcher = vi
        .fn()
        .mockResolvedValue(
            new Response(JSON.stringify({ detail: "SHAP đang chạy." }), {
                status: 409,
            }),
        );
    vi.stubGlobal("fetch", fetcher);
    await expect(deleteRun(id)).rejects.toMatchObject({
        status: 409,
        message: "SHAP đang chạy.",
    });
    expect(fetcher).toHaveBeenCalledTimes(1);
});
