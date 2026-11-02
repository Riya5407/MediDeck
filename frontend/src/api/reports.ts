import { useQuery } from "@tanstack/react-query";
import { request } from "./client";

export interface SalesByDateRow {
  date: string;
  bills: number;
  total: number;
}

export interface TopMedicineRow {
  med_no: number;
  med_name: string;
  qty_sold: number;
  revenue: number;
}

export interface ExpiredBatch {
  batch_no: number;
  med_no: number;
  med_name: string;
  exp_date: string;
  qty_in_stock: number;
  pur_price?: number | null;
  days_to_expiry: number;
  status: string;
  value: number;
}

export interface ExpiredStockResponse {
  items: ExpiredBatch[];
  total_value: number;
}

export interface PurchasesBySupplierRow {
  sup_no: number;
  sup_name: string;
  orders: number;
  total: number;
}

export interface ReportParams {
  from?: string;
  to?: string;
}

function buildQs(params: ReportParams & { limit?: number }): string {
  const qs = new URLSearchParams();
  if (params.from) qs.set("from", params.from);
  if (params.to) qs.set("to", params.to);
  if (params.limit) qs.set("limit", params.limit.toString());
  return qs.toString() ? `?${qs.toString()}` : "";
}

export function useSalesByDate(params: ReportParams) {
  return useQuery({
    queryKey: ["reports", "sales-by-date", params],
    queryFn: () =>
      request<SalesByDateRow[]>(`/api/reports/sales-by-date${buildQs(params)}`),
  });
}

export function useTopMedicines(params: ReportParams & { limit?: number }) {
  return useQuery({
    queryKey: ["reports", "top-medicines", params],
    queryFn: () =>
      request<TopMedicineRow[]>(`/api/reports/top-medicines${buildQs(params)}`),
  });
}

export function useExpiredStock() {
  return useQuery({
    queryKey: ["reports", "expired-stock"],
    queryFn: () => request<ExpiredStockResponse>("/api/reports/expired-stock"),
  });
}

export function usePurchasesBySupplier(params: ReportParams) {
  return useQuery({
    queryKey: ["reports", "purchases-by-supplier", params],
    queryFn: () =>
      request<PurchasesBySupplierRow[]>(
        `/api/reports/purchases-by-supplier${buildQs(params)}`
      ),
  });
}

export function csvUrl(endpoint: string, params: ReportParams & { limit?: number }): string {
  const qs = new URLSearchParams();
  if (params.from) qs.set("from", params.from);
  if (params.to) qs.set("to", params.to);
  if (params.limit) qs.set("limit", params.limit.toString());
  qs.set("format", "csv");
  return `/api/reports/${endpoint}?${qs.toString()}`;
}

