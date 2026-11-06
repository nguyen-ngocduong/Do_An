import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { ActivityChart, ClassDistribution, dayLabel } from "./charts";
import { CLASS_NAMES, type ClassName } from "@/types/model";

it("ngày được giữ nguyên nhãn lịch, dữ liệu 0 không tạo NaN và cột có thể đọc bằng bàn phím", () => {
    const { container } = render(
        <ActivityChart
            days={[
                {
                    date: "2026-11-02",
                    normal_rows: 0,
                    suspected_rows: 0,
                    total_rows: 0,
                },
                {
                    date: "2026-11-03",
                    normal_rows: 0,
                    suspected_rows: 0,
                    total_rows: 0,
                },
            ]}
        />,
    );
    expect(dayLabel("2026-11-02")).toBe("02/11");
    expect(container.querySelector("svg")?.outerHTML).not.toMatch(
        /NaN|Infinity/,
    );
    expect(container.querySelector(".chart-kde-path")).not.toBeInTheDocument();
    expect(
        screen.getByText(/Chưa đủ ngày có dữ liệu để ước lượng KDE/),
    ).toBeInTheDocument();
    fireEvent.focus(
        screen.getByRole("img", { name: "02/11: 0 Normal, 0 khác Normal" }),
    );
    expect(container.querySelector(".activity-detail")?.textContent).toContain(
        "02/11",
    );
    expect(screen.getByText("Xem bảng số liệu theo ngày")).toBeInTheDocument();
});

it("vẽ đường KDE khi có đa-ngày dữ liệu và không vẽ khi ngày đơn", () => {
    // Đa ngày với dữ liệu
    const multiDays = [
        {
            date: "2026-11-01",
            normal_rows: 10,
            suspected_rows: 5,
            total_rows: 15,
        },
        {
            date: "2026-11-02",
            normal_rows: 20,
            suspected_rows: 10,
            total_rows: 30,
        },
    ];
    const { container, rerender } = render(<ActivityChart days={multiDays} />);
    const kdePath = container.querySelector(".chart-kde-path");
    expect(kdePath).toBeInTheDocument();
    expect(kdePath?.getAttribute("d")).toMatch(/^M\s/);
    expect(container.querySelector("svg")?.outerHTML).not.toMatch(
        /NaN|Infinity/,
    );
    expect(
        screen.getByText(
            /KDE · Ước lượng từ số lượt theo ngày/,
        ),
    ).toBeInTheDocument();

    // Ngày đơn burst -> không vẽ KDE
    const singleDay = [
        {
            date: "2026-11-01",
            normal_rows: 50,
            suspected_rows: 0,
            total_rows: 50,
        },
        {
            date: "2026-11-02",
            normal_rows: 0,
            suspected_rows: 0,
            total_rows: 0,
        },
    ];
    rerender(<ActivityChart days={singleDay} />);
    expect(container.querySelector(".chart-kde-path")).not.toBeInTheDocument();
    expect(
        screen.getByText(/Chưa đủ ngày có dữ liệu để ước lượng KDE/),
    ).toBeInTheDocument();
});

it("phân bố tròn giữ đủ tám lớp, tính phần trên tổng và không tạo tỷ lệ giả khi trống", () => {
    const counts = Object.fromEntries(
        CLASS_NAMES.map((name) => [name, 0]),
    ) as Record<ClassName, number>;
    const view = render(<ClassDistribution counts={counts} />);
    expect(
        view.container.querySelectorAll(".class-pie-legend li"),
    ).toHaveLength(8);
    expect(view.container.querySelectorAll(".class-pie path")).toHaveLength(0);
    expect(view.container.querySelector(".class-pie")?.outerHTML).not.toMatch(
        /NaN|Infinity/,
    );
    expect(
        view.container.querySelector(".class-pie-percentage"),
    ).toHaveTextContent("—");

    view.rerender(
        <ClassDistribution counts={{ ...counts, Normal: 1, DDoS: 49 }} />,
    );
    expect(
        screen.getByRole("img", { name: /Phân bố nhãn của 50 mẫu/ }),
    ).toBeInTheDocument();
    const rows = Array.from(
        view.container.querySelectorAll(".class-pie-legend li"),
    );
    expect(rows.map((row) => row.children[1].textContent)).toEqual(CLASS_NAMES);
    expect(rows[0].querySelector(".class-pie-percentage")).toHaveTextContent(
        "2%",
    );
    expect(rows[2].querySelector(".class-pie-percentage")).toHaveTextContent(
        "98%",
    );
    expect(view.container.querySelectorAll(".class-pie path")).toHaveLength(2);
});

