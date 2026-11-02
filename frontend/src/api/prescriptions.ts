import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { request } from "./client";
import type { PaginatedResponse } from "./types";

export interface PrescriptionItem {
  med_no: number;
  med_name: string;
  dosage?: string | null;
  duration?: string | null;
}

export interface Prescription {
  pres_no: number;
  cust_no?: number | null;
  cust_name?: string | null;
  doc_name?: string | null;
  pres_date: string;
  diagnosis?: string | null;
  items: PrescriptionItem[];
}

export interface PrescriptionListItem {
  pres_no: number;
  cust_no?: number | null;
  cust_name?: string | null;
  doc_name?: string | null;
  pres_date: string;
  diagnosis?: string | null;
  item_count: number;
}

export interface PrescriptionItemInput {
  med_no: number;
  dosage?: string | null;
  duration?: string | null;
}

export interface PrescriptionCreate {
  cust_no?: number | null;
  doc_name?: string | null;
  pres_date: string;
  diagnosis?: string | null;
  items: PrescriptionItemInput[];
}

export type PrescriptionUpdate = PrescriptionCreate;

export interface PrescriptionQueryParams {
  cust_no?: number;
  search?: string;
  from?: string;
  to?: string;
  page?: number;
  page_size?: number;
}

export function usePrescriptions(params: PrescriptionQueryParams) {
  const qs = new URLSearchParams();
  if (params.cust_no) qs.set("cust_no", params.cust_no.toString());
  if (params.search) qs.set("search", params.search);
  if (params.from) qs.set("from", params.from);
  if (params.to) qs.set("to", params.to);
  if (params.page) qs.set("page", params.page.toString());
  if (params.page_size) qs.set("page_size", params.page_size.toString());
  const queryStr = qs.toString() ? `?${qs.toString()}` : "";
  return useQuery({
    queryKey: ["prescriptions", params],
    queryFn: () => request<PaginatedResponse<PrescriptionListItem>>(`/api/prescriptions${queryStr}`),
  });
}

export function usePrescription(pres_no?: number) {
  return useQuery({
    queryKey: ["prescriptions", pres_no],
    queryFn: () => request<Prescription>(`/api/prescriptions/${pres_no}`),
    enabled: Boolean(pres_no),
  });
}

export function useCreatePrescription() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PrescriptionCreate) =>
      request<Prescription>("/api/prescriptions", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["prescriptions"] });
    },
  });
}

export function useUpdatePrescription() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ pres_no, data }: { pres_no: number; data: PrescriptionUpdate }) =>
      request<Prescription>(`/api/prescriptions/${pres_no}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["prescriptions"] });
      queryClient.invalidateQueries({ queryKey: ["prescriptions", variables.pres_no] });
    },
  });
}

export function useDeletePrescription() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (pres_no: number) =>
      request<void>(`/api/prescriptions/${pres_no}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["prescriptions"] });
    },
  });
}

