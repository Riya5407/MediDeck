from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


class PosBatchOut(BaseModel):
    batch_no: int
    exp_date: date
    qty_in_stock: int


class PosMedicineOut(BaseModel):
    med_no: int
    med_name: str
    unit: Optional[str] = None
    mrp: Optional[float] = None
    total_stock: int
    batches: List[PosBatchOut] = []


class SaleLineInput(BaseModel):
    med_no: int
    batch_no: int
    qty_sold: int = Field(..., gt=0)
    sale_price: Optional[float] = Field(None, ge=0)


class SaleCreate(BaseModel):
    cust_no: Optional[int] = None
    emp_no: int
    payment_mode: str
    lines: List[SaleLineInput] = Field(..., min_length=1)


class SaleLineOut(BaseModel):
    med_no: int
    med_name: str
    batch_no: int
    qty_sold: int
    sale_price: float
    mrp: Optional[float] = None
    discount_pct: float
    line_total: float


class SaleDetailOut(BaseModel):
    bill_no: int
    sale_date: date
    cust_no: Optional[int] = None
    cust_name: Optional[str] = None
    emp_no: int
    emp_name: Optional[str] = None
    payment_mode: str
    total_amt: float
    lines: List[SaleLineOut] = []


class SaleListItem(BaseModel):
    bill_no: int
    sale_date: date
    cust_name: Optional[str] = None
    emp_name: Optional[str] = None
    payment_mode: str
    total_amt: float
    item_count: int


class PaginatedSales(BaseModel):
    items: List[SaleListItem]
    total: int
    page: int
    page_size: int

