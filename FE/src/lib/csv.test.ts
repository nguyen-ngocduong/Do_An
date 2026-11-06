import { expect, it } from "vitest";
import { parseCsv } from "./csv";

it("đọc CSV có BOM, dấu phẩy, dấu nháy và xuống dòng trong chuỗi", () => {
    expect(
        parseCsv(
            '\uFEFFfeature,value\r\n"A,B","say ""yes"""\r\n"two\nlines",0\r\n',
        ),
    ).toEqual([
        ["feature", "value"],
        ["A,B", 'say "yes"'],
        ["two\nlines", "0"],
    ]);
});