it("toàn bộ mẫu thuộc một lớp vẫn vẽ đủ hình tròn và hiển thị 100%", () => {
    const counts = Object.fromEntries(
        CLASS_NAMES.map((name) => [name, 0]),
    ) as Record<ClassName, number>;
    const { container } = render(
        <ClassDistribution counts={{ ...counts, DoS: 50 }} />,
    );
    expect(
        container.querySelector(".class-pie circle:not(.class-pie-empty)"),
    ).toBeInTheDocument();
    expect(container.querySelector(".class-pie path")).not.toBeInTheDocument();
    expect(
        container.querySelector(".class-pie-legend li:nth-child(4)"),
    ).toHaveTextContent("100%");
});

it("phân bố 70%/20% không label chen bên trong hình quạt, hiển thị đúng legend và shapes", () => {
    const counts = Object.fromEntries(
        CLASS_NAMES.map((name) => [name, 0]),
    ) as Record<ClassName, number>;
    const view = render(
        <ClassDistribution
            counts={{ ...counts, DDoS: 35, DoS: 10, Mirai: 5 }}
        />,
    );
    // Không còn nhãn text/tspan chen trong hình quạt
    expect(view.container.querySelectorAll(".class-pie-label")).toHaveLength(0);
    expect(view.container.querySelectorAll(".class-pie text")).toHaveLength(0);

    // 3 hình quạt
    expect(view.container.querySelectorAll(".class-pie path")).toHaveLength(3);

    // Legend hiển thị đúng số liệu
    const rows = Array.from(
        view.container.querySelectorAll(".class-pie-legend li"),
    );
    expect(rows).toHaveLength(8);

    // DDoS (index 2 trong CLASS_NAMES)
    const ddosRow = rows[CLASS_NAMES.indexOf("DDoS")];
    expect(ddosRow.children[1]).toHaveTextContent("DDoS");
    expect(ddosRow).toHaveTextContent("35");
    expect(ddosRow.querySelector(".class-pie-percentage")).toHaveTextContent(
        "70%",
    );
    expect(ddosRow.getAttribute("data-dominant")).toBe("true");

    const dosRow = rows[CLASS_NAMES.indexOf("DoS")];
    expect(dosRow.children[1]).toHaveTextContent("DoS");
    expect(dosRow).toHaveTextContent("10");
    expect(dosRow.querySelector(".class-pie-percentage")).toHaveTextContent(
        "20%",
    );

    const miraiRow = rows[CLASS_NAMES.indexOf("Mirai")];
    expect(miraiRow.children[1]).toHaveTextContent("Mirai");
    expect(miraiRow).toHaveTextContent("5");
    expect(miraiRow.querySelector(".class-pie-percentage")).toHaveTextContent(
        "10%",
    );

    // Trường hợp 100% DoS
    view.rerender(<ClassDistribution counts={{ ...counts, DoS: 50 }} />);
    expect(
        view.container.querySelector(".class-pie circle:not(.class-pie-empty)"),
    ).toBeInTheDocument();
    expect(view.container.querySelectorAll(".class-pie-label")).toHaveLength(0);
});

