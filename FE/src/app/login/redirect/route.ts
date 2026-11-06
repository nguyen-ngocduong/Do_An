import { loginUrl } from "@/lib/api/auth";

// Nginx chỉ gọi nội bộ khi trang riêng tư chưa được xác thực.
export function GET(request: Request) {
    const next = request.headers.get("x-login-return-to") || "/dashboard";
    return new Response(null, {
        status: 302,
        headers: { Location: loginUrl(next), "Cache-Control": "no-store" },
    });
}
