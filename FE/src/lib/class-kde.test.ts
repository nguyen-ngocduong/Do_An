import { expect, it } from "vitest";
import { classKde } from "./class-kde";
import { CLASS_NAMES, type ClassName } from "@/types/model";

it("classKde trả về rỗng khi dữ liệu null, undefined hoặc toàn số 0", () => {
    expect(classKde(null)).toEqual({ points: [], bandwidth: null });
    expect(classKde(undefined)).toEqual({ points: [], bandwidth: null });
    expect(classKde({})).toEqual({ points: [], bandwidth: null });
    expect(classKde([0, 0, 0, 0, 0, 0, 0, 0])).toEqual({
        points: [],
        bandwidth: null,
    });
});

it("classKde trả về rỗng khi tổng số mẫu < 2 hoặc ít hơn 2 lớp dương", () => {
    // Chỉ có 1 mẫu đơn
    expect(classKde({ Normal: 1 })).toEqual({ points: [], bandwidth: null });

    // Nhiều mẫu nhưng dồn hết vào 1 lớp duy nhất
    expect(classKde({ DDoS: 100 })).toEqual({ points: [], bandwidth: null });
    expect(classKde({ "Web-Based": 50 })).toEqual({
        points: [],
        bandwidth: null,
    });
});

it("classKde tính toán chính xác theo công thức giải tích với hai lớp đối xứng", () => {
    // Normal (vị trí 0): 10 mẫu, DDoS (vị trí 2): 10 mẫu
    // N = 20, mean = (10*0 + 10*2)/20 = 1.0
    // sampleVariance = (10*(0-1)^2 + 10*(2-1)^2) / 19 = 20 / 19 ≈ 1.05263158
    // std = sqrt(20/19) ≈ 1.02597835
    // Scott bandwidth: max(0.5, std * 20^(-0.2)) = max(0.5, 1.02597835 * 0.54928027) = max(0.5, 0.5635496) ≈ 0.56355
    const res = classKde({ Normal: 10, DDoS: 10 });

    expect(res.bandwidth).not.toBeNull();
    expect(res.bandwidth!).toBeCloseTo(0.56355, 4);

    // Đúng 121 điểm trong khoảng [-0.5, 7.5]
    expect(res.points).toHaveLength(121);
    expect(res.points[0].x).toBeCloseTo(-0.5, 6);
    expect(res.points[120].x).toBeCloseTo(7.5, 6);

    // Không có giá trị NaN hoặc âm
    for (const p of res.points) {
        expect(Number.isFinite(p.x)).toBe(true);
        expect(Number.isFinite(p.y)).toBe(true);
        expect(p.y).toBeGreaterThanOrEqual(0);
    }

    // Tính chất đối xứng qua tâm mean = 1.0:
    // x = 0 (chỉ số k = 7.5 -> k=7, 8) và x = 2
    // Đỉnh tại x = 0 và x = 2 xấp xỉ ngang nhau
    const pointAt0 = res.points.find((p) => Math.abs(p.x - 0) < 0.04);
    const pointAt2 = res.points.find((p) => Math.abs(p.x - (2 - pointAt0!.x)) < 1e-9);
    expect(pointAt0).toBeDefined();
    expect(pointAt2).toBeDefined();
    expect(pointAt0!.y).toBeCloseTo(pointAt2!.y, 2);
});

it("băng thông luôn được chặn dưới bởi ngưỡng tối thiểu 0.5", () => {
    // Dữ liệu cực kỳ dồn cục ở 2 lớp cạnh nhau với số mẫu lớn: std * N^(-0.2) < 0.5
    // Normal: 5000, BruteForce: 5000
    // mean = 0.5, std = 0.500025, N = 10000 -> std * 10000^(-0.2) = 0.500025 * 0.158489 ≈ 0.0792 < 0.5
    const res = classKde({ Normal: 5000, BruteForce: 5000 });
    expect(res.bandwidth).toBe(0.5);
});

it("khớp đối chiếu SciPy trên 2.000 mẫu mã hóa theo thứ tự nhãn cố định", () => {
    // scipy.stats.gaussian_kde(np.repeat(np.arange(8), counts)), băng thông tối thiểu 0.5.
    const result = classKde([81, 2, 1259, 454, 150, 26, 27, 1]);
    expect(result.bandwidth).toBe(0.5);
    const reference = [
        [0, 39.220728333782056],
        [8, 65.17040917469222],
        [38, 1058.4560545405498],
        [68, 165.69389767454442],
        [120, 0.7233385754381247],
    ];
    for (const [index, expected] of reference) {
        expect(result.points[index].y).toBeCloseTo(expected, 8);
    }
});

it("ổn định với tần số rất lớn mà không mở rộng mảng mẫu trong bộ nhớ", () => {
    const hugeCounts: Record<ClassName, number> = {
        Normal: 1_000_000_000,
        BruteForce: 0,
        DDoS: 2_000_000_000,
        DoS: 500_000_000,
        Mirai: 0,
        Recon: 0,
        Spoofing: 0,
        "Web-Based": 100_000_000,
    };

    const res = classKde(hugeCounts);

    // Tần số hàng tỷ mẫu vẫn chỉ sinh 121 điểm, không mở rộng từng mẫu.
    expect(res.points).toHaveLength(121);
    expect(res.bandwidth).not.toBeNull();
    expect(Number.isFinite(res.bandwidth!)).toBe(true);
    for (const p of res.points) {
        expect(Number.isFinite(p.y)).toBe(true);
        expect(p.y).toBeGreaterThanOrEqual(0);
    }
});

it("xử lý ổn định khi nhận mảng số hoặc nhãn có ký tự đặc biệt Web-Based", () => {
    // Truyền dạng mảng
    const arrCounts = [10, 20, 30, 40, 50, 60, 70, 80];
    const resArr = classKde(arrCounts);
    expect(resArr.points).toHaveLength(121);
    expect(resArr.bandwidth).toBeGreaterThan(0.5);

    // Kiểm tra lớp "Web-Based" có mặt trong CLASS_NAMES
    expect(CLASS_NAMES).toContain("Web-Based");
    const countsWithWebBased: Record<ClassName, number> = Object.fromEntries(
        CLASS_NAMES.map((name) => [name, 0]),
    ) as Record<ClassName, number>;
    countsWithWebBased.Normal = 10;
    countsWithWebBased["Web-Based"] = 15;
    const resObj = classKde(countsWithWebBased);
    expect(resObj.points).toHaveLength(121);
    expect(resObj.bandwidth).not.toBeNull();
});
