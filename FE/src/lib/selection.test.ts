import { expect, it } from "vitest";
import { selectPage, toggleSelection } from "./selection";
import { pageOffset, safeReturn } from "./navigation";
it("chọn/bỏ chọn dòng theo row_index, không sửa mảng cũ", () => {
    const before = [2, 14];
    expect(toggleSelection(before, 14)).toEqual([2]);
    expect(toggleSelection(before, 0)).toEqual([2, 14, 0]);
    expect(before).toEqual([2, 14]);
});
it("chọn tất cả trang không nhân đôi và không xóa lựa chọn trang khác", () => {
    expect(selectPage([0, 20], [0, 1, 2], true)).toEqual([0, 20, 1, 2]);
    expect(selectPage([0, 1, 20], [0, 1, 2], false)).toEqual([20]);
});
it("giới hạn 50 trên nhiều trang và cho phép bỏ chọn khi đủ", () => {
    const full = Array.from({ length: 50 }, (_, i) => i);
    expect(toggleSelection(full, 50)).toHaveLength(50);
    expect(selectPage(full, [51, 52], true)).toHaveLength(50);
    expect(toggleSelection(full, 0)).toHaveLength(49);
});
it("offset khác row_index, từ chối số âm/lẻ; return chỉ trong ứng dụng", () => {
    for (const value of ["-1", "1.5", "NaN"]) expect(pageOffset(value)).toBe(0);
    expect(pageOffset("20")).toBe(20);
    expect(safeReturn("https://outside.invalid", "/runs")).toBe("/runs");
    expect(safeReturn("/alerts?alert=2", "/runs")).toBe("/alerts?alert=2");
});
