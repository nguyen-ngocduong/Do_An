import type { NextConfig } from "next";

const target = process.env.API_PROXY_TARGET || "http://127.0.0.1:8000";
const config: NextConfig = {
    output: "standalone",
    reactStrictMode: true,
    devIndicators: false,
    // Giữ bundle và số worker build phù hợp máy local một node.
    experimental: { cpus: 2, proxyClientMaxBodySize: "11mb" },
    async rewrites() {
        return ["/api/:path*", "/docs", "/openapi.json", "/health"].map(
            (path) => ({
                source: path,
                destination: `${target}${path}`,
            }),
        );
    },
};
export default config;
