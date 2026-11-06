"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
    AlertCircle,
    ArrowRight,
    Eye,
    EyeOff,
    LoaderCircle,
    ShieldCheck,
} from "lucide-react";
import { getSession, login, safeReturnTo } from "@/lib/api/auth";
import { errorText } from "@/lib/api/client";
import { useAction } from "@/lib/use-action";
import { APP_FULL_NAME, APP_NAME } from "@/lib/brand";
import { SiteFooter } from "@/components/shared/site-footer";

export function LoginForm() {
    const search = useSearchParams();
    const next = safeReturnTo(search.get("next"));
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [visible, setVisible] = useState(false);
    const [capsLock, setCapsLock] = useState(false);
    const [validation, setValidation] = useState("");
    const [remember, setRemember] = useState(false);
    const [supportOpen, setSupportOpen] = useState(false);
    const [dark, setDark] = useState(false);
    const usernameInput = useRef<HTMLInputElement>(null);
    const passwordInput = useRef<HTMLInputElement>(null);
    const action = useAction();

    useEffect(() => {
        const controller = new AbortController();
        getSession(controller.signal)
            .then((session) => {
                if (!controller.signal.aborted && session.expires_at !== null)
                    window.location.replace(next);
            })
            .catch(() => {
                // Chưa có phiên hoặc BE đang mất kết nối: giữ form để đăng nhập.
            });
        try {
            const saved = localStorage.getItem("iot:theme") === "dark";
            document.documentElement.dataset.theme = saved ? "dark" : "light";
            // eslint-disable-next-line react-hooks/set-state-in-effect -- Khôi phục tùy chọn giao diện sau hydration.
            setDark(saved);
        } catch {
            /* Đăng nhập không phụ thuộc browser storage. */
        }
        return () => controller.abort();
    }, [next]);

    function toggleTheme() {
        const next = !dark;
        setDark(next);
        document.documentElement.dataset.theme = next ? "dark" : "light";
        try {
            localStorage.setItem("iot:theme", next ? "dark" : "light");
        } catch {
            /* Giữ lựa chọn trong phiên hiện tại. */
        }
    }

    function submit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        setValidation("");
        if (!username.trim() || !password) {
            setValidation("Vui lòng nhập tên đăng nhập và mật khẩu.");
            if (!username.trim()) usernameInput.current?.focus();
            else passwordInput.current?.focus();
            return;
        }
        void action.run(
            () => login(username.trim(), password, remember),
            () => {
                setPassword("");
                window.location.replace(next);
            },
        );
    }

    const message = validation || (action.error ? errorText(action.error) : "");
    return (
        <div className="login-page">
            <header className="login-header">
                <label className="theme-control">
                    <input
                        id="theme-toggle"
                        type="checkbox"
                        role="switch"
                        aria-label="Nền tối"
                        checked={dark}
                        onChange={toggleTheme}
                    />
                    <span className="theme-switch-track" aria-hidden="true" />
                    Nền tối
                </label>
            </header>
            <main className="login-main" id="main-content">
                <section
                    className="login-content"
                    aria-labelledby="login-title"
                >
                    <div className="login-intro">
                        <div className="login-brand" title={APP_FULL_NAME}>
                            <ShieldCheck className="icon" aria-hidden="true" />
                            {APP_NAME}
                        </div>
                        <h1 id="login-title">Đăng nhập</h1>
                        <p>
                            Truy cập không gian phân tích và giải thích cảnh
                            báo.
                        </p>
                    </div>
                    <form
                        id="login-form"
                        onSubmit={submit}
                        noValidate
                        aria-busy={action.pending}
                        aria-describedby={message ? "login-error" : undefined}
                    >
                        <label className="field" htmlFor="login-username">
                            Tên đăng nhập
                            <input
                                ref={usernameInput}
                                id="login-username"
                                name="username"
                                autoComplete="username"
                                placeholder="admin"
                                autoCapitalize="none"
                                spellCheck={false}
                                maxLength={128}
                                required
                                disabled={action.pending}
                                value={username}
                                onChange={(event) =>
                                    setUsername(event.target.value)
                                }
                            />
                        </label>
                        <div className="field">
                            <label htmlFor="login-password">Mật khẩu</label>
                            <div className="login-password-field">
                                <input
                                    ref={passwordInput}
                                    id="login-password"
                                    name="password"
                                    type={visible ? "text" : "password"}
                                    autoComplete="current-password"
                                    placeholder="••••••••"
                                    maxLength={4096}
                                    required
                                    disabled={action.pending}
                                    value={password}
                                    aria-describedby={
                                        message
                                            ? "login-error"
                                            : capsLock
                                              ? "caps-lock-warning"
                                              : "login-session-note"
                                    }
                                    onChange={(event) =>
                                        setPassword(event.target.value)
                                    }
                                    onKeyUp={(event) =>
                                        setCapsLock(
                                            event.getModifierState("CapsLock"),
                                        )
                                    }
                                    onBlur={() => setCapsLock(false)}
                                />
                                <button
                                    type="button"
                                    className="icon-button text-button"
                                    aria-label={
                                        visible
                                            ? "Ẩn mật khẩu"
                                            : "Hiện mật khẩu"
                                    }
                                    aria-pressed={visible}
                                    disabled={action.pending}
                                    onClick={() => setVisible(!visible)}
                                >
                                    {visible ? (
                                        <EyeOff className="icon" />
                                    ) : (
                                        <Eye className="icon" />
                                    )}
                                </button>
                            </div>
                        </div>
                        <div className="login-options">
                            <label className="login-remember">
                                <input
                                    id="login-remember"
                                    name="remember"
                                    type="checkbox"
                                    checked={remember}
                                    disabled={action.pending}
                                    onChange={(event) =>
                                        setRemember(event.target.checked)
                                    }
                                />
                                Ghi nhớ phiên
                            </label>
                            <button
                                type="button"
                                className="text-button login-support-link"
                                aria-expanded={supportOpen}
                                aria-controls="login-support"
                                disabled={action.pending}
                                onClick={() => setSupportOpen(!supportOpen)}
                            >
                                Quên mật khẩu?
                            </button>
                        </div>
                        <div className="login-feedback">
                            {message ? (
                                <div
                                    id="login-error"
                                    className="notice error"
                                    role="alert"
                                >
                                    <AlertCircle
                                        className="icon"
                                        aria-hidden="true"
                                    />
                                    <span>{message}</span>
                                </div>
                            ) : capsLock ? (
                                <p
                                    id="caps-lock-warning"
                                    className="login-caps"
                                >
                                    Caps Lock đang bật.
                                </p>
                            ) : (
                                <p
                                    id="login-session-note"
                                    className="login-session-note"
                                >
                                    {remember
                                        ? "Ghi nhớ trên trình duyệt này, tối đa 8 giờ. Chỉ dùng trên thiết bị tin cậy."
                                        : "Phiên đăng nhập có hiệu lực tối đa 8 giờ."}
                                </p>
                            )}
                        </div>
                        <button
                            id="login-submit"
                            type="submit"
                            className="primary login-submit"
                            disabled={action.pending}
                        >
                            {action.pending && (
                                <LoaderCircle
                                    className="icon login-spinner"
                                    aria-hidden="true"
                                />
                            )}
                            {action.pending ? "Đang đăng nhập…" : "Đăng nhập"}
                            {!action.pending && (
                                <ArrowRight
                                    className="icon"
                                    aria-hidden="true"
                                />
                            )}
                        </button>
                    </form>
                    <div
                        id="login-support"
                        className="login-support"
                        hidden={!supportOpen}
                    >
                        <strong>Liên hệ quản trị viên</strong>
                        <p>
                            Hãy liên hệ người quản trị đã cấp tài khoản để được
                            đặt lại mật khẩu.
                        </p>
                    </div>
                </section>
            </main>
            <SiteFooter />
        </div>
    );
}
