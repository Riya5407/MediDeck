import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { request } from "./client";

export type UserRole = "admin" | "pharmacist" | "cashier";

export interface AuthUser {
  username: string;
  role: UserRole;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface LoginResponse {
  username: string;
  role: UserRole;
  access_token: string;
  csrf_token: string;
}

export interface VerifyResponse {
  valid: boolean;
  username: string;
  role: UserRole;
}

export function useCurrentUser() {
  return useQuery<AuthUser | null>({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      try {
        return await request<AuthUser>("/api/auth/me");
      } catch {
        return null;
      }
    },
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}

export function useLogin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: LoginPayload) =>
      request<LoginResponse>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: (data) => {
      queryClient.setQueryData(["auth", "me"], {
        username: data.username,
        role: data.role,
      });
      queryClient.invalidateQueries();
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () =>
      request<{ status: string }>("/api/auth/logout", {
        method: "POST",
      }),
    onSuccess: () => {
      queryClient.setQueryData(["auth", "me"], null);
      queryClient.clear();
    },
  });
}
