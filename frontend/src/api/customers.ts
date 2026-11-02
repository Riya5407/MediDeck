import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { request } from "./client";
import type { Customer, CustomerInput, CustomerHistory, PaginatedResponse } from "./types";

export interface CustomerQueryParams {
  search?: string;
  page?: number;
  page_size?: number;
}

export function useCustomers(params: CustomerQueryParams) {
  const queryParams = new URLSearchParams();
  if (params.search) queryParams.set("search", params.search);
  if (params.page) queryParams.set("page", params.page.toString());
  if (params.page_size) queryParams.set("page_size", params.page_size.toString());

  const queryStr = queryParams.toString() ? `?${queryParams.toString()}` : "";

  return useQuery({
    queryKey: ["customers", params],
    queryFn: () => request<PaginatedResponse<Customer>>(`/api/customers${queryStr}`),
  });
}

export function useCustomerHistory(cust_no?: number) {
  return useQuery({
    queryKey: ["customers", cust_no, "history"],
    queryFn: () => request<CustomerHistory>(`/api/customers/${cust_no}/history`),
    enabled: Boolean(cust_no),
  });
}

export function useCreateCustomer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CustomerInput) =>
      request<Customer>("/api/customers", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customers"] });
    },
  });
}

export function useUpdateCustomer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ cust_no, data }: { cust_no: number; data: CustomerInput }) =>
      request<Customer>(`/api/customers/${cust_no}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customers"] });
    },
  });
}

export function useDeleteCustomer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (cust_no: number) =>
      request<void>(`/api/customers/${cust_no}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customers"] });
    },
  });
}

