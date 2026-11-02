import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { request } from "./client";
import type {
  Medicine,
  MedicineDetail,
  MedicineInput,
  PaginatedResponse,
  CategoriesResponse,
} from "./types";

export interface MedicineQueryParams {
  search?: string;
  category?: string;
  status?: string;
  page?: number;
  page_size?: number;
}

export function useMedicines(params: MedicineQueryParams) {
  const queryParams = new URLSearchParams();
  if (params.search) queryParams.set("search", params.search);
  if (params.category) queryParams.set("category", params.category);
  if (params.status) queryParams.set("status", params.status);
  if (params.page) queryParams.set("page", params.page.toString());
  if (params.page_size) queryParams.set("page_size", params.page_size.toString());

  const queryStr = queryParams.toString() ? `?${queryParams.toString()}` : "";

  return useQuery({
    queryKey: ["medicines", params],
    queryFn: () => request<PaginatedResponse<Medicine>>(`/api/medicines${queryStr}`),
  });
}

export function useMedicine(med_no?: number) {
  return useQuery({
    queryKey: ["medicines", med_no],
    queryFn: () => request<MedicineDetail>(`/api/medicines/${med_no}`),
    enabled: Boolean(med_no),
  });
}

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: () => request<CategoriesResponse>("/api/categories"),
  });
}

export function useCreateMedicine() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: MedicineInput) =>
      request<MedicineDetail>("/api/medicines", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["medicines"] });
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useUpdateMedicine() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ med_no, data }: { med_no: number; data: MedicineInput }) =>
      request<MedicineDetail>(`/api/medicines/${med_no}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["medicines"] });
      queryClient.invalidateQueries({ queryKey: ["medicines", variables.med_no] });
      queryClient.invalidateQueries({ queryKey: ["categories"] });
    },
  });
}

export function useDeleteMedicine() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (med_no: number) =>
      request<void>(`/api/medicines/${med_no}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["medicines"] });
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

