const path = require("path");

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  outputFileTracingRoot: path.join(__dirname),
  async rewrites() {
    const backendUrl = process.env.Config || "http://localhost:8000";

    return [
      {
        source: "/backend-api/:path*",
        destination: `${backendUrl.replace(/\/+$/, "")}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
