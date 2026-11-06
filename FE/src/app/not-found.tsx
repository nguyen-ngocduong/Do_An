import Link from "next/link";
import { SiteFooter } from "@/components/shared/site-footer";
export default function NotFound() {
    return (
        <div className="public-page">
            <main>
                <h1>Không tìm thấy trang</h1>
                <p>Kiểm tra đường dẫn, ID lần chạy hoặc chỉ số dòng.</p>
                <Link className="button" href="/runs">
                    Về lịch sử lần chạy
                </Link>
            </main>
            <SiteFooter />
        </div>
    );
}
