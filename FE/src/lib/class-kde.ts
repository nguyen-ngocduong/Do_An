import { CLASS_NAMES, type ClassName } from "@/types/model";

export interface ClassKdePoint {
    x: number;
    y: number;
}

export interface ClassKdeResult {
    points: ClassKdePoint[];
    bandwidth: number | null;
}

/**
 * Ước lượng mật độ kernel Gaussian (KDE minh họa) theo số lượng mẫu của tám lớp mô hình.
 *
 * Bản chất dữ liệu phân loại:
 * - Tám nhãn lớp mô hình là biến định danh không có thứ tự tự nhiên (unordered categorical data).
 * - Thứ tự nhãn được cố định từ 0 đến 7 theo CLASS_NAMES:
 *   0: Normal, 1: BruteForce, 2: DDoS, 3: DoS, 4: Mirai, 5: Recon, 6: Spoofing, 7: Web-Based.
 * - Số đếm mỗi lớp (counts) được mã hóa như tần số lặp tại vị trí chỉ số 0..7.
 * - Đường làm mượt Gaussian này chỉ nhằm mục đích minh họa trực quan hình dáng phân bố
 *   tổng quan qua các cột nhãn, KHÔNG biểu thị chuỗi thời gian, hàm mật độ xác suất chuẩn tắc,
 *   hay độ tin cậy được hiệu chuẩn.
 *
 * Thuật toán làm mượt Gaussian (Real Gaussian-kernel smoothing):
 * - N = tổng số mẫu (sum c_i). Không mở rộng mảng mẫu riêng lẻ (tiết kiệm bộ nhớ O(1)).
 * - Kỳ vọng mẫu: mean = sum(c_i * i) / N.
 * - Phương sai mẫu Bessel: sampleVariance = sum(c_i * (i - mean)^2) / (N - 1).
 * - Băng thông theo quy tắc Scott: bandwidth = max(0.5, sqrt(sampleVariance) * N^(-1/5)).
 * - Đánh giá 121 điểm đều trong đoạn [-0.5, 7.5].
 * - Cường độ: intensity(x) = sum(c_i * exp(-0.5 * ((x - i) / h)^2) / (h * sqrt(2 * PI))).
 *   Đơn vị cường độ khớp với số mẫu trên bin 1 nhãn (cùng thang đo trục Y với cột số đếm).
 * - Điều kiện vẽ: cần N >= 2 và ít nhất 2 lớp có số mẫu dương (> 0).
 *   Nếu không đủ điều kiện, trả về mảng rỗng để giao diện hiển thị thông báo.
 */
export function classKde(
    counts?: Record<ClassName, number> | Record<string, number> | number[] | null,
): ClassKdeResult {
    if (!counts) {
        return { points: [], bandwidth: null };
    }

    // Trích xuất 8 giá trị số đếm theo đúng thứ tự CLASS_NAMES
    const classValues = new Array<number>(CLASS_NAMES.length).fill(0);
    if (Array.isArray(counts)) {
        for (let i = 0; i < Math.min(counts.length, CLASS_NAMES.length); i++) {
            const val = counts[i];
            if (typeof val === "number" && Number.isFinite(val) && val > 0) {
                classValues[i] = val;
            }
        }
    } else if (typeof counts === "object") {
        for (let i = 0; i < CLASS_NAMES.length; i++) {
            const name = CLASS_NAMES[i];
            const val = counts[name];
            if (typeof val === "number" && Number.isFinite(val) && val > 0) {
                classValues[i] = val;
            }
        }
    }

    let n = 0;
    let positiveClasses = 0;
    for (let i = 0; i < classValues.length; i++) {
        const count = classValues[i];
        if (count > 0) {
            n += count;
            positiveClasses++;
        }
    }

    // Yêu cầu tối thiểu: N >= 2 và ít nhất 2 lớp có mẫu để tính phương sai
    if (positiveClasses < 2 || n < 2) {
        return { points: [], bandwidth: null };
    }

    let mean = 0;
    for (let i = 0; i < classValues.length; i++) {
        const count = classValues[i];
        if (count > 0) {
            mean += (count * i) / n;
        }
    }

    let sampleVariance = 0;
    for (let i = 0; i < classValues.length; i++) {
        const count = classValues[i];
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
    const xMax = 7.5;
    const step = (xMax - xMin) / (numPoints - 1);

    const invH = 1 / bandwidth;
    const normFactor = 1 / (bandwidth * Math.sqrt(2 * Math.PI));

    const points: ClassKdePoint[] = new Array(numPoints);

    for (let k = 0; k < numPoints; k++) {
        const x = xMin + k * step;
        let y = 0;
        for (let i = 0; i < classValues.length; i++) {
            const count = classValues[i];
            if (count > 0) {
                const u = (x - i) * invH;
                y += count * normFactor * Math.exp(-0.5 * u * u);
            }
        }
        points[k] = { x, y };
    }

    return { points, bandwidth };
}
