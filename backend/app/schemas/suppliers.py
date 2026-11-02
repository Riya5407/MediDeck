from typing import Optional, List
from pydantic import BaseModel, Field


class SupplierBase(BaseModel):
    sup_name: str = Field(..., min_length=1)
    address: Optional[str] = None
    gst_no: Optional[str] = None
    phones: List[str] = []


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(SupplierBase):
    pass


class SupplierOut(SupplierBase):
    sup_no: int


class PaginatedSuppliers(BaseModel):
    items: List[SupplierOut]
    total: int
    page: int
    page_size: int

