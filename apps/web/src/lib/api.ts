export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const headers = new Headers({ "Content-Type": "application/json" });
  if (options?.headers) {
    const extra = new Headers(options.headers);
    extra.forEach((value, key) => headers.set(key, value));
  }

  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}