it("khi không có classCounts thì không tự bịa số liệu tấn công bằng 0, ẩn bộ chọn tab và mặc định xem theo ngày", () => {
    const days = [
        {
            date: "2026-11-01",
            normal_rows: 10,
            suspected_rows: 5,
            total_rows: 15,
        },
        {
            date: "2026-11-02",
            normal_rows: 20,
            suspected_rows: 10,
            total_rows: 30,
        },
    ];
    const { container } = render(<ActivityChart days={days} />);
    // Không hiển thị bộ chọn tab khi không có classCounts
    expect(screen.queryByRole("tablist")).not.toBeInTheDocument();
    expect(
        screen.queryByRole("tab", { name: "Theo lớp" }),
    ).not.toBeInTheDocument();
    // Không vẽ biểu đồ thanh ngang theo lớp
    expect(
        container.querySelector(".chart-class-columns"),
    ).not.toBeInTheDocument();
    // Mặc định hiển thị biểu đồ ngày
    expect(container.querySelector(".chart-kde-path")).toBeInTheDocument();
    expect(screen.getByText("Xem bảng số liệu theo ngày")).toBeInTheDocument();
});

it("'Theo lớp' hiển thị tám cột đứng, trục label/count, KDE minh họa, tóm tắt và bảng số liệu", () => {
    const counts: Record<ClassName, number> = {
        Normal: 81,
        BruteForce: 2,
        DDoS: 1259,
        DoS: 454,
        Mirai: 150,
        Recon: 26,
        Spoofing: 27,
        "Web-Based": 1,
    };
    const days = [
        {
            date: "2026-11-01",
            normal_rows: 40,
            suspected_rows: 900,
            total_rows: 940,
        },
        {
            date: "2026-11-02",
            normal_rows: 41,
            suspected_rows: 1019,
            total_rows: 1060,
        },
    ];
    const { container } = render(
        <ActivityChart days={days} classCounts={counts} />,
    );

    // Mặc định chọn tab "Theo lớp"
    const classTab = screen.getByRole("tab", { name: "Theo lớp" });
    expect(classTab).toHaveAttribute("aria-selected", "true");
    expect(classTab).toHaveAttribute("tabindex", "0");
    const dailyTab = screen.getByRole("tab", { name: "Theo ngày · KDE" });
    expect(dailyTab).toHaveAttribute("tabindex", "-1");

    // Tám nhãn trên trục X, giữ thứ tự cố định.
    const classNames = Array.from(
        container.querySelectorAll(".chart-class-name"),
    ).map((el) => el.textContent);
    expect(classNames).toEqual(CLASS_NAMES);

    // Số đếm nguyên thật hiển thị trên từng cột mà không cần hover.
    const countTexts = Array.from(
        container.querySelectorAll(".chart-bar-count"),
    ).map((el) => el.textContent);
    expect(countTexts).toContain("81");
    expect(countTexts).toContain("2");
    expect(countTexts).toContain("1.259");
    expect(countTexts).toContain("1");

    // Thanh dương nhỏ ("Web-Based": 1) vẫn có thanh trực quan thật mà không bị thổi phồng
    const webBasedGroup = screen.getByRole("img", {
        name: /Web-Based: 1 mẫu/,
    });
    expect(
        webBasedGroup.querySelector(".chart-class-bar"),
    ).toBeInTheDocument();
    const rareHeight = Number(webBasedGroup.querySelector(".chart-class-bar")?.getAttribute("height"));
    const dominantHeight = Number(container.querySelector('[data-class="DDoS"] .chart-class-bar')?.getAttribute("height"));
    expect(rareHeight / dominantHeight).toBeCloseTo(1 / 1259, 10);
    expect(container.querySelector(".class-kde-path")).toBeInTheDocument();
    expect(container.querySelector("svg")?.outerHTML).not.toMatch(/NaN|Infinity/);
    expect(screen.getByText("Lớp dự đoán", { selector: "svg text" })).toBeInTheDocument();
    expect(screen.getByText("Số mẫu", { selector: "svg text" })).toBeInTheDocument();

    // Lớp có count = 0 thì không vẽ thanh ngang (barWidth = 0)
    const countsWithZero: Record<ClassName, number> = {
        ...counts,
        "Web-Based": 0,
    };
    const viewWithZero = render(
        <ActivityChart days={days} classCounts={countsWithZero} />,
    );
    const zeroGroup = viewWithZero.container.querySelector(
        '[data-class="Web-Based"]',
    );
    expect(
        zeroGroup?.querySelector(".chart-class-bar"),
    ).not.toBeInTheDocument();
    viewWithZero.unmount();

    // Tóm tắt Normal và Khác Normal từ số đếm thật
    expect(
        container.querySelector(".activity-detail")?.textContent,
    ).toContain("Normal: 81");
    expect(
        container.querySelector(".activity-detail")?.textContent,
    ).toContain("Khác Normal: 1.919");
    expect(
        container.querySelector(".activity-detail")?.textContent,
    ).toContain("Tổng: 2.000");

    // Ghi chú giải thích KDE có sẵn ở chế độ theo ngày
    expect(
        screen.getByText(
            /KDE được làm mượt theo thứ tự nhãn cố định/,
        ),
    ).toBeInTheDocument();

    // Bảng số liệu theo lớp
    expect(screen.getByText("Xem bảng số liệu theo lớp")).toBeInTheDocument();

    // Tương tác focus vào 1 hàng cập nhật thông tin chi tiết với nhãn "Khác Normal" (không dùng "Tấn công")
    const ddosBarGroup = screen.getByRole("img", {
        name: /DDoS: 1\.259 mẫu/,
    });
    fireEvent.focus(ddosBarGroup);
    expect(container.querySelector(".activity-detail")?.textContent).toContain(
        "DDoS",
    );
    expect(container.querySelector(".activity-detail")?.textContent).toContain(
        "1.259",
    );
    expect(container.querySelector(".activity-detail")?.textContent).toContain(
        "Khác Normal",
    );
    expect(
        container.querySelector(".activity-detail")?.textContent,
    ).not.toContain("Tấn công");

    // Blur khôi phục tóm tắt tổng quan
    fireEvent.blur(ddosBarGroup);
    expect(container.querySelector(".activity-detail")?.textContent).toContain(
        "Normal: 81",
    );
});

