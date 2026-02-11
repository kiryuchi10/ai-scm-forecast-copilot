const baseURL = import.meta.env.VITE_API_BASE_URL ?? "";

export async function apiGet<T>(path: string, params?: Record<string, string | number>): Promise<T> {
  const url = new URL(path, baseURL || window.location.origin);
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, String(v)));
  }
  const res = await fetch(url.toString(), { credentials: "omit" });
  if (!res.ok) {
    let msg = `API ${res.status}: ${res.statusText}`;
    let errorType: string | undefined;
    try {
      const body = (await res.json()) as { detail?: string; error_type?: string };
      if (body?.detail) msg += ` — ${body.detail}`;
      errorType = body?.error_type;
    } catch {
      /* ignore */
    }
    const err = new Error(msg) as Error & { errorType?: string };
    err.errorType = errorType;
    throw err;
  }
  return res.json() as Promise<T>;
}
