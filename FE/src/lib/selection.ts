// Checkbox chọn mẫu độc lập với dòng đang xem nhanh.
export function toggleSelection(selected: number[], row: number, limit = 50) {
    if (selected.includes(row))
        return selected.filter((value) => value !== row);
    if (selected.length >= limit) return selected;
    return [...selected, row];
}
export function selectPage(
    selected: number[],
    rows: number[],
    checked: boolean,
    limit = 50,
) {
    if (!checked) return selected.filter((row) => !rows.includes(row));
    return [...new Set([...selected, ...rows])].slice(0, limit);
}