it("chuyển đổi tab bằng phím mũi tên và Home/End theo chuẩn roving tabIndex", () => {
    const counts: Record<ClassName, number> = {
        Normal: 81,
        BruteForce: 2,
        DDoS: 1259,
        DoS: 454,
        Mirai: 150,
        Recon: 26,
        Spoofing: 27,
        "Web-Based": 1,
    };
    const days = [
        {
            date: "2026-11-01",
            normal_rows: 40,
            suspected_rows: 900,
            total_rows: 940,
        },
        {
            date: "2026-11-02",
            normal_rows: 41,
            suspected_rows: 1019,
            total_rows: 1060,
        },
    ];
    const { container } = render(
        <ActivityChart days={days} classCounts={counts} />,
    );

    const classTab = screen.getByRole("tab", { name: "Theo lớp" });
    const dailyTab = screen.getByRole("tab", { name: "Theo ngày · KDE" });

    // Roving tabIndex ban đầu: Theo lớp là 0, Theo ngày là -1
    expect(classTab).toHaveAttribute("tabindex", "0");
    expect(dailyTab).toHaveAttribute("tabindex", "-1");

    // Phím ArrowRight chuyển sang Theo ngày · KDE
    fireEvent.keyDown(classTab, { key: "ArrowRight" });
    expect(dailyTab).toHaveAttribute("aria-selected", "true");
    expect(dailyTab).toHaveAttribute("tabindex", "0");
    expect(classTab).toHaveAttribute("tabindex", "-1");
    expect(container.querySelector(".chart-kde-path")).toBeInTheDocument();

    // Phím ArrowLeft quay lại Theo lớp
    fireEvent.keyDown(dailyTab, { key: "ArrowLeft" });
    expect(classTab).toHaveAttribute("aria-selected", "true");
    expect(classTab).toHaveAttribute("tabindex", "0");
    expect(dailyTab).toHaveAttribute("tabindex", "-1");

    // Phím End nhảy tới tab cuối (Theo ngày)
    fireEvent.keyDown(classTab, { key: "End" });
    expect(dailyTab).toHaveAttribute("aria-selected", "true");
    expect(dailyTab).toHaveAttribute("tabindex", "0");

    // Phím Home nhảy về tab đầu (Theo lớp)
    fireEvent.keyDown(dailyTab, { key: "Home" });
    expect(classTab).toHaveAttribute("aria-selected", "true");
    expect(classTab).toHaveAttribute("tabindex", "0");
});

