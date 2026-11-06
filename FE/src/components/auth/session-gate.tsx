"use client";

import { useCallback, useEffect } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { getSession, loginUrl } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { usePolling } from "@/lib/use-polling";
import { ErrorNotice, Loading } from "@/components/shared/controls";

export function SessionGate({ children }: { children: React.ReactNode }) {
    const router = useRouter();
    const pathname = usePathname();
    const search = useSearchParams();
    const session = usePolling("session", getSession, 60000);
    const returnToLogin = useCallback(() => {
        const query = search.toString();
        router.replace(loginUrl(pathname + (query ? `?${query}` : "")));
    }, [pathname, search, router]);
    // Basic có thể còn trong cache trình duyệt cũ; dashboard cần phiên cookie
    // để nút Đăng xuất thực sự kết thúc phiên giao diện.
    const unauthorized = (session.error instanceof ApiError && session.error.status === 401)
        || (session.data !== null && session.data !== undefined && session.data.expires_at === null);

    useEffect(() => {
        if (unauthorized) returnToLogin();
        window.addEventListener("iot:session-expired", returnToLogin);
        return () => window.removeEventListener("iot:session-expired", returnToLogin);
    }, [unauthorized, returnToLogin]);

    if (unauthorized || (!session.data && !session.error)) return <Loading />;
    if (!session.data) return <ErrorNotice error={session.error} retry={session.refresh} />;
    return children;
}
