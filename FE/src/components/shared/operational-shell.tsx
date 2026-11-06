"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    Bell,
    LayoutDashboard,
    History,
    ChartNoAxesColumn,
    CirclePlus,
    CodeXml,
    ShieldCheck,
    LogOut,
    Menu,
    X,
} from "lucide-react";
import { useEffect, useLayoutEffect, useState } from "react";
import { useUi } from "@/store/ui-store";
import { validRunId } from "@/lib/navigation";
import { errorText } from "@/lib/api/client";
import { Loading } from "./controls";
import { logout } from "@/lib/api/auth";
import { useAction } from "@/lib/use-action";
import { APP_FULL_NAME, APP_NAME } from "@/lib/brand";
import { SiteFooter } from "./site-footer";

export function OperationalShell({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const [expandedPath, setExpandedPath] = useState<string | null>(null);
    const menuOpen = expandedPath === pathname;
    const ui = useUi();
    const signOut = useAction();
    const id = pathname.split("/")[2] || "";
    const { rememberRun } = ui;
    useEffect(() => {
        if (validRunId(id)) rememberRun(id);
    }, [id, rememberRun]);
    useLayoutEffect(() => {
        document.getElementById("main-content")?.scrollTo(0, 0);
    }, [pathname]);
    const isRun = validRunId(id);
    const title =
        pathname === "/dashboard"
            ? "Tổng quan"
            : pathname === "/runs/new"
              ? "Tạo lần chạy"
              : pathname.startsWith("/alerts")
                ? "Cảnh báo"
                : pathname.includes("/rows/")
                  ? "Giải thích một mẫu"
                  : pathname.endsWith("/predictions")
                    ? "Bảng dự đoán"
                    : pathname.endsWith("/monitor")
                      ? "Theo dõi lần chạy"
                      : pathname.endsWith("/export")
                        ? "Xuất kết quả"
                        : "Lịch sử lần chạy";
    const current = isRun ? id : ui.lastRun;
    const nav = [
        {
            title: "Tổng quan",
            shortTitle: "Tổng quan",
            href: "/dashboard",
            active: pathname === "/dashboard",
            icon: LayoutDashboard,
        },
        {
            title: "Lịch sử lần chạy",
            shortTitle: "Lịch sử",
            href: "/runs",
            active: pathname === "/runs",
            icon: History,
        },
        {
            title: "Tạo lần chạy",
            shortTitle: "Tạo mới",
            href: "/runs/new",
            active: pathname === "/runs/new",
            icon: CirclePlus,
        },
        {
            title: "Lần chạy hiện tại",
            shortTitle: "Hiện tại",
            href: validRunId(current)
                ? `/runs/${current}/predictions`
                : "/runs/new",
            active: isRun,
            icon: ChartNoAxesColumn,
        },
        {
            title: "Cảnh báo",
            shortTitle: "Cảnh báo",
            href: "/alerts",
            active: pathname.startsWith("/alerts"),
            icon: Bell,
        },
    ];
    const connectionError = !ui.online
        ? "Trình duyệt đang ngoại tuyến."
        : ui.metadata.error
          ? errorText(ui.metadata.error)
          : "";
    return (
        <>
            <a className="skip-link" href="#main-content">
                Đến nội dung chính
            </a>
            <div
                className="app-shell"
                data-sidebar={ui.sidebarCollapsed ? "collapsed" : "expanded"}
            >
                <aside
                    className="sidebar"
                    aria-label="Điều hướng ứng dụng"
                    onKeyDown={(event) => {
                        if (event.key === "Escape" && menuOpen) {
                            setExpandedPath(null);
                            document
                                .getElementById("navigation-toggle")
                                ?.focus();
                        }
                    }}
                >
                    <div className="sidebar-heading">
                        <button
                            id="sidebar-toggle"
                            className="sidebar-toggle"
                            aria-label={
                                ui.sidebarCollapsed
                                    ? "Mở rộng menu"
                                    : "Thu gọn menu"
                            }
                            title={
                                ui.sidebarCollapsed
                                    ? "Mở rộng menu"
                                    : "Thu gọn menu"
                            }
                            aria-expanded={!ui.sidebarCollapsed}
                            aria-controls="primary-navigation"
                            onClick={ui.toggleSidebar}
                        >
                            <Menu className="icon" aria-hidden="true" />
                        </button>
                        <Link
                            className="brand"
                            href="/dashboard"
                            title={APP_FULL_NAME}
                        >
                            <ShieldCheck className="icon" />
                            {APP_NAME}
                        </Link>
                        <button
                            id="navigation-toggle"
                            className="navigation-toggle"
                            aria-expanded={menuOpen}
                            aria-controls="primary-navigation"
                            onClick={() =>
                                setExpandedPath(menuOpen ? null : pathname)
                            }
                        >
                            {menuOpen ? (
                                <X className="icon" aria-hidden="true" />
                            ) : (
                                <Menu className="icon" aria-hidden="true" />
                            )}
                            {menuOpen ? "Đóng menu" : "Menu"}
                        </button>
                    </div>
                    <div className="project">DATN / CICIoT2023</div>
                    <nav id="primary-navigation" data-open={menuOpen}>
                        {nav.map((item) => (
                            <Link
                                key={item.title}
                                href={item.href}
                                aria-label={item.title}
                                title={item.title}
                                aria-current={item.active ? "page" : undefined}
                                onClick={() => setExpandedPath(null)}
                            >
                                <item.icon
                                    className="icon"
                                    aria-hidden="true"
                                />
                                <span className="nav-label">{item.title}</span>
                                <span
                                    className="nav-short-label"
                                    aria-hidden="true"
                                >
                                    {item.shortTitle}
                                </span>
                            </Link>
                        ))}
                    </nav>
                    <div className="sidebar-bottom">
                        <a
                            href="/docs"
                            target="_blank"
                            rel="noopener"
                            aria-label="Mở Swagger API trong tab mới"
                            title="Swagger API"
                        >
                            <CodeXml className="icon" aria-hidden="true" />
                            <span className="nav-label">Swagger API ↗</span>
                            <span
                                className="nav-short-label"
                                aria-hidden="true"
                            >
                                API
                            </span>
                        </a>
                        <p className="small">Đồ án tốt nghiệp</p>
                    </div>
                </aside>
                <div className="workspace">
                    <header className="topbar">
                        <Link
                            className="topbar-brand brand"
                            href="/dashboard"
                            title={APP_FULL_NAME}
                        >
                            <ShieldCheck className="icon" aria-hidden="true" />
                            {APP_NAME}
                        </Link>
                        <div className="breadcrumb">
                            DATN / CICIoT2023 / <span>{title}</span>
                        </div>
                        <div className="top-actions">
                            <label className="theme-control">
                                <input
                                    id="theme-toggle"
                                    type="checkbox"
                                    role="switch"
                                    aria-label="Nền tối"
                                    checked={ui.dark}
                                    onChange={ui.toggleTheme}
                                />
                                <span
                                    className="theme-switch-track"
                                    aria-hidden="true"
                                />
                                Nền tối
                            </label>
                            <button
                                id="logout-button"
                                className="text-button logout-button"
                                disabled={signOut.pending}
                                onClick={() =>
                                    signOut.run(logout, () =>
                                        window.location.replace("/login"),
                                    )
                                }
                            >
                                <LogOut className="icon" aria-hidden="true" />
                                {signOut.pending
                                    ? "Đang đăng xuất…"
                                    : "Đăng xuất"}
                            </button>
                        </div>
                    </header>
                    <div
                        id="connection-error"
                        hidden={!connectionError}
                        className="notice error connection-error"
                        role="status"
                    >
                        {connectionError} Dữ liệu đang xem được giữ lại.{" "}
                        <button onClick={ui.metadata.refresh}>
                            Thử kết nối lại
                        </button>
                        <Link href="/login">Đăng nhập lại</Link>
                    </div>
                    <main id="main-content" tabIndex={-1}>
                        <div className="page-content">
                            {Boolean(signOut.error) && (
                                <div className="notice error" role="alert">
                                    {errorText(signOut.error)}
                                </div>
                            )}
                            {ui.ready ? children : <Loading />}
                        </div>
                        <SiteFooter />
                    </main>
                </div>
            </div>
            <div id="toast" className="toast" role="status" hidden={!ui.toast}>
                {ui.toast}
            </div>
        </>
    );
}
