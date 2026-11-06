import { Suspense } from "react";
import { OperationalShell } from "@/components/shared/operational-shell";
import { Loading } from "@/components/shared/controls";
import { UiProvider } from "@/store/ui-store";
import { SessionGate } from "@/components/auth/session-gate";
export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <Suspense fallback={<Loading />}>
            <SessionGate>
                <UiProvider>
                    <OperationalShell>{children}</OperationalShell>
                </UiProvider>
            </SessionGate>
        </Suspense>
    );
}
