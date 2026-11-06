"use client";
import {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useRef,
    useState,
} from "react";
import { getMetadata } from "@/lib/api/model";
import { usePolling } from "@/lib/use-polling";

export interface TableMemory {
    selected: number[];
    peekIndex: number | null;
    peekOpen: boolean;
    peekTab: string;
    scrollTop: number;
    scrollLeft: number;
}
export const emptyTable: TableMemory = {
    selected: [],
    peekIndex: null,
    peekOpen: true,
    peekTab: "predict",
    scrollTop: 0,
    scrollLeft: 0,
};
function useUiState() {
    const [ready, setReady] = useState(false);
    const [dark, setDark] = useState(false);
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [lastRun, setLastRun] = useState("");
    const [online, setOnline] = useState(true);
    const [toast, setToast] = useState("");
    const tables = useRef(new Map<string, TableMemory>());
    const metadata = usePolling("metadata", getMetadata, 15000);
    useEffect(() => {
        // Browser storage được đọc sau hydration; HTML đầu tiên luôn nhất quán.
        try {
            const dark = localStorage.getItem("iot:theme") === "dark";
            document.documentElement.dataset.theme = dark ? "dark" : "light";
            // eslint-disable-next-line react-hooks/set-state-in-effect -- Khôi phục tùy chọn trình duyệt sau hydration.
            setDark(dark);
            setLastRun(localStorage.getItem("iot:last-run") || "");
            setSidebarCollapsed(
                localStorage.getItem("nidr:sidebar") === "collapsed",
            );
        } catch {
            /* Không bắt buộc browser storage. */
        }
        setReady(true);
        const update = () => setOnline(navigator.onLine);
        update();
        window.addEventListener("online", update);
        window.addEventListener("offline", update);
        return () => {
            window.removeEventListener("online", update);
            window.removeEventListener("offline", update);
        };
    }, []);
    useEffect(() => {
        if (toast) {
            const timer = setTimeout(() => setToast(""), 4500);
            return () => clearTimeout(timer);
        }
    }, [toast]);
    const toggleTheme = useCallback(
        () =>
            setDark((previous) => {
                const next = !previous;
                document.documentElement.dataset.theme = next
                    ? "dark"
                    : "light";
                try {
                    localStorage.setItem("iot:theme", next ? "dark" : "light");
                } catch {
                    /* Tùy chọn vẫn dùng được trong bộ nhớ. */
                }
                return next;
            }),
        [],
    );
    const rememberRun = useCallback((id: string) => {
        setLastRun(id);
        try {
            localStorage.setItem("iot:last-run", id);
        } catch {
            /* Giữ state trong phiên. */
        }
    }, []);
    const toggleSidebar = useCallback(() => {
        setSidebarCollapsed((previous) => {
            const next = !previous;
            try {
                localStorage.setItem(
                    "nidr:sidebar",
                    next ? "collapsed" : "expanded",
                );
            } catch {
                /* Menu vẫn dùng được khi trình duyệt không cho lưu tùy chọn. */
            }
            return next;
        });
    }, []);
    const forgetRun = useCallback((id: string) => {
        tables.current.delete(id);
        setLastRun((previous) => (previous === id ? "" : previous));
        try {
            sessionStorage.removeItem(`iot:next:table:${id}`);
            if (localStorage.getItem("iot:last-run") === id)
                localStorage.removeItem("iot:last-run");
        } catch {
            /* State trong phiên vẫn được dọn khi storage không truy cập được. */
        }
    }, []);
    const getTable = useCallback((id: string): TableMemory => {
        const cached = tables.current.get(id);
        if (cached) return cached;
        try {
            const stored = JSON.parse(
                sessionStorage.getItem(`iot:next:table:${id}`) || "null",
            ) as Partial<TableMemory> | null;
            if (stored && Array.isArray(stored.selected))
                return {
                    ...emptyTable,
                    ...stored,
                    selected: stored.selected
                        .filter(Number.isSafeInteger)
                        .slice(0, 50),
                };
        } catch {
            /* Bỏ qua state cũ không đọc được. */
        }
        return { ...emptyTable, selected: [] };
    }, []);
    const saveTable = useCallback((id: string, value: TableMemory) => {
        tables.current.set(id, value);
        try {
            sessionStorage.setItem(
                `iot:next:table:${id}`,
                JSON.stringify(value),
            );
        } catch {
            /* Bộ nhớ trong context vẫn còn. */
        }
    }, []);
    return {
        ready,
        dark,
        sidebarCollapsed,
        toggleSidebar,
        lastRun,
        online,
        toggleTheme,
        rememberRun,
        forgetRun,
        getTable,
        saveTable,
        notify: setToast,
        toast,
        metadata,
    };
}
type UiState = ReturnType<typeof useUiState>;
const Context = createContext<UiState | null>(null);
export function UiProvider({ children }: { children: React.ReactNode }) {
    const value = useUiState();
    return <Context.Provider value={value}>{children}</Context.Provider>;
}
export function useUi() {
    const value = useContext(Context);
    if (!value) throw new Error("Thiếu UiProvider.");
    return value;
}
