import { Suspense } from "react";
import { LoginForm } from "@/components/auth/login-form";
import { Loading } from "@/components/shared/controls";
import { APP_NAME } from "@/lib/brand";

export const metadata = { title: `Đăng nhập · ${APP_NAME}` };

export default function LoginPage() {
    return (
        <Suspense fallback={<Loading />}>
            <LoginForm />
        </Suspense>
    );
}
