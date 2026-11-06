import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { MarkdownPreview } from "./markdown-preview";

it("render nhấn mạnh, code, danh sách, liên kết và bảng GFM thành văn bản có cấu trúc", () => {
    const { container } = render(
        <MarkdownPreview
            files={{}}
            text={
                "# Báo cáo\n\n**DDoS** với `IAT`.\n\n- Kiểm tra log\n\n[Tham khảo](https://example.com)\n\n| Lớp | Xác suất |\n| --- | --- |\n| DDoS | 100% |"
            }
        />,
    );
    expect(
        screen.getByRole("heading", { name: "Báo cáo", level: 3 }),
    ).toBeInTheDocument();
    expect(container.querySelector("strong")).toHaveTextContent("DDoS");
    expect(container.querySelector("code")).toHaveTextContent("IAT");
    expect(container.querySelector("li")).toHaveTextContent("Kiểm tra log");
    expect(screen.getByRole("table")).toHaveTextContent("100%");
    expect(screen.getByRole("link", { name: "Tham khảo" })).toHaveAttribute(
        "rel",
        "noopener noreferrer",
    );
});

it("không thực thi HTML/URL script hoặc tải ảnh ngoài; chỉ dùng waterfall đúng mẫu", () => {
    const { container } = render(
        <MarkdownPreview
            files={{
                "waterfall.png": "/api/runs/example/cases/14/waterfall.png",
            }}
            text={
                '<script>alert(1)</script>\n\n<img src=x onerror="alert(1)">\n\n[Không an toàn](javascript:alert%281%29)\n\n![Ngoài](https://example.com/track.png)\n\n![Waterfall](waterfall.png)'
            }
        />,
    );
    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector("[onerror]")).toBeNull();
    expect(container.querySelector('a[href^="javascript:"]')).toBeNull();
    expect(container.querySelectorAll("img")).toHaveLength(1);
    expect(screen.getByRole("img", { name: "Waterfall" })).toHaveAttribute(
        "src",
        "/api/runs/example/cases/14/waterfall.png",
    );
    expect(screen.getByText("Ngoài")).toBeInTheDocument();
});
