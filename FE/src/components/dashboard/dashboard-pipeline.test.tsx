import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DashboardPipeline } from "./dashboard-pipeline";
import type { DashboardSummary } from "@/types/dashboard";
import type { RunInfo } from "@/types/run";

function makeSummary(
    overrides: Partial<DashboardSummary> = {},
): DashboardSummary {
    return {
        generated_at: "2026-11-04T12:00:00Z",
        period: "7d",
        timezone: "Asia/Ho_Chi_Minh",
        start_date: "2026-10-28",
        end_date: "2026-11-04",
        trend_start_date: "2026-10-28",
        trend_end_date: "2026-11-04",
        audience_level: "technical",
        selected_run: null,
        metrics: {
            predicted_rows: 100,
            normal_rows: 80,
            suspected_rows: 20,
            suspected_percentage: 20,
            pending_alerts: 5,
            shap_rows: 45,
            run_count: 2,
        },
        class_counts: {
            Normal: 80,
            BruteForce: 0,
            DDoS: 15,
            DoS: 5,
            Mirai: 0,
            Recon: 0,
            Spoofing: 0,
            "Web-Based": 0,
        },
        daily_activity: [],
        alert_counts: {
            acknowledged: 2,
            closed: 1,
            new: 2,
        },
        explanation_counts: {
            not_requested: 55,
            queued: 5,
            shap_running: 5,
            gemini_running: 5,
            completed: 25,
            partial: 2,
            failed: 2,
            interrupted: 1,
        },
        gemini_counts: {
            accepted: 30,
            api_error: 2,
        },
        review_counts: {
            not_reviewed: 70,
            agree: 18,
            disagree: 2,
            uncertain: 10,
        },
        saved_reviews: 30,
        proposed_labels: 3,
        recent_runs: [],
        recent_alerts: [],
        run_options: [],
        available_run_count: 2,
        ...overrides,
    };
}

