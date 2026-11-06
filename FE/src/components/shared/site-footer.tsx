import Link from "next/link";
import { ArrowUpRight, ShieldCheck } from "lucide-react";
import { APP_FULL_NAME, APP_NAME } from "@/lib/brand";

// Thông tin nhóm được đối chiếu với Đề cương đồ án tốt nghiệp.docx.
const STUDENTS = [
    { name: "Nguyễn Ngọc Dương", id: "B22DCVT112", className: "D22VTHI02" },
    { name: "Hà Minh Hải", id: "B22DCVT173", className: "D22VTMD03" },
    { name: "Tạ Trung Kiên", id: "B22DCVT265", className: "D22VTMD01" },
];

export function SiteFooter() {
    return (
        <footer className="site-footer" aria-label="Thông tin NIDR">
            <div className="site-footer-inner">
                <section className="site-footer-brand" aria-label="Về NIDR">
                    <Link className="site-footer-logo" href="/dashboard">
                        <ShieldCheck aria-hidden="true" />
                        <span>{APP_NAME}</span>
                    </Link>
                    <p>{APP_FULL_NAME}</p>
                    <p>
                        Hệ thống phát hiện xâm nhập mạng IoT, giải thích bằng
                        SHAP và diễn giải Gemini.
                    </p>
                    <span>Đồ án tốt nghiệp · Nhóm số 07</span>
                </section>
                <section aria-labelledby="footer-institution">
                    <h2 id="footer-institution">Đơn vị đào tạo</h2>
                    <a
                        className="site-footer-institution"
                        href="https://ptit.edu.vn/"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Học viện Công nghệ Bưu chính Viễn thông
                        <ArrowUpRight className="icon" aria-hidden="true" />
                    </a>
                    <p>
                        Khoa Viễn thông I<br />
                        Bộ môn Mạng viễn thông
                    </p>
                    <p>
                        Kỹ thuật Điện tử Viễn thông
                        <br />
                        Chính quy · Khóa 2022–2026
                    </p>
                </section>
                <section aria-labelledby="footer-team">
                    <h2 id="footer-team">Nhóm thực hiện</h2>
                    <ul className="site-footer-team">
                        {STUDENTS.map((student) => (
                            <li key={student.id}>
                                <span>{student.name}</span>
                                <small>
                                    {student.id} · {student.className}
                                </small>
                            </li>
                        ))}
                    </ul>
                </section>
                <nav aria-labelledby="footer-navigation">
                    <h2 id="footer-navigation">Liên kết nhanh</h2>
                    <ul className="site-footer-links">
                        <li>
                            <Link href="/dashboard">Tổng quan</Link>
                        </li>
                        <li>
                            <Link href="/runs">Lịch sử lần chạy</Link>
                        </li>
                        <li>
                            <Link href="/runs/new">Tạo lần chạy</Link>
                        </li>
                        <li>
                            <Link href="/alerts">Trung tâm cảnh báo</Link>
                        </li>
                        <li>
                            <a
                                href="/docs"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                Tài liệu API{" "}
                                <ArrowUpRight
                                    className="icon"
                                    aria-hidden="true"
                                />
                            </a>
                        </li>
                    </ul>
                </nav>
            </div>
            <div className="site-footer-bottom">
                <div>
                    <span>NIDR · Nhóm 07 · 2026</span>
                    <span>Dữ liệu CICIoT2023 · SHAP · Gemini</span>
                </div>
            </div>
        </footer>
    );
}
