import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { request } from "./client";
import type { PaginatedResponse } from "./types";

export interface POLineOut {
  med_no: number;
  med_name: string;
  qty_ordered: number;
  rate: number;
  line_total: number;
}

export interface POOut {
  pur_no: number;
  sup_no: number;
  sup_name?: string | null;
  order_date: string;
  status: string;
  total: number;
  lines: POLineOut[];
}

export interface POListItem {
  pur_no: number;
  sup_no: number;
  sup_name?: string | null;
  order_date: string;
  status: string;
  total: number;
}

export interface POLineInput {
  med_no: number;
  qty_ordered: number;
  rate: number;
}

export interface POCreate {
  sup_no: number;
  lines: POLineInput[];
}

export interface POReceiveLine {
  med_no: number;
  qty_received?: number | null;
  mfg_date?: string | null;
  exp_date: string;
}

export interface POReceiveInput {
  lines: POReceiveLine[];
}

export interface POReceiveResponse extends POOut {
  created_batches: number[];
}

export interface POQueryParams {
  status?: string;
  sup_no?: number;
  from?: string;
  to?: string;
  page?: number;
  page_size?: number;
}

export function usePurchaseOrders(params: POQueryParams) {
  const qs = new URLSearchParams();
  if (params.status) qs.set("status", params.status);
  if (params.sup_no) qs.set("sup_no", params.sup_no.toString());
  if (params.from) qs.set("from", params.from);
  if (params.to) qs.set("to", params.to);
  if (params.page) qs.set("page", params.page.toString());
  if (params.page_size) qs.set("page_size", params.page_size.toString());
  const queryStr = qs.toString() ? `?${qs.toString()}` : "";
  return useQuery({
    queryKey: ["purchase-orders", params],
    queryFn: () => request<PaginatedResponse<POListItem>>(`/api/purchase-orders${queryStr}`),
  });
}

export function usePurchaseOrder(pur_no?: number) {
  return useQuery({
    queryKey: ["purchase-orders", pur_no],
    queryFn: () => request<POOut>(`/api/purchase-orders/${pur_no}`),
    enabled: Boolean(pur_no),
  });
}

export function useCreatePurchaseOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: POCreate) =>
      request<POOut>("/api/purchase-orders", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["purchase-orders"] });
    },
  });
}

export function useCancelPurchaseOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (pur_no: number) =>
      request<POOut>(`/api/purchase-orders/${pur_no}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status: "Cancelled" }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["purchase-orders"] });
    },
  });
}

export function useReceivePurchaseOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ pur_no, data }: { pur_no: number; data: POReceiveInput }) =>
      request<POReceiveResponse>(`/api/purchase-orders/${pur_no}/receive`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["purchase-orders"] });
      queryClient.invalidateQueries({ queryKey: ["batches"] });
      queryClient.invalidateQueries({ queryKey: ["medicines"] });
    },
  });
}

