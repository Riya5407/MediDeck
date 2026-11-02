import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { request } from "./client";
import type { Batch, BatchInput, PaginatedBatchesResponse } from "./types";

export interface BatchQueryParams {
  search?: string;
  status?: string;
  med_no?: number;
  page?: number;
  page_size?: number;
}

export function useBatches(params: BatchQueryParams) {
  const queryParams = new URLSearchParams();
  if (params.search) queryParams.set("search", params.search);
  if (params.status) queryParams.set("status", params.status);
  if (params.med_no) queryParams.set("med_no", params.med_no.toString());
  if (params.page) queryParams.set("page", params.page.toString());
  if (params.page_size) queryParams.set("page_size", params.page_size.toString());

  const queryStr = queryParams.toString() ? `?${queryParams.toString()}` : "";

  return useQuery({
    queryKey: ["batches", params],
    queryFn: () => request<PaginatedBatchesResponse>(`/api/batches${queryStr}`),
  });
}

export function useCreateBatch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: BatchInput) =>
      request<Batch>("/api/batches", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["batches"] });
      queryClient.invalidateQueries({ queryKey: ["medicines"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useUpdateBatch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ batch_no, data }: { batch_no: number; data: BatchInput }) =>
      request<Batch>(`/api/batches/${batch_no}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["batches"] });
      queryClient.invalidateQueries({ queryKey: ["medicines"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useDeleteBatch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (batch_no: number) =>
      request<void>(`/api/batches/${batch_no}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["batches"] });
      queryClient.invalidateQueries({ queryKey: ["medicines"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

