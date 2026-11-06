import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { detail } from "@/mocks/evidence";
import { GeminiView, ShapView } from "./evidence";
import { number, percent, seconds } from "@/lib/format";
it("phân biệt null, số 0 và đơn vị", () => {
    expect(number(null)).toBe("—");
    expect(number(0)).toBe("0");
    expect(seconds(undefined)).toBe("—");
    expect(percent(0.125)).toBe("12,5%");
});
it("render bản nháp Gemini dưới dạng văn bản, không thực thi HTML", () => {
    const { container } = render(<GeminiView detail={detail} />);
    expect(screen.getByText(/BẢN NHÁP CẦN SỬA/)).toBeInTheDocument();
    expect(screen.getByText(detail.gemini!.tom_tat)).toBeInTheDocument();
    expect(container.querySelector("script")).toBeNull();
});
it("waterfall giữ đóng góp âm, giá trị thiếu và phần ngoài top5", () => {
    const { container } = render(<ShapView item={detail.explanation} />);
    expect(screen.getByText("Giá trị: Thiếu")).toBeInTheDocument();
    expect(screen.getByText("Giá trị: 0")).toBeInTheDocument();
    expect(container.querySelectorAll(".negative-bar")).toHaveLength(1);
    expect(container.querySelectorAll(".waterfall-bar")).toHaveLength(3);
    expect(screen.getByText("Bảo toàn đạt")).toBeInTheDocument();
    expect(screen.getByText("41 đặc trưng còn lại")).toBeInTheDocument();
});
it("xem nhanh chỉ mở toàn bộ diễn giải khi bấm Xem thêm, đổi mẫu tự thu gọn", () => {
    const { rerender } = render(<GeminiView detail={detail} compact />);
    expect(
        screen.queryByText("So sánh hai lớp đứng đầu"),
    ).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Xem thêm" }));
    expect(screen.getByText("So sánh hai lớp đứng đầu")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Thu gọn" })).toHaveAttribute(
        "aria-expanded",
        "true",
    );
    rerender(<GeminiView detail={{ ...detail, row_index: 15 }} compact />);
    expect(
        screen.queryByText("So sánh hai lớp đứng đầu"),
    ).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Xem thêm" })).toHaveAttribute(
        "aria-expanded",
        "false",
    );
});
