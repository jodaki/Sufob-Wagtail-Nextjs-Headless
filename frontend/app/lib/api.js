export function getApiUrl() {
  // When the code is running on the server (server-side rendering or API routes),
  // `window` is not defined. In this case, we use the internal Docker network URL.
  if (typeof window === 'undefined') {
    return 'http://backend:9000';
  }

  // When the code is running on the client-side, we use the public URL,
  // which is accessible from the user's browser.
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000';
}