import { useState } from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { Tabs } from "./controls";
function Example() {
    const [tab, setTab] = useState("predict");
    return (
        <Tabs
            items={[
                ["predict", "Dự đoán"],
                ["shap", "SHAP"],
                ["gemini", "Gemini"],
            ]}
            value={tab}
            onChange={setTab}
            name="Bằng chứng"
        />
    );
}
it("tab bàn phím chuyển lựa chọn và focus bằng mũi tên, Home, End", () => {
    render(<Example />);
    const predict = screen.getByRole("tab", { name: "Dự đoán" });
    predict.focus();
    fireEvent.keyDown(predict, { key: "ArrowRight" });
    expect(screen.getByRole("tab", { name: "SHAP" })).toHaveFocus();
    expect(screen.getByRole("tab", { name: "SHAP" })).toHaveAttribute(
        "aria-selected",
        "true",
    );
    fireEvent.keyDown(document.activeElement!, { key: "End" });
    expect(screen.getByRole("tab", { name: "Gemini" })).toHaveFocus();
    fireEvent.keyDown(document.activeElement!, { key: "Home" });
    expect(predict).toHaveFocus();
});
