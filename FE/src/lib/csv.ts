// Đọc CSV có dấu phẩy, xuống dòng trong chuỗi và dấu nháy kép đã escape.
export function parseCsv(text: string): string[][] {
    const rows: string[][] = [];
    let row: string[] = [];
    let field = "";
    let quoted = false;
    const input = text.replace(/^\uFEFF/, "");
    for (let i = 0; i < input.length; i++) {
        const char = input[i];
        if (char === '"') {
            if (quoted && input[i + 1] === '"') {
                field += '"';
                i++;
            } else {
                quoted = !quoted;
            }
        } else if (char === "," && !quoted) {
            row.push(field);
            field = "";
        } else if ((char === "\n" || char === "\r") && !quoted) {
            if (char === "\r" && input[i + 1] === "\n") i++;
            rows.push([...row, field]);
            row = [];
            field = "";
        } else {
            field += char;
        }
    }
    if (field || row.length) rows.push([...row, field]);
    return rows;
}
