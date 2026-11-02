import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { request } from "./client";
import type { Employee, EmployeeInput, PaginatedResponse } from "./types";

export interface EmployeeQueryParams {
  search?: string;
  page?: number;
  page_size?: number;
}

export function useEmployees(params: EmployeeQueryParams) {
  const queryParams = new URLSearchParams();
  if (params.search) queryParams.set("search", params.search);
  if (params.page) queryParams.set("page", params.page.toString());
  if (params.page_size) queryParams.set("page_size", params.page_size.toString());

  const queryStr = queryParams.toString() ? `?${queryParams.toString()}` : "";

  return useQuery({
    queryKey: ["employees", params],
    queryFn: () => request<PaginatedResponse<Employee>>(`/api/employees${queryStr}`),
  });
}

export function useCreateEmployee() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: EmployeeInput) =>
      request<Employee>("/api/employees", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["employees"] });
    },
  });
}

export function useUpdateEmployee() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ emp_no, data }: { emp_no: number; data: EmployeeInput }) =>
      request<Employee>(`/api/employees/${emp_no}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["employees"] });
    },
  });
}

export function useDeleteEmployee() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (emp_no: number) =>
      request<void>(`/api/employees/${emp_no}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["employees"] });
    },
  });
}

