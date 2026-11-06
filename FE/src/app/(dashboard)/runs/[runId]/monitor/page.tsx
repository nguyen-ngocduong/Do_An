import { notFound } from "next/navigation";
import { RunMonitor } from "@/components/runs/monitor";
import { validRunId } from "@/lib/navigation";
export default async function Page({
    params,
}: {
    params: Promise<{ runId: string }>;
}) {
    const { runId } = await params;
    if (!validRunId(runId)) notFound();
    return <RunMonitor key={runId} id={runId} />;
}
