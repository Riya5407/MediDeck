import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { request } from "./client";
import type { Supplier, SupplierInput, PaginatedResponse } from "./types";

export interface SupplierQueryParams {
  search?: string;
  page?: number;
  page_size?: number;
}

export function useSuppliers(params: SupplierQueryParams) {
  const queryParams = new URLSearchParams();
  if (params.search) queryParams.set("search", params.search);
  if (params.page) queryParams.set("page", params.page.toString());
  if (params.page_size) queryParams.set("page_size", params.page_size.toString());

  const queryStr = queryParams.toString() ? `?${queryParams.toString()}` : "";

  return useQuery({
    queryKey: ["suppliers", params],
    queryFn: () => request<PaginatedResponse<Supplier>>(`/api/suppliers${queryStr}`),
  });
}

export function useCreateSupplier() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: SupplierInput) =>
      request<Supplier>("/api/suppliers", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["suppliers"] });
    },
  });
}

export function useUpdateSupplier() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ sup_no, data }: { sup_no: number; data: SupplierInput }) =>
      request<Supplier>(`/api/suppliers/${sup_no}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["suppliers"] });
    },
  });
}

export function useDeleteSupplier() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sup_no: number) =>
      request<void>(`/api/suppliers/${sup_no}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["suppliers"] });
    },
  });
}

