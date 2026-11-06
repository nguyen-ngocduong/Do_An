import { notFound } from "next/navigation";
import { RunExport } from "@/components/runs/export";
import { validRunId } from "@/lib/navigation";
export default async function Page({
    params,
}: {
    params: Promise<{ runId: string }>;
}) {
    const { runId } = await params;
    if (!validRunId(runId)) notFound();
    return <RunExport key={runId} id={runId} />;
}
