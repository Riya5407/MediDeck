/** API response types mirroring API_SPEC.md exactly. */

export interface HealthResponse {
  status: string;
}

export interface MetaResponse {
  payment_modes: string[];
  po_statuses: string[];
  low_stock_threshold: number;
  expiry_warning_days: number;
}

export type CategoriesResponse = string[];

export interface BatchCounts {
  total: number;
  expired: number;
  expiring_soon: number;
  valid: number;
}

export interface Batch {
  batch_no: number;
  med_no: number;
  med_name?: string;
  mfg_date?: string | null;
  exp_date?: string | null;
  qty_in_stock: number;
  pur_price?: number | null;
  status: "expired" | "out_of_stock" | "expiring_soon" | "low_stock" | "in_stock";
  days_to_expiry?: number | null;
}

export interface BatchInput {
  med_no: number;
  mfg_date?: string | null;
  exp_date?: string | null;
  qty_in_stock: number;
  pur_price?: number | null;
}

export interface Medicine {
  med_no: number;
  med_name: string;
  category?: string | null;
  manufacturer?: string | null;
  unit?: string | null;
  mrp?: number | null;
  total_stock: number;
  status: "in_stock" | "low_stock" | "out_of_stock";
  nearest_expiry?: string | null;
}

export interface MedicineDetail extends Medicine {
  batches: Batch[];
}

export interface MedicineInput {
  med_name: string;
  category?: string | null;
  manufacturer?: string | null;
  unit?: string | null;
  mrp?: number | null;
}

export interface Employee {
  emp_no: number;
  emp_name: string;
  emp_role?: string | null;
  salary?: number | null;
  phone_no?: string | null;
}

export interface EmployeeInput {
  emp_name: string;
  emp_role?: string | null;
  salary?: number | null;
  phone_no?: string | null;
}

export interface Customer {
  cust_no: number;
  cust_name: string;
  age?: number | null;
  phone_no?: string | null;
  address?: string | null;
}

export interface CustomerInput {
  cust_name: string;
  age?: number | null;
  phone_no?: string | null;
  address?: string | null;
}

export interface CustomerHistorySale {
  bill_no: number;
  sale_date: string;
  cust_name?: string | null;
  emp_name?: string | null;
  payment_mode: string;
  total_amt: number;
  item_count: number;
}

export interface CustomerHistoryPrescription {
  pres_no: number;
  cust_no: number;
  cust_name?: string | null;
  doc_name?: string | null;
  pres_date: string;
  diagnosis?: string | null;
  item_count: number;
}

export interface CustomerHistory {
  sales: CustomerHistorySale[];
  prescriptions: CustomerHistoryPrescription[];
}

export interface Supplier {
  sup_no: number;
  sup_name: string;
  address?: string | null;
  gst_no?: string | null;
  phones: string[];
}

export interface SupplierInput {
  sup_name: string;
  address?: string | null;
  gst_no?: string | null;
  phones: string[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface PaginatedBatchesResponse extends PaginatedResponse<Batch> {
  counts: BatchCounts;
}
