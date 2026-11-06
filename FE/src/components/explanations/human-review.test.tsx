import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import { HumanReview } from "./human-review";
import { getReview, saveReview, type ReviewEnvelope } from "@/lib/api/reviews";

vi.mock("@/lib/api/reviews", async (original) => ({
    ...(await original<typeof import("@/lib/api/reviews")>()),
    getReview: vi.fn(),
    saveReview: vi.fn(),
}));
vi.mock("@/store/ui-store", () => ({ useUi: () => ({ notify: vi.fn() }) }));
const runId = "a".repeat(32);
let response: ReviewEnvelope;
beforeEach(() => {
    vi.clearAllMocks();
    response = {
        review: null,
        stale: false,
        context: {
            run_id: runId,
            row_index: 14,
            audience_level: "technical",
            predicted_class: "Web-Based",
            predicted_probability: 0.6,
            evidence_signature: "b".repeat(64),
            file_sha256: {},
        },
    };
    vi.mocked(getReview).mockImplementation(async () => response);
    vi.mocked(saveReview).mockImplementation(
        async (_id, _row, draft, signature) => {
            response = {
                ...response,
                review: {
                    ...draft,
                    evidence_signature: signature,
                    reviewer_username: "tester",
                    updated_at: "2026-11-02T00:00:00Z",
                },
            };
            return response;
        },
    );
});
it("không tự chấm/lưu; giữ bản nháp khi bằng chứng đổi và chỉ lưu sau xác nhận", async () => {
    const { rerender } = render(
        <HumanReview id={runId} row={14} revision="old" />,
    );
    const name = await screen.findByLabelText("Tên người đánh giá");
    expect(screen.getByLabelText("Nhận định về nhãn dự đoán")).toHaveValue(
        "not_reviewed",
    );
    expect(screen.getByLabelText("Độ rõ ràng của diễn giải")).toHaveValue("");
    expect(screen.getByRole("button", { name: "Lưu đánh giá" })).toBeDisabled();
    fireEvent.change(name, { target: { value: "Người kiểm tra" } });
    fireEvent.change(
        screen.getByLabelText("Nhận xét và bằng chứng đối chiếu"),
        { target: { value: "Cần đối chiếu nhật ký." } },
    );
    rerender(<HumanReview id={runId} row={14} revision="new" />);
    expect(name).toHaveValue("Người kiểm tra");
    expect(saveReview).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("checkbox"));
    fireEvent.click(screen.getByRole("button", { name: "Lưu đánh giá" }));
    await waitFor(() => expect(saveReview).toHaveBeenCalledTimes(1));
    expect(saveReview).toHaveBeenCalledWith(
        runId,
        14,
        expect.objectContaining({
            reviewer_name: "Người kiểm tra",
            prediction_assessment: "not_reviewed",
            explanation_clarity: null,
        }),
        "b".repeat(64),
    );
    await screen.findByText(/Đã lưu bởi tester/);
    expect(
        screen.getByRole("button", { name: /Tải bản đánh giá đã lưu/ }),
    ).toBeInTheDocument();
});
