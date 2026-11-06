import { act, renderHook } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { StrictMode } from "react";
import { usePolling } from "./use-polling";
afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
});
it("chờ request trước hoàn tất, loại phản hồi cũ và abort khi đổi mẫu", async () => {
    vi.useFakeTimers();
    let finishOld: (value: string) => void = () => {};
    let oldSignal: AbortSignal | undefined;
    const oldLoad = vi.fn((signal: AbortSignal) => {
        oldSignal = signal;
        return new Promise<string>((resolve) => {
            finishOld = resolve;
        });
    });
    const nextLoad = vi.fn(async () => "mẫu mới");
    const { result, rerender, unmount } = renderHook(
        ({ key, load }) => usePolling(key, load),
        {
            initialProps: {
                key: "old",
                load: oldLoad as (signal: AbortSignal) => Promise<string>,
            },
        },
    );
    await act(async () => {
        await vi.advanceTimersByTimeAsync(10000);
    });
    expect(oldLoad).toHaveBeenCalledTimes(1);
    await act(async () => {
        rerender({ key: "new", load: nextLoad });
    });
    expect(oldSignal?.aborted).toBe(true);
    await act(async () => {
        finishOld("mẫu cũ");
    });
    expect(result.current.data).toBe("mẫu mới");
    unmount();
    await act(async () => {
        await vi.advanceTimersByTimeAsync(10000);
    });
    expect(nextLoad).toHaveBeenCalledTimes(1);
});
it("giữ kết quả cuối khi lỗi; không gọi khi tab ẩn", async () => {
    vi.useFakeTimers();
    let hidden = false;
    vi.spyOn(document, "hidden", "get").mockImplementation(() => hidden);
    const load = vi
        .fn()
        .mockResolvedValueOnce("bằng chứng")
        .mockRejectedValue(new Error("mất mạng"));
    const { result } = renderHook(() => usePolling("same", load));
    await act(async () => {});
    expect(result.current.data).toBe("bằng chứng");
    hidden = true;
    await act(async () => {
        await vi.advanceTimersByTimeAsync(5000);
    });
    expect(load).toHaveBeenCalledTimes(1);
    hidden = false;
    await act(async () => {
        document.dispatchEvent(new Event("visibilitychange"));
    });
    expect(result.current.data).toBe("bằng chứng");
    expect(result.current.error).toBeInstanceOf(Error);
});
it("StrictMode cleanup abort lời gọi đầu và không giữ timer sau unmount", async () => {
    vi.useFakeTimers();
    const signals: AbortSignal[] = [];
    const load = vi.fn(async (signal: AbortSignal) => {
        signals.push(signal);
        return "ok";
    });
    const { unmount } = renderHook(() => usePolling("case", load), {
        wrapper: StrictMode,
    });
    await act(async () => {});
    expect(signals).toHaveLength(2);
    expect(signals[0].aborted).toBe(true);
    unmount();
    expect(signals[1].aborted).toBe(true);
    expect(vi.getTimerCount()).toBe(0);
});
it("tab nền vẫn tải lần đầu, đổi trang và refresh; chỉ dừng polling định kỳ", async () => {
    vi.useFakeTimers();
    vi.spyOn(document, "hidden", "get").mockReturnValue(true);
    const load = vi.fn(async () => "đã tải");
    const { result, rerender } = renderHook(
        ({ key }) => usePolling(key, load),
        {
            initialProps: { key: "first" },
        },
    );
    await act(async () => {});
    expect(result.current.data).toBe("đã tải");
    expect(load).toHaveBeenCalledTimes(1);
    await act(async () => {
        await vi.advanceTimersByTimeAsync(10000);
    });
    expect(load).toHaveBeenCalledTimes(1);
    await act(async () => {
        result.current.refresh();
    });
    expect(load).toHaveBeenCalledTimes(2);
    await act(async () => {
        rerender({ key: "next" });
    });
    expect(result.current.data).toBe("đã tải");
    expect(load).toHaveBeenCalledTimes(3);
});
it("lỗi lần đầu ở tab nền vẫn hiện để SessionGate không kẹt ở Đang tải", async () => {
    vi.useFakeTimers();
    vi.spyOn(document, "hidden", "get").mockReturnValue(true);
    const error = Object.assign(new Error("Cần đăng nhập"), { status: 401 });
    const load = vi.fn().mockRejectedValue(error);
    const { result } = renderHook(() => usePolling("session", load));
    await act(async () => {});
    expect(result.current.error).toBe(error);
    await act(async () => {
        await vi.advanceTimersByTimeAsync(5000);
    });
    expect(load).toHaveBeenCalledTimes(1);
});
