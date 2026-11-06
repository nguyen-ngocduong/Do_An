import Image from "next/image";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

export function MarkdownPreview({
    text,
    files,
}: {
    text: string;
    files: Record<string, string>;
}) {
    return (
        <div className="artifact-markdown">
            <Markdown
                skipHtml
                remarkPlugins={[remarkGfm]}
                components={{
                    h1: ({ children }) => <h3>{children}</h3>,
                    h2: ({ children }) => <h4>{children}</h4>,
                    h3: ({ children }) => <h5>{children}</h5>,
                    a: ({ href, children }) => (
                        <a
                            href={href}
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            {children}
                        </a>
                    ),
                    table: ({ children }) => (
                        <div className="table-wrap">
                            <table>{children}</table>
                        </div>
                    ),
                    img: ({ src, alt }) =>
                        src === "waterfall.png" && files["waterfall.png"] ? (
                            <Image
                                unoptimized
                                width={1200}
                                height={800}
                                src={files["waterfall.png"]}
                                alt={alt || "Waterfall SHAP của mẫu"}
                                className="waterfall"
                            />
                        ) : (
                            <span>
                                {alt || "Hình tham chiếu trong báo cáo"}
                            </span>
                        ),
                }}
            >
                {text}
            </Markdown>
        </div>
    );
}
