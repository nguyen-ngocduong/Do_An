"use client";
import { useEffect, useRef, useState } from "react";
import { CLASS_NAMES } from "@/types/model";
import type { DashboardDay } from "@/types/dashboard";
import type { ClassName } from "@/types/model";
import { number, percent } from "@/lib/format";
import { activityKde } from "@/lib/activity-kde";
import { classKde } from "@/lib/class-kde";

export function dayLabel(date: string) {
    return `${date.slice(8, 10)}/${date.slice(5, 7)}`;
}

/**
 * Tính toán miền giá trị Y và các mốc đánh dấu (ticks) hợp lý.
 * Bắt đầu từ 0, bao phủ max(counts, curve values) và có khoảng trống trên đỉnh cho nhãn số đếm.
 */
function computeClassYDomain(maxValue: number): {
    yMax: number;
    ticks: number[];
} {
    if (maxValue <= 0) {
        return { yMax: 1, ticks: [0, 1] };
    }
    if (maxValue <= 4) {
        const yMax = Math.ceil(maxValue) + 1;
        return {
            yMax,
            ticks: Array.from({ length: yMax + 1 }, (_, i) => i),
        };
    }

    const targetSteps = 3;
    const rawStep = maxValue / targetSteps;
    const power = Math.pow(10, Math.floor(Math.log10(rawStep)));
    const fraction = rawStep / power;

    let step: number;
    if (fraction <= 1.2) step = 1 * power;
    else if (fraction <= 2.2) step = 2 * power;
    else if (fraction <= 3) step = 2.5 * power;
    else if (fraction <= 6) step = 5 * power;
    else step = 10 * power;

    step = Math.max(1, Math.ceil(step));
    let yMax = Math.ceil(maxValue / step) * step;
    if (maxValue / yMax > 0.92) {
        yMax += step;
    }

    const ticks: number[] = [];
    for (let t = 0; t <= yMax; t += step) {
        ticks.push(t);
    }

    return { yMax, ticks };
}

export interface ActivityChartProps {
    days: DashboardDay[];
    classCounts?: Record<ClassName, number>;
    dateRange?: string;
    defaultView?: "classes" | "daily";
}

