"use client";
import Link from "next/link";
export default function DashboardError({ reset }: { reset: () => void }) {
    return (
        <div className="notice error" role="alert">
            <h1>Chưa tải được màn hình</h1>
            <p>Thử tải lại hoặc trở về lịch sử lần chạy.</p>
            <button onClick={reset}>Thử lại</button>
            <Link href="/runs">Lịch sử</Link>
        </div>
    );
}
