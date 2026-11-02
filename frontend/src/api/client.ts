/**
 * Fetch wrapper for the MediDesk API.
 * - Base URL from VITE_API_URL environment variable.
 * - Parses JSON when there is a body (handles 204 No Content).
 * - On HTTP error, throws { detail: "..." } using the server's message.
 * - On network failure, throws { detail: "Cannot reach the server" }.
 */

const BASE = import.meta.env.VITE_API_URL ?? "";

export interface ApiError {
  detail: string;
}

export async function request<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  let resp: Response;
  try {
    resp = await fetch(`${BASE}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });
  } catch {
    throw { detail: "Cannot reach the server" } satisfies ApiError;
  }

  // 204 No Content — no body to parse
  if (resp.status === 204) {
    return undefined as T;
  }

  let data: unknown;
  try {
    data = await resp.json();
  } catch {
    if (!resp.ok) {
      throw { detail: resp.statusText } satisfies ApiError;
    }
    return undefined as T;
  }

  if (!resp.ok) {
    const detail =
      (data as Record<string, unknown>)?.detail ?? resp.statusText;
    throw { detail: String(detail) } satisfies ApiError;
  }

  return data as T;
}

