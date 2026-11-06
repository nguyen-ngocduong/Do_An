import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import { APP_FULL_NAME, APP_NAME } from "@/lib/brand";
import "./globals.css";

const inter = Inter({
    subsets: ["latin", "vietnamese"],
    variable: "--font-ui",
});
const mono = JetBrains_Mono({
    subsets: ["latin", "vietnamese"],
    variable: "--font-mono",
});
export const metadata: Metadata = {
    title: APP_NAME,
    applicationName: APP_NAME,
    description:
        `${APP_FULL_NAME} — Dự đoán CICIoT2023, bằng chứng SHAP và diễn giải Gemini bằng tiếng Việt.`,
    icons: { icon: "/icon.svg" },
};
export default function RootLayout({
    children,
}: Readonly<{ children: React.ReactNode }>) {
    return (
        <html lang="vi" className={`${inter.variable} ${mono.variable}`}>
            <body>{children}</body>
        </html>
    );
}
