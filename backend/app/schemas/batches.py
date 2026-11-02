from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


class BatchCounts(BaseModel):
    total: int
    expired: int
    expiring_soon: int
    valid: int


class BatchBase(BaseModel):
    med_no: int
    mfg_date: Optional[date] = None
    exp_date: Optional[date] = None
    qty_in_stock: int = Field(..., ge=0)
    pur_price: Optional[float] = Field(None, ge=0)


class BatchCreate(BatchBase):
    pass


class BatchUpdate(BatchBase):
    pass


class BatchOut(BaseModel):
    batch_no: int
    med_no: int
    med_name: Optional[str] = None
    mfg_date: Optional[date] = None
    exp_date: Optional[date] = None
    qty_in_stock: int
    pur_price: Optional[float] = None
    status: str
    days_to_expiry: Optional[int] = None


class PaginatedBatches(BaseModel):
    items: List[BatchOut]
    total: int
    page: int
    page_size: int
    counts: BatchCounts

