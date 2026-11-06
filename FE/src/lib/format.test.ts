import { expect, it } from "vitest";
import { csvDisplayValue, seconds } from "./format";

it("hiển thị thời lượng từ giây, đổi đơn vị có tính toán và giữ giá trị thiếu", () => {
    expect(seconds(null)).toBe("—");
    expect(seconds(NaN)).toBe("—");
    expect(seconds(-1)).toBe("—");
    expect(seconds(0)).toBe("0 giây");
    expect(seconds(0.00005)).toBe("50 µs");
    expect(seconds(0.005)).toBe("5 ms");
    expect(seconds(0.5)).toBe("500 ms");
    expect(seconds(3.829)).toBe("3,83 giây");
    expect(seconds(7.624732632)).toBe("7,62 giây");
    expect(seconds(3829)).toBe("1 giờ 3 phút 49 giây");
    expect(seconds(119.999)).toBe("2 phút 0 giây");
    expect(seconds(3599.999)).toBe("1 giờ 0 phút 0 giây");
});

it("CSV chỉ rút gọn cột số, không biến giá trị rất nhỏ thành 0", () => {
    expect(csvDisplayValue("0.279578298330307", "shap_value")).toBe("0,279578");
    expect(
        csvDisplayValue("27.9578298330307", "impact_percentage_points"),
    ).toBe("27,9578");
    expect(csvDisplayValue("-0.00000000321", "shap_value")).toBe("-3.210e-9");
    expect(csvDisplayValue("0", "value")).toBe("0");
    expect(csvDisplayValue("", "shap_value")).toBe("");
    expect(csvDisplayValue("NaN", "value")).toBe("NaN");
    expect(csvDisplayValue("IAT", "feature")).toBe("IAT");
    expect(csvDisplayValue("000014", "row_index")).toBe("000014");
});
