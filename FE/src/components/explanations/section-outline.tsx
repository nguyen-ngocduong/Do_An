"use client";
import { useEffect, useState } from "react";

export function SectionOutline({
    sections,
}: {
    sections: { id: string; label: string }[];
}) {
    const [active, setActive] = useState(sections[0]?.id);
    const keys = sections.map((section) => section.id).join("|");
    useEffect(() => {
        const root = document.getElementById("main-content");
        function update() {
            const boundary =
                root && getComputedStyle(root).overflowY === "auto"
                    ? root.getBoundingClientRect().top + 80
                    : 80;
            const ids = keys.split("|");
            let current = ids[0];
            for (const id of ids) {
                const section = document.getElementById(id);
                if (section && section.getBoundingClientRect().top <= boundary)
                    current = id;
            }
            setActive(current);
        }
        const timer = window.setTimeout(update, 0);
        root?.addEventListener("scroll", update, { passive: true });
        window.addEventListener("scroll", update, { passive: true });
        window.addEventListener("resize", update);
        return () => {
            clearTimeout(timer);
            root?.removeEventListener("scroll", update);
            window.removeEventListener("scroll", update);
            window.removeEventListener("resize", update);
        };
    }, [keys]);
    function goTo(id: string) {
        const section = document.getElementById(id);
        if (!section) return;
        const behavior = matchMedia("(prefers-reduced-motion: reduce)").matches
            ? "auto"
            : "smooth";
        const root = document.getElementById("main-content");
        if (root && getComputedStyle(root).overflowY === "auto") {
            root.scrollTo({
                top:
                    root.scrollTop +
                    section.getBoundingClientRect().top -
                    root.getBoundingClientRect().top -
                    24,
                behavior,
            });
        } else {
            window.scrollTo({
                top: window.scrollY + section.getBoundingClientRect().top - 24,
                behavior,
            });
        }
    }
    return (
        <nav className="section-outline" aria-label="Mục lục nội dung mẫu">
            <strong>Trên trang này</strong>
            {sections.map((section) => (
                <a
                    key={section.id}
                    href={`#${section.id}`}
                    aria-current={
                        active === section.id ? "location" : undefined
                    }
                    onClick={(event) => {
                        event.preventDefault();
                        goTo(section.id);
                    }}
                >
                    {section.label}
                </a>
            ))}
        </nav>
    );
}
