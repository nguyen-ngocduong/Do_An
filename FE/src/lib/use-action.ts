"use client";
import { useCallback, useEffect, useRef, useState } from "react";

// Chỉ gọi từ event handler. Không gửi lại thao tác ghi khi unmount/Strict Mode.
export function useAction() {
    const mounted = useRef(false);
    const busy = useRef(false);
    const [pending, setPending] = useState(false);
    const [error, setError] = useState<unknown>();
    useEffect(() => {
        mounted.current = true;
        return () => {
            mounted.current = false;
        };
    }, []);
    const run = useCallback(
        async <T>(work: () => Promise<T>, success?: (value: T) => void) => {
            if (busy.current) return;
            busy.current = true;
            setPending(true);
            setError(undefined);
            try {
                const value = await work();
                if (mounted.current) success?.(value);
            } catch (error) {
                if (mounted.current) setError(error);
            } finally {
                busy.current = false;
                if (mounted.current) setPending(false);
            }
        },
        [],
    );
    return { pending, error, run };
}
