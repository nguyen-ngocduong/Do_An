import type { DashboardDay } from "@/types/dashboard";

export interface KdePoint {
    x: number;
    y: number;
}

export interface ActivityKdeResult {
    points: KdePoint[];
    bandwidth: number | null;
}

/**
 * Ước lượng mật độ kernel Gaussian (KDE) theo số lượt xử lý mỗi ngày.
 *
 * Thuật toán:
 * - N = tổng số mẫu (sum count)
 * - Mỗi ngày i (0 .. days.length - 1) có số mẫu count c_i = days[i].total_rows
 * - Điểm trung bình: mean = sum(c_i * i) / N
 * - Phương sai mẫu Bessel: var = sum(c_i * (i - mean)^2) / (N - 1)
 * - Độ lệch chuẩn: std = sqrt(var)
 * - Băng thông theo quy tắc Scott: h = max(0.5, std * N^(-0.2))
 * - Điều kiện ước lượng: ít nhất 2 ngày có count > 0 và tổng số mẫu N >= 2
 * - Grid 121 điểm từ x = -0.5 tới x = days.length - 0.5
 * - Cường độ: intensity(x) = sum(c_i * exp(-0.5 * ((x - i)/h)^2) / (h * sqrt(2 * PI)))
 *   đơn vị lượt/ngày tương ứng bin 1 ngày.
 */
export function activityKde(days: DashboardDay[]): ActivityKdeResult {
    if (!days || days.length < 2) {
        return { points: [], bandwidth: null };
    }

    let n = 0;
    let positiveDays = 0;
    for (let i = 0; i < days.length; i++) {
        const count = days[i].total_rows;
        if (count > 0) {
            n += count;
            positiveDays++;
        }
    }

    if (positiveDays < 2 || n < 2) {
        return { points: [], bandwidth: null };
    }

    let mean = 0;
    for (let i = 0; i < days.length; i++) {
        const count = days[i].total_rows;
        if (count > 0) {
            mean += (count * i) / n;
        }
    }

    let sampleVariance = 0;
    for (let i = 0; i < days.length; i++) {
        const count = days[i].total_rows;
        if (count > 0) {
            const diff = i - mean;
            sampleVariance += count * diff * diff;
        }
    }
    sampleVariance = sampleVariance / (n - 1);

    const std = Math.sqrt(Math.max(0, sampleVariance));
    const bandwidth = Math.max(0.5, std * Math.pow(n, -0.2));

    const numPoints = 121;
    const xMin = -0.5;
    const xMax = days.length - 0.5;
    const step = (xMax - xMin) / (numPoints - 1);

    const invH = 1 / bandwidth;
    const normFactor = 1 / (bandwidth * Math.sqrt(2 * Math.PI));

    const points: KdePoint[] = new Array(numPoints);

    for (let k = 0; k < numPoints; k++) {
        const x = xMin + k * step;
        let y = 0;
        for (let i = 0; i < days.length; i++) {
            const count = days[i].total_rows;
            if (count > 0) {
                const u = (x - i) * invH;
                y += count * normFactor * Math.exp(-0.5 * u * u);
            }
        }
        points[k] = { x, y };
    }

    return { points, bandwidth };
}
