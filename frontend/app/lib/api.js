export function getApiUrl() {
  if (typeof window === "undefined") {
    // Server-side (SSR or API from frontend container)
    return "http://backend:9000";
  }
  // Client-side (browser)
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:9000";
}