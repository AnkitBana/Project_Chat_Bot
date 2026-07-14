/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",   // enables Docker multi-stage build
  // Dev: proxy /api/* to FastAPI on :8000
  // Production: NEXT_PUBLIC_API_URL env var is used instead
  async rewrites() {
    return process.env.NODE_ENV === "development"
      ? [{ source: "/api/:path*", destination: "http://localhost:8000/api/:path*" }]
      : [];
  },
};

export default nextConfig;
