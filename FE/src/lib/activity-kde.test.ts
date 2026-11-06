import { describe, expect, it } from "vitest";
import { activityKde } from "./activity-kde";
import type { DashboardDay } from "@/types/dashboard";

function makeDays(counts: number[]): DashboardDay[] {
    return counts.map((count, i) => ({
        date: `2026-11-${String(i + 1).padStart(2, "0")}`,
        total_rows: count,
        normal_rows: count,
        suspected_rows: 0,
    }));
}

describe("activityKde", () => {
    it("trả về rỗng khi không có ngày hoặc chỉ có 1 ngày", () => {
        expect(activityKde([])).toEqual({ points: [], bandwidth: null });
        expect(activityKde(makeDays([100]))).toEqual({
            points: [],
            bandwidth: null,
        });
    });

    it("trả về rỗng khi toàn bộ số liệu bằng 0 hoặc chỉ có 1 ngày dương (one day burst)", () => {
        expect(activityKde(makeDays([0, 0, 0]))).toEqual({
            points: [],
            bandwidth: null,
        });
        expect(activityKde(makeDays([0, 50, 0, 0]))).toEqual({
            points: [],
            bandwidth: null,
        });
    });

    it("ước lượng khi có từ 2 ngày dương và N >= 2", () => {
        const result = activityKde(makeDays([10, 20]));
        expect(result.bandwidth).not.toBeNull();
        expect(result.bandwidth).toBeGreaterThanOrEqual(0.5);
        expect(result.points).toHaveLength(121);
        expect(result.points[0].x).toBeCloseTo(-0.5);
        expect(result.points[120].x).toBeCloseTo(1.5);

        for (const pt of result.points) {
            expect(Number.isFinite(pt.x)).toBe(true);
            expect(Number.isFinite(pt.y)).toBe(true);
            expect(pt.y).toBeGreaterThanOrEqual(0);
        }
    });

    it("đối xứng hoàn hảo khi phân bố số liệu theo ngày đối xứng", () => {
        const result = activityKde(makeDays([10, 30, 50, 30, 10]));
        expect(result.points).toHaveLength(121);
        const pts = result.points;
        for (let i = 0; i < 60; i++) {
            expect(pts[i].y).toBeCloseTo(pts[120 - i].y, 6);
        }
    });

    it("tính toán đúng giá trị giải tích lý thuyết phân bố chuẩn", () => {
        const days = makeDays([1, 1]); // N=2, indices 0, 1
        const result = activityKde(days);
        expect(result.bandwidth).not.toBeNull();
        const h = result.bandwidth!;
        // var = ((0-0.5)^2 + (1-0.5)^2)/(2-1) = 0.5; h = max(0.5, sqrt(0.5)*2^(-0.2))
        const expectedH = Math.max(0.5, Math.sqrt(0.5) * Math.pow(2, -0.2));
        expect(h).toBeCloseTo(expectedH, 6);

        // Tại x = 0.5 (trung tâm, index 60 trong 121 điểm từ -0.5 tới 1.5)
        const centerPt = result.points[60];
        expect(centerPt.x).toBeCloseTo(0.5);
        const u = 0.5 / h;
        const normFactor = 1 / (h * Math.sqrt(2 * Math.PI));
        const expectedY = 2 * normFactor * Math.exp(-0.5 * u * u);
        expect(centerPt.y).toBeCloseTo(expectedY, 6);
    });

    it("xử lý số liệu lớn (counts large) an toàn, không tràn bộ nhớ và không tạo NaN", () => {
        const largeDays = makeDays([5_000_000, 10_000_000, 2_000_000]);
        const result = activityKde(largeDays);
        expect(result.bandwidth).toBeGreaterThanOrEqual(0.5);
        expect(result.points).toHaveLength(121);
        for (const pt of result.points) {
            expect(Number.isNaN(pt.y)).toBe(false);
            expect(Number.isFinite(pt.y)).toBe(true);
            expect(pt.y).toBeGreaterThanOrEqual(0);
        }
    });
});

// SciPy gaussian_kde(np.repeat([0, 2], [10, 10])) * 20, tính độc lập trong lượt Codex review.
it("khớp SciPy trên các quan sát lặp theo số lượt ngày", () => {
    const result = activityKde(makeDays([10, 0, 10]));
    expect(result.bandwidth).toBeCloseTo(0.563549667943491, 12);
    expect(result.points[60].x).toBeCloseTo(1, 12);
    expect(result.points[60].y).toBeCloseTo(2.9327128722832714, 10);
});
