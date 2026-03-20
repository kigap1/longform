const defaultApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

function createRemotePattern(origin) {
  const url = new URL(origin);
  return {
    protocol: url.protocol.replace(":", ""),
    hostname: url.hostname,
    port: url.port,
    pathname: "/**"
  };
}

const apiOrigins = Array.from(
  new Set([
    defaultApiBaseUrl.replace(/\/api\/?$/, ""),
    "http://localhost:8000",
    "http://127.0.0.1:8000"
  ])
);

/** @type {import('next').NextConfig} */
const nextConfig = {
  typedRoutes: true,
  images: {
    remotePatterns: apiOrigins.map(createRemotePattern)
  }
};

export default nextConfig;
