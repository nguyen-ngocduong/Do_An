import { notFound, redirect } from "next/navigation";
import { validRunId } from "@/lib/navigation";
export default async function Page({
    params,
}: {
    params: Promise<{ runId: string }>;
}) {
    const { runId } = await params;
    if (!validRunId(runId)) notFound();
    redirect(`/runs/${runId}/monitor`);
}
