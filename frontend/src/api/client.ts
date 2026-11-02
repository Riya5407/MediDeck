/**
 * Fetch wrapper for the MediDeck API.
 * - Base URL from VITE_API_URL environment variable.
 * - Automatically includes credentials (cookies) on all requests.
 * - Sends X-CSRF-Token on state-changing requests (POST, PUT, PATCH, DELETE).
 * - Parses JSON responses and handles 204 No Content.
 * - On HTTP error, throws { detail: "...", status: number }.
 */

export const API_BASE = import.meta.env.VITE_API_URL ?? "";

export interface ApiError {
  detail: string;
  status?: number;
}

function getCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
  return match ? decodeURIComponent(match[2]) : null;
}

export async function request<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const method = (init?.method || "GET").toUpperCase();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string>),
  };

  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    const csrfToken = getCookie("csrf_token");
    if (csrfToken && !headers["X-CSRF-Token"]) {
      headers["X-CSRF-Token"] = csrfToken;
    }
  }

  let resp: Response;
  try {
    resp = await fetch(`${API_BASE}${path}`, {
      ...init,
      credentials: "include",
      headers,
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
      throw { detail: resp.statusText, status: resp.status } satisfies ApiError;
    }
    return undefined as T;
  }

  if (!resp.ok) {
    const detail =
      (data as Record<string, unknown>)?.detail ?? resp.statusText;
    throw { detail: String(detail), status: resp.status } satisfies ApiError;
  }

  return data as T;
}
