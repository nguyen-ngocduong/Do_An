"use client";
import { useCallback, useEffect, useState } from "react";

interface PollState<T> {
    key: string;
    data?: T;
    error?: unknown;
}
export function usePolling<T>(
    key: string,
    load: (signal: AbortSignal) => Promise<T>,
    interval = 2500,
) {
    const [state, setState] = useState<PollState<T>>({ key });
    const [version, setVersion] = useState(0);
    const refresh = useCallback(() => setVersion((value) => value + 1), []);
    useEffect(() => {
        let active = true;
        let timer: ReturnType<typeof setTimeout>;
        let busy = false;
        let firstRequest = true;
        const controller = new AbortController();
        async function tick() {
            if (!active || busy) return;
            clearTimeout(timer);
            // Tab nền vẫn cần dữ liệu đầu tiên để hiện trang/kiểm tra phiên.
            // Chỉ các lần polling định kỳ mới chờ tới khi tab được xem.
            if (firstRequest || !document.hidden) {
                firstRequest = false;
                busy = true;
                try {
                    const data = await load(controller.signal);
                    if (active) setState({ key, data });
                } catch (error) {
                    if (active)
                        setState((previous) => ({
                            key,
                            data:
                                previous.key === key
                                    ? previous.data
                                    : undefined,
                            error,
                        }));
                } finally {
                    busy = false;
                }
            }
            if (active) timer = setTimeout(tick, interval);
        }
        void tick();
        const visible = () => {
            if (!document.hidden) void tick();
        };
        document.addEventListener("visibilitychange", visible);
        window.addEventListener("online", visible);
        return () => {
            active = false;
            controller.abort();
            clearTimeout(timer);
            document.removeEventListener("visibilitychange", visible);
            window.removeEventListener("online", visible);
        };
    }, [key, load, version, interval]);
    return {
        data: state.key === key ? state.data : undefined,
        error: state.key === key ? state.error : undefined,
        refresh,
    };
}
