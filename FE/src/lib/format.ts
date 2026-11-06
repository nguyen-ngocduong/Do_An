export function number(value: number | null | undefined, digits = 0) {
    return value == null || !Number.isFinite(value)
        ? "—"
        : value.toLocaleString("vi-VN", { maximumFractionDigits: digits });
}
export function percent(value: number | null | undefined, digits = 2) {
    return value == null ? "—" : `${number(value * 100, digits)}%`;
}
export function seconds(value: number | null | undefined) {
    if (value == null || !Number.isFinite(value) || value < 0) return "—";
    if (value === 0) return "0 giây";
    if (value < 0.001) return `${number(value * 1_000_000, 2)} µs`;
    if (value < 1) return `${number(value * 1000, 2)} ms`;
    if (value < 60) return `${number(value, 2)} giây`;
    const rounded = Math.round(value * 10) / 10;
    const minutes = Math.floor(rounded / 60);
    const remaining = number(rounded % 60, 1);
    if (rounded < 3600) return `${minutes} phút ${remaining} giây`;
    return `${Math.floor(minutes / 60)} giờ ${minutes % 60} phút ${remaining} giây`;
}

export function csvDisplayValue(value: string, column: string) {
    if (!["value", "shap_value", "impact_percentage_points"].includes(column))
        return value;
    if (!value.trim()) return value;
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) return value;
    const digits = column === "impact_percentage_points" ? 4 : 6;
    if (parsed !== 0 && Math.abs(parsed) < 10 ** -digits)
        return parsed.toExponential(3);
    return number(parsed, digits);
}
export function rowName(row: number) {
    return `#${String(row).padStart(6, "0")}`;
}
export function time(value?: string) {
    return value ? new Date(value).toLocaleString("vi-VN") : "—";
}
const labels: Record<string, string> = {
    queued: "Đang xếp hàng",
    running: "Đang dự đoán",
    paused: "Tạm dừng",
    stopped: "Đã dừng",
    interrupted: "Bị gián đoạn",
    failed: "Thất bại",
    completed: "Hoàn tất",
    partial: "Hoàn tất một phần",
    not_requested: "Chưa yêu cầu",
    shap_running: "Đang tính SHAP",
    gemini_running: "Đang gọi Gemini",
    accepted: "Đạt kiểm tra tự động",
    gemini_disabled: "Không dùng Gemini",
    not_configured: "Chưa cấu hình Gemini",
    pending: "Chờ xử lý",
    api_error: "Lỗi API",
    request_error: "Lỗi kết nối",
    invalid_evidence: "Không đạt bằng chứng",
    needs_text_review: "Bản nháp cần sửa",
    not_completed: "Chưa hoàn tất",
    new: "Mới",
    acknowledged: "Đã tiếp nhận",
    closed: "Đã đóng",
};
export const statusLabel = (status?: string) =>
    status ? labels[status] || "Trạng thái chưa xác định" : "Chưa có dữ liệu";
