from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


class MedicineBase(BaseModel):
    med_name: str = Field(..., min_length=1)
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    unit: Optional[str] = None
    mrp: Optional[float] = None


class MedicineCreate(MedicineBase):
    pass


class MedicineUpdate(MedicineBase):
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


class MedicineOut(MedicineBase):
    med_no: int
    total_stock: int
    status: str
    nearest_expiry: Optional[date] = None


class MedicineDetailOut(MedicineOut):
    batches: List[BatchOut] = []


class PaginatedMedicines(BaseModel):
    items: List[MedicineOut]
    total: int
    page: int
    page_size: int

