import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { request } from "./client";
import type { PaginatedResponse } from "./types";

export interface PosBatch {
  batch_no: number;
  exp_date: string;
  qty_in_stock: number;
}

export interface PosMedicine {
  med_no: number;
  med_name: string;
  unit?: string | null;
  mrp?: number | null;
  total_stock: number;
  batches: PosBatch[];
}

export interface SaleLineOut {
  med_no: number;
  med_name: string;
  batch_no: number;
  qty_sold: number;
  sale_price: number;
  mrp?: number | null;
  discount_pct: number;
  line_total: number;
}

export interface SaleDetail {
  bill_no: number;
  sale_date: string;
  cust_no?: number | null;
  cust_name?: string | null;
  emp_no: number;
  emp_name?: string | null;
  payment_mode: string;
  total_amt: number;
  lines: SaleLineOut[];
}

export interface SaleListItem {
  bill_no: number;
  sale_date: string;
  cust_name?: string | null;
  emp_name?: string | null;
  payment_mode: string;
  total_amt: number;
  item_count: number;
}

export interface SaleLineInput {
  med_no: number;
  batch_no: number;
  qty_sold: number;
  sale_price?: number | null;
}

export interface SaleCreate {
  cust_no?: number | null;
  emp_no: number;
  payment_mode: string;
  lines: SaleLineInput[];
}

export interface SalesQueryParams {
  from?: string;
  to?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

export function usePosMedicines(q: string) {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  params.set("limit", "50");
  return useQuery({
    queryKey: ["pos-medicines", q],
    queryFn: () => request<PosMedicine[]>(`/api/pos/medicines?${params.toString()}`),
  });
}

export function useSales(params: SalesQueryParams) {
  const qs = new URLSearchParams();
  if (params.from) qs.set("from", params.from);
  if (params.to) qs.set("to", params.to);
  if (params.search) qs.set("search", params.search);
  if (params.page) qs.set("page", params.page.toString());
  if (params.page_size) qs.set("page_size", params.page_size.toString());
  const queryStr = qs.toString() ? `?${qs.toString()}` : "";
  return useQuery({
    queryKey: ["sales", params],
    queryFn: () => request<PaginatedResponse<SaleListItem>>(`/api/sales${queryStr}`),
  });
}

export function useSale(bill_no?: number) {
  return useQuery({
    queryKey: ["sales", bill_no],
    queryFn: () => request<SaleDetail>(`/api/sales/${bill_no}`),
    enabled: Boolean(bill_no),
  });
}

export function useCreateSale() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: SaleCreate) =>
      request<SaleDetail>("/api/sales", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sales"] });
      queryClient.invalidateQueries({ queryKey: ["pos-medicines"] });
      queryClient.invalidateQueries({ queryKey: ["batches"] });
      queryClient.invalidateQueries({ queryKey: ["medicines"] });
    },
  });
}

export function useCancelSale() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (bill_no: number) =>
      request<void>(`/api/sales/${bill_no}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sales"] });
      queryClient.invalidateQueries({ queryKey: ["pos-medicines"] });
      queryClient.invalidateQueries({ queryKey: ["batches"] });
    },
  });
}

