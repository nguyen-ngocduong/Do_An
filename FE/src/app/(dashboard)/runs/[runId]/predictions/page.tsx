import { notFound } from "next/navigation";
import { PredictionBrowser } from "@/components/predictions/prediction-browser";
import { validRunId } from "@/lib/navigation";
export default async function Page({
    params,
}: {
    params: Promise<{ runId: string }>;
}) {
    const { runId } = await params;
    if (!validRunId(runId)) notFound();
    return <PredictionBrowser key={runId} id={runId} />;
}