export function ActivityChart({
    days,
    classCounts,
    dateRange,
    defaultView,
}: ActivityChartProps) {
    const container = useRef<HTMLDivElement>(null);
    const tabClassesRef = useRef<HTMLButtonElement>(null);
    const tabDailyRef = useRef<HTMLButtonElement>(null);

    const [chartWidth, setChartWidth] = useState(640);
    const hasClassData = Boolean(classCounts);
    const [view, setView] = useState<"classes" | "daily">(
        defaultView ?? (hasClassData ? "classes" : "daily"),
    );
    const [activeDate, setActiveDate] = useState<string | null>(null);
    const [activeClass, setActiveClass] = useState<ClassName | null>(null);

    useEffect(() => {
        if (!container.current || typeof ResizeObserver === "undefined") return;
        const observer = new ResizeObserver((entries) => {
            setChartWidth(Math.max(160, entries[0].contentRect.width));
        });
        observer.observe(container.current);
        return () => observer.disconnect();
    }, []);

    // Số liệu hoạt động theo ngày
    const activeDay = days.find((day) => day.date === activeDate) ?? days.at(-1);
    const kde = activityKde(days);
    const maxBar = Math.max(0, ...days.map((day) => day.total_rows));
    const maxKde =
        kde.points.length > 0 ? Math.max(...kde.points.map((p) => p.y)) : 0;
    const dailyMaximum = Math.max(1, Math.ceil(Math.max(maxBar, maxKde)));
    const dailyTicks = [
        ...new Set([0, Math.ceil(dailyMaximum / 2), dailyMaximum]),
    ];
    const plotWidth = chartWidth - 56;
    const plotHeight = 132;
    const daySlot = plotWidth / Math.max(1, days.length);
    const dayBarWidth = Math.min(28, daySlot * 0.6);
    const tickStep = Math.ceil(
        days.length / (chartWidth < 340 ? 3 : chartWidth < 420 ? 4 : 6),
    );

    const kdePath =
        kde.points.length > 0
            ? kde.points
                  .map((p, idx) => {
                      const x = 44 + daySlot * (p.x + 0.5);
                      const y =
                          14 + plotHeight - (p.y / dailyMaximum) * plotHeight;
                      return `${idx === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
                  })
                  .join(" ")
            : "";

    // Số liệu theo tám lớp mô hình (chỉ tính toán khi có dữ liệu thật từ BE)
    const counts = classCounts ?? null;
    const classTotal = counts
        ? CLASS_NAMES.reduce((sum, name) => sum + (counts[name] ?? 0), 0)
        : 0;
    const normalCount = counts?.Normal ?? 0;
    const attackCount = classTotal - normalCount;
    const maxClassCount = counts
        ? Math.max(0, ...CLASS_NAMES.map((name) => counts[name] ?? 0))
        : 0;

    // Tính toán đường KDE minh họa từ số đếm 8 lớp
    const classKdeResult = counts
        ? classKde(counts)
        : { points: [], bandwidth: null };
    const maxClassKdeY =
        classKdeResult.points.length > 0
            ? Math.max(...classKdeResult.points.map((p) => p.y))
            : 0;
    const rawClassMax = Math.max(maxClassCount, maxClassKdeY);

    // Trục Y dùng chung cho cả cột đứng và đường KDE
    const { yMax: classMaximum, ticks: classTicks } =
        computeClassYDomain(rawClassMax);

    // Cấu hình tọa độ và kích thước cho 8 cột đứng (~270px)
    const classSvgHeight = 270;
    const classPlotTop = 28;
    const classPlotBottom = 196;
    const classPlotHeight = classPlotBottom - classPlotTop; // 168px
    const classPlotLeft = 44;
    const classPlotRight = chartWidth - 16;
    const classPlotWidth = Math.max(1, classPlotRight - classPlotLeft);
    const classSlotWidth = classPlotWidth / CLASS_NAMES.length;
    const classBarWidth = Math.min(32, Math.max(10, classSlotWidth * 0.55));

    const classKdePath =
        classKdeResult.points.length > 0
            ? classKdeResult.points
                  .map((p, idx) => {
                      const x = classPlotLeft + (p.x + 0.5) * classSlotWidth;
                      const y =
                          classPlotBottom -
                          (p.y / classMaximum) * classPlotHeight;
                      return `${idx === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
                  })
                  .join(" ")
            : "";

    const dateRangeLabel =
        dateRange ||
        (days.length > 0
            ? `${dayLabel(days[0].date)} – ${dayLabel(days.at(-1)!.date)}`
            : "");

    const handleTabKeyDown = (event: React.KeyboardEvent) => {
        if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
            event.preventDefault();
            if (view === "classes") {
                setView("daily");
                tabDailyRef.current?.focus();
            } else {
                setView("classes");
                tabClassesRef.current?.focus();
            }
        } else if (event.key === "Home") {
            event.preventDefault();
            setView("classes");
            tabClassesRef.current?.focus();
        } else if (event.key === "End") {
            event.preventDefault();
            setView("daily");
            tabDailyRef.current?.focus();
        }
    };

    return (
        <>
            <div className="activity-chart-toolbar">
                {hasClassData && (
                    <div
                        className="chart-view-selector"
                        role="tablist"
                        aria-label="Chế độ biểu đồ hoạt động"
                        onKeyDown={handleTabKeyDown}
                    >
                        <button
                            ref={tabClassesRef}
                            type="button"
                            role="tab"
                            id="tab-view-classes"
                            aria-selected={view === "classes"}
                            aria-controls="panel-view-classes"
                            tabIndex={view === "classes" ? 0 : -1}
                            className={`chart-view-btn ${view === "classes" ? "active" : ""}`}
                            onClick={() => setView("classes")}
                        >
                            Theo lớp
                        </button>
                        <button
                            ref={tabDailyRef}
                            type="button"
                            role="tab"
                            id="tab-view-daily"
                            aria-selected={view === "daily"}
                            aria-controls="panel-view-daily"
                            tabIndex={view === "daily" ? 0 : -1}
                            className={`chart-view-btn ${view === "daily" ? "active" : ""}`}
                            onClick={() => setView("daily")}
                        >
                            Theo ngày · KDE
                        </button>
                    </div>
                )}
                {view === "daily" || !hasClassData ? (
                    <div className="dashboard-chart-legend">
                        <span>
                            <i className="series-kde" />
                            KDE · Ước lượng
                        </span>
                        <span>
                            <i className="series-normal" />
                            Normal
                        </span>
                        <span>
                            <i className="series-suspected" />
                            Khác Normal
                        </span>
                    </div>
                ) : (
                    <div className="dashboard-chart-legend">
                        <span>
                            <i className="series-kde class-kde-swatch" />
                            KDE minh họa
                        </span>
                        <span>
                            <i
                                className="series-normal"
                                style={{ background: "var(--pie-class-0)" }}
                            />
                            Normal
                        </span>
                        <span>
                            <i
                                className="series-attack"
                                style={{ background: "var(--pie-class-2)" }}
                            />
                            Khác Normal
                        </span>
                    </div>
                )}
            </div>

            <div
                ref={container}
                className="dashboard-activity-plot"
                role={hasClassData ? "tabpanel" : undefined}
                id={
                    hasClassData
                        ? view === "classes"
                            ? "panel-view-classes"
                            : "panel-view-daily"
                        : undefined
                }
                aria-labelledby={
                    hasClassData
                        ? view === "classes"
                            ? "tab-view-classes"
                            : "tab-view-daily"
                        : undefined
                }
                aria-label={!hasClassData ? "Biểu đồ hoạt động theo ngày" : undefined}
            >
                {view === "daily" || !hasClassData || !counts ? (
                    <svg
                        className="activity-chart"
                        viewBox={`0 0 ${chartWidth} 176`}
                        role="group"
                        aria-label="Số mẫu server xử lý theo ngày"
                    >
                        {dailyTicks.map((tick) => {
                            const y =
                                14 +
                                plotHeight -
                                (tick / dailyMaximum) * plotHeight;
                            return (
                                <g key={tick} aria-hidden="true">
                                    <line
                                        x1="44"
                                        x2={chartWidth - 12}
                                        y1={y}
                                        y2={y}
                                        className="chart-gridline"
                                    />
                                    <text x="36" y={y + 4} textAnchor="end">
                                        {number(tick)}
                                    </text>
                                </g>
                            );
                        })}
                        {days.map((day, index) => {
                            const x =
                                44 +
                                daySlot * index +
                                (daySlot - dayBarWidth) / 2;
                            const normalHeight =
                                (day.normal_rows / dailyMaximum) * plotHeight;
                            const suspectedHeight =
                                (day.suspected_rows / dailyMaximum) *
                                plotHeight;
                            const description = `${dayLabel(day.date)}: ${number(day.normal_rows)} Normal, ${number(day.suspected_rows)} khác Normal`;
                            return (
                                <g
                                    key={day.date}
                                    tabIndex={0}
                                    role="img"
                                    aria-label={description}
                                    onFocus={() => setActiveDate(day.date)}
                                    onMouseEnter={() => setActiveDate(day.date)}
                                >
                                    <title>{description}</title>
                                    <rect
                                        className="chart-hitbox"
                                        x={44 + daySlot * index}
                                        y="10"
                                        width={daySlot}
                                        height="138"
                                        rx="3"
                                    />
                                    <rect
                                        className="series-normal"
                                        x={x}
                                        y={14 + plotHeight - normalHeight}
                                        width={dayBarWidth}
                                        height={normalHeight}
                                        rx="2"
                                    />
                                    <rect
                                        className="series-suspected"
                                        x={x}
                                        y={
                                            14 +
                                            plotHeight -
                                            normalHeight -
                                            suspectedHeight
                                        }
                                        width={dayBarWidth}
                                        height={suspectedHeight}
                                        rx="2"
                                    />
                                    {(index % tickStep === 0 ||
                                        index === days.length - 1) && (
                                        <text
                                            x={x + dayBarWidth / 2}
                                            y="168"
                                            textAnchor="middle"
                                        >
                                            {dayLabel(day.date)}
                                        </text>
                                    )}
                                </g>
                            );
                        })}
                        {kdePath && (
                            <path
                                d={kdePath}
                                className="chart-kde-path"
                                aria-hidden="true"
                            />
                        )}
                    </svg>
                ) : (
                    <svg
                        className="activity-chart chart-class-columns"
                        viewBox={`0 0 ${chartWidth} ${classSvgHeight}`}
                        role="group"
                        aria-label="Số lượng mẫu theo tám lớp mô hình"
                    >
                        <text x={classPlotLeft} y="13" className="chart-axis-name">Số mẫu</text>
                        {classTicks.map((tick) => {
                            const y = classPlotBottom - (tick / classMaximum) * classPlotHeight;
                            return (
                                <g key={tick} aria-hidden="true">
                                    <line x1={classPlotLeft} x2={classPlotRight} y1={y} y2={y} className="chart-gridline" />
                                    <text x={classPlotLeft - 8} y={y + 4} textAnchor="end">{number(tick)}</text>
                                </g>
                            );
                        })}
                        {CLASS_NAMES.map((name, index) => {
                            const count = counts[name] ?? 0;
                            const share = classTotal ? count / classTotal : 0;
                            const center = classPlotLeft + (index + 0.5) * classSlotWidth;
                            const height = (count / classMaximum) * classPlotHeight;
                            const y = classPlotBottom - height;
                            const description = `${name}: ${number(count)} mẫu (${classTotal ? percent(share, 1) : "0%"})`;
                            return (
                                <g
                                    key={name}
                                    tabIndex={0}
                                    role="img"
                                    aria-label={description}
                                    data-class={name}
                                    data-active={activeClass === name ? "true" : undefined}
                                    onFocus={() => setActiveClass(name)}
                                    onBlur={() => setActiveClass(null)}
                                    onMouseEnter={() => setActiveClass(name)}
                                    onMouseLeave={() => setActiveClass(null)}
                                >
                                    <title>{description}</title>
                                    <rect className="chart-hitbox" x={center - classSlotWidth / 2} y={classPlotTop - 4} width={classSlotWidth} height={classPlotHeight + 8} rx="3" />
                                    {height > 0 && (
                                        <rect className="chart-class-bar" data-class={name} x={center - classBarWidth / 2} y={y} width={classBarWidth} height={height} rx="2" fill={`var(--pie-class-${index})`} />
                                    )}
                                    <text x={center} y={Math.max(20, y - 6)} textAnchor="middle" className="chart-bar-count">{number(count)}</text>
                                    <text
                                        x={center}
                                        y={classPlotBottom + 16}
                                        textAnchor="end"
                                        transform={`rotate(-40 ${center} ${classPlotBottom + 16})`}
                                        className="chart-class-name"
                                    >
                                        {name}
                                    </text>
                                </g>
                            );
                        })}
                        {classKdePath && <path d={classKdePath} className="chart-kde-path class-kde-path" aria-hidden="true" />}
                        <text x={(classPlotLeft + classPlotRight) / 2} y={classSvgHeight - 6} textAnchor="middle" className="chart-axis-name">Lớp dự đoán</text>
                    </svg>
                )}
            </div>

            {view === "daily" || !hasClassData || !counts ? (
                <>
                    <p className="activity-detail" aria-live="polite">
                        {activeDay && (
                            <>
                                <strong>{dayLabel(activeDay.date)}</strong>
                                <span>
                                    Normal <b>{number(activeDay.normal_rows)}</b>
                                </span>
                                <span>
                                    Khác Normal <b>{number(activeDay.suspected_rows)}</b>
                                </span>
                            </>
                        )}
                    </p>
                    <p className="activity-kde-note">
                        {kde.points.length > 0
                            ? `KDE · Ước lượng từ số lượt theo ngày (${dateRangeLabel || "phạm vi đã chọn"}), không phải dự báo tương lai.`
                            : `Chưa đủ ngày có dữ liệu để ước lượng KDE${dateRangeLabel ? ` (${dateRangeLabel})` : ""}.`}
                    </p>
                    <details className="dashboard-data-table">
                        <summary>Xem bảng số liệu theo ngày</summary>
                        <div className="table-wrap">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Ngày</th>
                                        <th>Normal</th>
                                        <th>Khác Normal</th>
                                        <th>Tổng mẫu</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {days.map((day) => (
                                        <tr key={day.date}>
                                            <td>{day.date}</td>
                                            <td>{number(day.normal_rows)}</td>
                                            <td>{number(day.suspected_rows)}</td>
                                            <td>{number(day.total_rows)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </details>
                </>
            ) : (
                <>
                    <p className="activity-detail" aria-live="polite">
                        {activeClass ? (
                            <>
                                <strong>{activeClass}</strong>
                                <span>
                                    Số mẫu: <b>{number(counts[activeClass] ?? 0)}</b>
                                </span>
                                <span>
                                    Tỷ lệ:{" "}
                                    <b>
                                        {classTotal
                                            ? percent(
                                                  (counts[activeClass] ?? 0) /
                                                      classTotal,
                                                  1,
                                              )
                                            : "—"}
                                    </b>
                                </span>
                                <span className="muted">
                                    (
                                    {activeClass === "Normal"
                                        ? "Normal"
                                        : "Khác Normal"}
                                    )
                                </span>
                            </>
                        ) : (
                            <>
                                <span>
                                    Normal: <b>{number(normalCount)}</b> (
                                    {classTotal
                                        ? percent(normalCount / classTotal, 1)
                                        : "—"}
                                    )
                                </span>
                                <span>
                                    Khác Normal: <b>{number(attackCount)}</b> (
                                    {classTotal
                                        ? percent(attackCount / classTotal, 1)
                                        : "—"}
                                    )
                                </span>
                                <span>
                                    Tổng: <b>{number(classTotal)}</b> mẫu
                                </span>
                            </>
                        )}
                    </p>
                    <p className="activity-kde-note">
                        {classKdeResult.points.length === 0 && "Chưa đủ lớp có mẫu để vẽ KDE. "}
                        KDE được làm mượt theo thứ tự nhãn cố định, chỉ để tham khảo;
                        số mẫu chính xác hiển thị trên cột.
                    </p>
                    <details className="dashboard-data-table">
                        <summary>Xem bảng số liệu theo lớp</summary>
                        <div className="table-wrap">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Lớp dự đoán</th>
                                        <th>Phân loại</th>
                                        <th>Số mẫu</th>
                                        <th>Tỷ lệ</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {CLASS_NAMES.map((name, idx) => {
                                        const count = counts[name] ?? 0;
                                        const share = classTotal
                                            ? count / classTotal
                                            : 0;
                                        return (
                                            <tr key={name}>
                                                <td>
                                                    <span
                                                        className="class-pie-dot"
                                                        style={{
                                                            display:
                                                                "inline-block",
                                                            marginRight: 6,
                                                            background: `var(--pie-class-${idx})`,
                                                        }}
                                                        aria-hidden="true"
                                                    />
                                                    {name}
                                                </td>
                                                <td>
                                                    {name === "Normal"
                                                        ? "Normal"
                                                        : "Khác Normal"}
                                                </td>
                                                <td>{number(count)}</td>
                                                <td>
                                                    {classTotal
                                                        ? percent(share, 1)
                                                        : "—"}
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </details>
                </>
            )}
        </>
    );
}

export function ClassDistribution({
    counts,
}: {
    counts: Record<ClassName, number>;
}) {
    const [activeName, setActiveName] = useState<ClassName | null>(null);
    const total = CLASS_NAMES.reduce((sum, name) => sum + counts[name], 0);
    const maxCount =
        total > 0 ? Math.max(...CLASS_NAMES.map((name) => counts[name])) : 0;

    const slices = CLASS_NAMES.map((name, index) => {
        const share = total ? counts[name] / total : 0;
        const previousCount = CLASS_NAMES.slice(0, index).reduce(
            (sum, previous) => sum + counts[previous],
            0,
        );
        const start =
            -Math.PI / 2 + (total ? (previousCount / total) * 2 * Math.PI : 0);
        const end = start + share * 2 * Math.PI;
        const x1 = 110 + 96 * Math.cos(start);
        const y1 = 110 + 96 * Math.sin(start);
        const x2 = 110 + 96 * Math.cos(end);
        const y2 = 110 + 96 * Math.sin(end);
        return {
            name,
            count: counts[name],
            share,
            color: `var(--pie-class-${index})`,
            path: `M 110 110 L ${x1.toFixed(2)} ${y1.toFixed(2)} A 96 96 0 ${share > 0.5 ? 1 : 0} 1 ${x2.toFixed(2)} ${y2.toFixed(2)} Z`,
            isDominant: total > 0 && counts[name] === maxCount && maxCount > 0,
        };
    });

    const dominantSlice = slices.find((s) => s.isDominant) ?? slices[0];
    const activeSlice = slices.find((s) => s.name === activeName);

    return (
        <div
            className="dashboard-distribution"
            aria-label="Phân bố tám lớp dự đoán"
        >
            <svg
                className="class-pie"
                viewBox="0 0 220 220"
                role="img"
                aria-label={`Phân bố nhãn của ${number(total)} mẫu; số liệu chi tiết ở chú giải bên cạnh`}
            >
                {!total && (
                    <>
                        <circle
                            cx="110"
                            cy="110"
                            r="88"
                            className="class-pie-empty"
                        />
                        <text
                            x="110"
                            y="116"
                            textAnchor="middle"
                            className="class-pie-zero"
                        >
                            0 mẫu
                        </text>
                    </>
                )}
                {slices
                    .filter((slice) => slice.count > 0)
                    .map((slice) => {
                        const isActive = activeName === slice.name;
                        const label = `${slice.name}: ${number(slice.count)} mẫu · ${percent(slice.share, 1)}`;
                        return (
                            <g
                                key={slice.name}
                                tabIndex={0}
                                role="img"
                                aria-label={label}
                                data-active={isActive ? "true" : undefined}
                                onFocus={() => setActiveName(slice.name)}
                                onBlur={() => setActiveName(null)}
                                onMouseEnter={() => setActiveName(slice.name)}
                                onMouseLeave={() => setActiveName(null)}
                            >
                                <title>{label}</title>
                                {slice.share === 1 ? (
                                    <circle
                                        cx="110"
                                        cy="110"
                                        r="96"
                                        fill={slice.color}
                                        data-active={
                                            isActive ? "true" : undefined
                                        }
                                    />
                                ) : (
                                    <path
                                        d={slice.path}
                                        fill={slice.color}
                                        data-active={
                                            isActive ? "true" : undefined
                                        }
                                    />
                                )}
                            </g>
                        );
                    })}
            </svg>
            <div className="class-pie-legend-wrap">
                <div className="class-pie-legend-header" aria-hidden="true">
                    <span>Lớp dự đoán</span>
                    <span>Số mẫu</span>
                    <span>Tỷ lệ</span>
                </div>
                <ul className="class-pie-legend" role="list">
                    {slices.map((slice) => {
                        const isActive = activeName === slice.name;
                        return (
                            <li
                                key={slice.name}
                                tabIndex={0}
                                role="listitem"
                                data-dominant={
                                    slice.isDominant ? "true" : undefined
                                }
                                data-active={isActive ? "true" : undefined}
                                onFocus={() => setActiveName(slice.name)}
                                onBlur={() => setActiveName(null)}
                                onMouseEnter={() => setActiveName(slice.name)}
                                onMouseLeave={() => setActiveName(null)}
                            >
                                <span
                                    className="class-pie-dot"
                                    style={{ background: slice.color }}
                                    aria-hidden="true"
                                />
                                <span>{slice.name}</span>
                                <strong>
                                    {number(slice.count)}
                                    <span className="sr-only"> mẫu</span>
                                </strong>
                                <span className="class-pie-percentage">
                                    {total ? percent(slice.share, 1) : "—"}
                                </span>
                            </li>
                        );
                    })}
                </ul>
            </div>
            <p className="class-pie-detail" aria-live="polite">
                {activeSlice ? (
                    <>
                        Đang xem: <strong>{activeSlice.name}</strong> ·{" "}
                        <b>{number(activeSlice.count)}</b> mẫu (
                        {total ? percent(activeSlice.share, 1) : "—"})
                    </>
                ) : total > 0 && dominantSlice && dominantSlice.count > 0 ? (
                    <>
                        Lớp nhiều nhất: <strong>{dominantSlice.name}</strong> ·{" "}
                        <b>{number(dominantSlice.count)}</b> mẫu (
                        {percent(dominantSlice.share, 1)})
                    </>
                ) : (
                    <>Chưa có mẫu dự đoán trong khoảng thời gian đã chọn.</>
                )}
            </p>
        </div>
    );
}
