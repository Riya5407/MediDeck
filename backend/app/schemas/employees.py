from typing import Optional, List
from pydantic import BaseModel, Field


class EmployeeBase(BaseModel):
    emp_name: str = Field(..., min_length=1)
    emp_role: Optional[str] = None
    salary: Optional[float] = Field(None, ge=0)
    phone_no: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass


class EmployeeOut(EmployeeBase):
    emp_no: int


class PaginatedEmployees(BaseModel):
    items: List[EmployeeOut]
    total: int
    page: int
    page_size: int

