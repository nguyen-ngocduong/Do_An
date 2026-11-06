"use client";
import Image from "next/image";
import { useCallback, useState } from "react";
import { FileSearch } from "lucide-react";
import { getText } from "@/lib/api/client";
import { parseCsv } from "@/lib/csv";
import { csvDisplayValue } from "@/lib/format";
import { MarkdownPreview } from "./markdown-preview";
import { usePolling } from "@/lib/use-polling";
import {
    DownloadButton,
    Empty,
    ErrorNotice,
    JsonViewer,
    Loading,
} from "@/components/shared/controls";

const FILES = [
    "explanation.json",
    "report_vi.md",
    "top5_features.csv",
    "waterfall.png",
];

export function CaseFiles({
    files,
    revision,
}: {
    files: Record<string, string>;
    revision?: string;
}) {
    const [selected, setSelected] = useState(FILES[0]);
    const [sourceView, setSourceView] = useState(false);
    const available = FILES.filter((name) => files[name]);
    const filename = available.includes(selected) ? selected : available[0];
    const path = filename ? files[filename] : undefined;
    const load = useCallback(
        async (signal: AbortSignal) => {
            if (!path || filename === "waterfall.png") return null;
            const text = await getText(path, signal);
            return {
                text,
                json: filename.endsWith(".json")
                    ? (JSON.parse(text) as unknown)
                    : null,
                csv: filename.endsWith(".csv") ? parseCsv(text) : [],
            };
        },
        [path, filename],
    );
    const preview = usePolling(`artifact:${path}:${revision}`, load, 30000);
    return (
        <section
            className="case-artifacts"
            id="case-files"
            aria-labelledby="case-files-title"
        >
            <div className="section-heading">
                <h2 id="case-files-title">
                    <FileSearch className="icon" aria-hidden="true" />
                    Tệp kết quả của mẫu
                </h2>
                {path && (
                    <DownloadButton path={path} name={filename}>
                        Tải tệp đang xem
                    </DownloadButton>
                )}
            </div>
            <p className="muted small">
                Xem dữ liệu đã lưu, báo cáo và biểu đồ của đúng mẫu này.
            </p>
            <div
                className="artifact-tabs"
                role="group"
                aria-label="Chọn tệp xem trước"
            >
                {FILES.map((name) => (
                    <button
                        key={name}
                        data-artifact={name}
                        disabled={!files[name]}
                        aria-pressed={name === filename}
                        onClick={() => setSelected(name)}
                    >
                        {name}
                    </button>
                ))}
            </div>
            {!path ? (
                <Empty
                    title="Chưa có tệp kết quả"
                    description="Tệp sẽ xuất hiện sau khi mẫu được giải thích và ghi xong kết quả."
                />
            ) : (
                <>
                    <ErrorNotice
                        error={preview.error}
                        retry={preview.refresh}
                    />
                    {filename.endsWith(".md") && (
                        <div
                            className="artifact-view-mode"
                            role="group"
                            aria-label="Chế độ xem báo cáo"
                        >
                            <button
                                aria-pressed={!sourceView}
                                onClick={() => setSourceView(false)}
                            >
                                Bản trình bày
                            </button>
                            <button
                                aria-pressed={sourceView}
                                onClick={() => setSourceView(true)}
                            >
                                Văn bản gốc
                            </button>
                        </div>
                    )}
                    <div className="artifact-content" id="artifact-preview">
                        {filename === "waterfall.png" ? (
                            <Image
                                unoptimized
                                width={1200}
                                height={800}
                                src={path}
                                className="waterfall"
                                alt="Biểu đồ Waterfall SHAP của mẫu đang xem"
                            />
                        ) : !preview.data ? (
                            <Loading />
                        ) : filename.endsWith(".json") ? (
                            <JsonViewer
                                value={preview.data.json}
                                title={filename}
                            />
                        ) : filename.endsWith(".csv") ? (
                            <div className="table-wrap">
                                <table className="artifact-csv">
                                    <thead>
                                        <tr>
                                            {preview.data.csv[0]?.map(
                                                (name, index) => (
                                                    <th key={index}>{name}</th>
                                                ),
                                            )}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {preview.data.csv
                                            .slice(1)
                                            .map((row, index) => (
                                                <tr key={index}>
                                                    {row.map(
                                                        (value, column) => (
                                                            <td
                                                                className="wrap"
                                                                key={column}
                                                                title={value}
                                                                data-raw-value={
                                                                    value
                                                                }
                                                            >
                                                                {csvDisplayValue(
                                                                    value,
                                                                    preview.data
                                                                        ?.csv[0]?.[
                                                                        column
                                                                    ] || "",
                                                                )}
                                                            </td>
                                                        ),
                                                    )}
                                                </tr>
                                            ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : sourceView ? (
                            <pre className="artifact-source">
                                {preview.data.text}
                            </pre>
                        ) : (
                            <MarkdownPreview
                                text={preview.data.text}
                                files={files}
                            />
                        )}
                    </div>
                </>
            )}
        </section>
    );
}
