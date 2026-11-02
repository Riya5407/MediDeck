from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


class POLineInput(BaseModel):
    med_no: int
    qty_ordered: int = Field(..., gt=0)
    rate: float = Field(..., ge=0)


class POCreate(BaseModel):
    sup_no: int
    lines: List[POLineInput] = Field(..., min_length=1)


class POStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^Cancelled$")


class ReceiveLineInput(BaseModel):
    med_no: int
    mfg_date: Optional[date] = None
    exp_date: date
    qty_received: Optional[int] = Field(None, gt=0)


class POReceiveInput(BaseModel):
    lines: List[ReceiveLineInput] = Field(..., min_length=1)


class POLineOut(BaseModel):
    med_no: int
    med_name: str
    qty_ordered: int
    rate: float
    line_total: float


class POOut(BaseModel):
    pur_no: int
    sup_no: int
    sup_name: Optional[str] = None
    order_date: date
    status: str
    total: float
    lines: List[POLineOut] = []


class POReceiveResponse(POOut):
    created_batches: List[int] = []


class POListItem(BaseModel):
    pur_no: int
    sup_no: int
    sup_name: Optional[str] = None
    order_date: date
    status: str
    total: float


class PaginatedPOs(BaseModel):
    items: List[POListItem]
    total: int
    page: int
    page_size: int