it("ClassDistribution có caption chi tiết khi hover/focus và khôi phục lớp nhiều nhất khi blur", () => {
    const counts = Object.fromEntries(
        CLASS_NAMES.map((name) => [name, 0]),
    ) as Record<ClassName, number>;
    counts.Normal = 20;
    counts.DDoS = 80;

    const view = render(<ClassDistribution counts={counts} />);
    const caption = view.container.querySelector(".class-pie-detail");
    expect(caption).toBeInTheDocument();

    // Khi chưa hover: hiển thị lớp nhiều nhất (DDoS 80 mẫu, 80%)
    expect(caption?.textContent).toContain("Lớp nhiều nhất: DDoS");
    expect(caption?.textContent).toContain("80 mẫu");
    expect(caption?.textContent).toContain("80%");

    // Hover vào phần Normal trên legend
    const legendItems = view.container.querySelectorAll(
        ".class-pie-legend li",
    );
    fireEvent.mouseEnter(legendItems[0]);
    expect(caption?.textContent).toContain("Đang xem: Normal");
    expect(caption?.textContent).toContain("20 mẫu");
    expect(caption?.textContent).toContain("20%");
    expect(legendItems[0]).toHaveAttribute("data-active", "true");

    // Rời chuột (mouseLeave) khôi phục lớp nhiều nhất
    fireEvent.mouseLeave(legendItems[0]);
    expect(caption?.textContent).toContain("Lớp nhiều nhất: DDoS");
    expect(legendItems[0]).not.toHaveAttribute("data-active");

    // Trường hợp 0 mẫu: hiển thị thông báo trống phù hợp
    const zeroCounts = Object.fromEntries(
        CLASS_NAMES.map((name) => [name, 0]),
    ) as Record<ClassName, number>;
    view.rerender(<ClassDistribution counts={zeroCounts} />);
    expect(
        view.container.querySelector(".class-pie-detail")?.textContent,
    ).toContain("Chưa có mẫu dự đoán");
});

it("cột lớp giữ số 0 và không tạo KDE khi chỉ có một lớp; cập nhật được khi dữ liệu thay đổi", () => {
    const empty = Object.fromEntries(CLASS_NAMES.map((name) => [name, 0])) as Record<ClassName, number>;
    const view = render(<ActivityChart days={[]} classCounts={empty} />);
    expect(view.container.querySelectorAll(".chart-bar-count")).toHaveLength(8);
    expect(view.container.querySelectorAll(".chart-class-bar")).toHaveLength(0);
    expect(view.container.querySelector(".class-kde-path")).not.toBeInTheDocument();
    expect(view.container.querySelector("svg")?.outerHTML).not.toMatch(/NaN|Infinity/);

    view.rerender(<ActivityChart days={[]} classCounts={{ ...empty, Normal: 1 }} />);
    const normalLabel = view.container.querySelector('[data-class="Normal"] .chart-bar-count');
    expect(Number(normalLabel?.getAttribute("y"))).toBeGreaterThan(35);

    view.rerender(<ActivityChart days={[]} classCounts={{ ...empty, Normal: 50 }} />);
    expect(view.container.querySelectorAll(".chart-class-bar")).toHaveLength(1);
    expect(view.container.querySelector(".class-kde-path")).not.toBeInTheDocument();
    expect(screen.getByText(/Chưa đủ lớp có mẫu để vẽ KDE/)).toBeInTheDocument();

    view.rerender(<ActivityChart days={[]} classCounts={{ ...empty, Normal: 10, DDoS: 40 }} />);
    expect(view.container.querySelectorAll(".chart-class-bar")).toHaveLength(2);
    expect(view.container.querySelector(".class-kde-path")).toBeInTheDocument();
});
