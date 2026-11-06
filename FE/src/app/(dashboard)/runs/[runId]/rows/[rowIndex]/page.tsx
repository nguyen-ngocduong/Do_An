import { notFound } from "next/navigation";
import { validRunId } from "@/lib/navigation";
import { ExplanationInspector } from "@/components/explanations/explanation-inspector";
export default async function Page({
    params,
}: {
    params: Promise<{ runId: string; rowIndex: string }>;
}) {
    const { runId, rowIndex } = await params;
    const index = Number(rowIndex);
    if (
        !validRunId(runId) ||
        !/^\d+$/.test(rowIndex) ||
        !Number.isSafeInteger(index)
    )
        notFound();
    return (
        <ExplanationInspector
            key={`${runId}:${index}`}
            id={runId}
            index={index}
        />
    );
}
