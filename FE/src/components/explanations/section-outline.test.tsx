import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { SectionOutline } from "./section-outline";

it("tự sáng theo vị trí cuộn của main; nhấp mục lục không đổi URL/bước", async () => {
    let offset = 0;
    const sections = [
        { id: "stage-content", label: "SHAP" },
        { id: "case-files", label: "Tệp kết quả" },
        { id: "human-review", label: "Đánh giá thủ công" },
    ];
    const { container, unmount } = render(
        <main id="main-content" style={{ overflowY: "auto" }}>
            <SectionOutline sections={sections} />
            {sections.map((item) => (
                <section id={item.id} key={item.id} />
            ))}
        </main>,
    );
    const main = container.querySelector("main")!;
    main.getBoundingClientRect = () => ({ top: 50 }) as DOMRect;
    sections.forEach((item, index) => {
        container.querySelector(`#${item.id}`)!.getBoundingClientRect = () =>
            ({ top: 74 + index * 500 - offset }) as DOMRect;
    });
    await waitFor(() =>
        expect(screen.getByRole("link", { name: "SHAP" })).toHaveAttribute(
            "aria-current",
            "location",
        ),
    );
    offset = 500;
    fireEvent.scroll(main);
    expect(screen.getByRole("link", { name: "Tệp kết quả" })).toHaveAttribute(
        "aria-current",
        "location",
    );
    offset = 1000;
    fireEvent.scroll(main);
    expect(
        screen.getByRole("link", { name: "Đánh giá thủ công" }),
    ).toHaveAttribute("aria-current", "location");
    const url = location.href;
    main.scrollTo = vi.fn();
    vi.stubGlobal("matchMedia", () => ({ matches: true }));
    fireEvent.click(screen.getByRole("link", { name: "SHAP" }));
    expect(main.scrollTo).toHaveBeenCalledWith({
        top: -1000,
        behavior: "auto",
    });
    expect(location.href).toBe(url);
    unmount();
    vi.unstubAllGlobals();
});
