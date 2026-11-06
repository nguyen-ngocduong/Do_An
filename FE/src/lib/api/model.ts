import { get } from "./client";
import type { ModelInfo, InputSchema } from "@/types/model";
export async function getMetadata(signal: AbortSignal) {
    const [model, schema] = await Promise.all([
        get<ModelInfo>("/api/model", signal),
        get<InputSchema>("/api/schema", signal),
    ]);
    return { model, schema };
}
