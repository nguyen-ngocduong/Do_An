import { StrictMode } from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import { detail } from "@/mocks/evidence";
import { getExplanation, requestExplanations } from "@/lib/api/explanations";
import { ExplanationInspector } from "./explanation-inspector";
const context = vi.hoisted(() => ({
    search: new URLSearchParams(),
    replace: vi.fn(),
    notify: vi.fn(),
}));
vi.mock("next/navigation", () => ({
    useSearchParams: () => context.search,
    usePathname: () => "/runs/" + "a".repeat(32) + "/rows/14",
    useRouter: () => ({ replace: context.replace }),
}));
vi.mock("@/store/ui-store", () => ({
    useUi: () => ({ notify: context.notify, metadata: { data: undefined } }),
}));
vi.mock("@/lib/api/runs", () => ({
    getRun: vi.fn(async () => ({
        id: "a".repeat(32),
        total_rows: 50,
        status: "completed",
        mode: "batch",
    })),
}));
vi.mock("@/lib/api/predictions", () => ({
    getInput: vi.fn(async () => ({ features: { IAT: null, Rate: 0 } })),
    getPredictions: vi.fn(async () => ({
        items: [
            {
                row_index: 14,
                predicted_class: "Web-Based",
                predicted_probability: 0.6,
                probabilities: { Normal: 0.4, "Web-Based": 0.6 },
            },
        ],
    })),
}));
vi.mock("@/lib/api/explanations", () => ({
    getExplanation: vi.fn(async () => detail),
    requestExplanations: vi.fn(async () => ({ items: [] })),
}));
vi.mock("./human-review", () => ({ HumanReview: () => null }));
beforeEach(() => {
    vi.clearAllMocks();
    context.search = new URLSearchParams();
});
it("StrictMode, đổi tab chỉ GET; link Basic được chuẩn hóa về Kỹ thuật", async () => {
    const { rerender } = render(
        <StrictMode>
            <ExplanationInspector id={detail.run_id} index={14} />
        </StrictMode>,
    );
    await screen.findByText("Bảo toàn đạt");
    expect(requestExplanations).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("tab", { name: "Metadata" }));
    expect(context.replace).toHaveBeenCalled();
    expect(requestExplanations).not.toHaveBeenCalled();
    context.search = new URLSearchParams("audience=basic&tab=input");
    rerender(
        <StrictMode>
            <ExplanationInspector id={detail.run_id} index={14} />
        </StrictMode>,
    );
    await waitFor(() =>
        expect(getExplanation).toHaveBeenCalledWith(
            detail.run_id,
            14,
            "technical",
            expect.any(AbortSignal),
        ),
    );
    expect(context.replace).toHaveBeenCalledWith(
        expect.stringContaining("audience=technical"),
        { scroll: false },
    );
    expect(screen.queryByLabelText("Mức diễn giải")).not.toBeInTheDocument();
    expect(requestExplanations).not.toHaveBeenCalled();
});
it("chỉ nút yêu cầu gửi một POST với đúng dòng và lựa chọn Gemini", async () => {
    render(<ExplanationInspector id={detail.run_id} index={14} />);
    const button = await screen.findByRole("button", {
        name: "Yêu cầu / dùng lại kết quả",
    });
    fireEvent.click(screen.getByRole("checkbox", { name: "Dùng Gemini" }));
    fireEvent.click(button);
    await waitFor(() => expect(requestExplanations).toHaveBeenCalledTimes(1));
    expect(requestExplanations).toHaveBeenCalledWith(detail.run_id, {
        row_indices: [14],
        audience_level: "technical",
        use_gemini: true,
        retry_gemini: false,
    });
});