describe("DashboardPipeline", () => {
    it("hiển thị chính xác số liệu ba phần phẳng từ API và progressbar aria", () => {
        const summary = makeSummary();
        const { container } = render(<DashboardPipeline data={summary} />);

        // Ba phần phẳng
        expect(
            screen.getByRole("heading", { name: "Bằng chứng SHAP" }),
        ).toBeInTheDocument();
        expect(
            screen.getByRole("heading", { name: "Diễn giải Gemini", level: 3 }),
        ).toBeInTheDocument();
        expect(
            screen.getByRole("heading", { name: "Đánh giá của bạn" }),
        ).toBeInTheDocument();

        // Số liệu đạt / tổng
        expect(screen.getByText("45 / 100")).toBeInTheDocument();
        expect(screen.getAllByText("30 / 100")).toHaveLength(2); // Gemini accepted và saved reviews

        // Nhãn chỉ định
        expect(screen.getAllByText("Đạt kiểm tra tự động")).toHaveLength(2);
        expect(screen.getByText("Phiếu đã lưu")).toBeInTheDocument();

        // Progress bar aria
        const progressBars = container.querySelectorAll(
            '.meter[role="progressbar"]',
        );
        expect(progressBars).toHaveLength(3);
        expect(progressBars[0].getAttribute("aria-valuenow")).toBe("45");
        expect(progressBars[0].getAttribute("aria-valuemax")).toBe("100");
    });

    it("xử lý tỷ lệ 0 khi không có mẫu mà không gây NaN", () => {
        const summary = makeSummary({
            metrics: {
                predicted_rows: 0,
                normal_rows: 0,
                suspected_rows: 0,
                suspected_percentage: null,
                pending_alerts: 0,
                shap_rows: 0,
                run_count: 0,
            },
            gemini_counts: {},
            saved_reviews: 0,
        });

        const { container } = render(<DashboardPipeline data={summary} />);
        expect(container.innerHTML).not.toMatch(/NaN|Infinity/);

        const progressBars = container.querySelectorAll(
            '.meter[role="progressbar"]',
        );
        expect(progressBars).toHaveLength(3);
        progressBars.forEach((bar) => {
            expect(bar.getAttribute("aria-valuenow")).toBe("0");
            expect(bar.getAttribute("aria-valuemax")).toBe("100");
            const span = bar.querySelector("span");
            expect(span?.style.width).toBe("0%");
        });
    });

    it("giữ toàn bộ thống kê chi tiết trong disclosure", () => {
        const summary = makeSummary();
        const { container } = render(<DashboardPipeline data={summary} />);

        const details = container.querySelector(
            "details.dashboard-pipeline-details",
        );
        expect(details).toBeInTheDocument();

        // Tác vụ giải thích
        expect(details).toHaveTextContent("Chưa yêu cầu");
        expect(details).toHaveTextContent("55");
        expect(details).toHaveTextContent("Đang chờ / xử lý");
        expect(details).toHaveTextContent("15"); // 5 + 5 + 5
        expect(details).toHaveTextContent("Hoàn tất");
        expect(details).toHaveTextContent("25");
        expect(details).toHaveTextContent("Một phần / lỗi / gián đoạn");
        expect(details).toHaveTextContent("5"); // 2 + 2 + 1

        // Diễn giải Gemini
        expect(details).toHaveTextContent("30");
        expect(details).toHaveTextContent("2");

        // Đánh giá thủ công
        expect(details).toHaveTextContent("Chưa đánh giá dự đoán");
        expect(details).toHaveTextContent("70");
        expect(details).toHaveTextContent("Đồng ý / Không đồng ý");
        expect(details).toHaveTextContent("18 / 2");
        expect(details).toHaveTextContent("Chưa chắc");
        expect(details).toHaveTextContent("10");
        expect(details).toHaveTextContent("Đề xuất nhãn khác");
        expect(details).toHaveTextContent("3");
    });

    it("trỏ đúng link lần chạy đang chọn hoặc gần nhất, và không hiển thị link nếu không có lần chạy", () => {
        // Case 1: có selected_run
        const summarySelected = makeSummary({
            selected_run: {
                id: "a".repeat(32),
                filename: "traffic_test.csv",
                created_at: "2026-11-04T10:00:00Z",
            },
        });
        const view1 = render(<DashboardPipeline data={summarySelected} />);
        const link1 = view1.container.querySelector("a.pipeline-run-link");
        expect(link1).toBeInTheDocument();
        expect(link1).toHaveTextContent("Xem lần chạy đã chọn");
        expect(link1?.getAttribute("href")).toBe(
            `/runs/${"a".repeat(32)}/predictions`,
        );

        // Case 2: không có selected_run nhưng có recent_runs
        const dummyRun: RunInfo = {
            id: "b".repeat(32),
            filename: "recent.csv",
            created_at: "2026-11-04T09:00:00Z",
            updated_at: "2026-11-04T09:10:00Z",
            status: "completed",
            mode: "batch",
            total_rows: 50,
            processed_rows: 50,
            interval_seconds: 0,
            message: "",
            signature: "fixture",
        };
        const summaryRecent = makeSummary({
            selected_run: null,
            recent_runs: [dummyRun],
        });
        const view2 = render(<DashboardPipeline data={summaryRecent} />);
        const link2 = view2.container.querySelector("a.pipeline-run-link");
        expect(link2).toBeInTheDocument();
        expect(link2).toHaveTextContent("Xem lần chạy gần nhất");
        expect(link2?.getAttribute("href")).toBe(
            `/runs/${"b".repeat(32)}/predictions`,
        );

        // Case 3: không có run nào
        const summaryEmpty = makeSummary({
            selected_run: null,
            recent_runs: [],
        });
        const view3 = render(<DashboardPipeline data={summaryEmpty} />);
        expect(
            view3.container.querySelector("a.pipeline-run-link"),
        ).not.toBeInTheDocument();
    });
});
