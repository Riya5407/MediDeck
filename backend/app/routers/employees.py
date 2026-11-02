from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from psycopg import AsyncConnection

from app.db import get_db
from app.schemas.employees import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeOut,
    PaginatedEmployees,
)
from app.repositories import employees as emp_repo

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.get("", response_model=PaginatedEmployees)
async def list_employees(
    search: Optional[str] = Query(None, description="Search by name, role, or phone"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    conn: AsyncConnection = Depends(get_db),
):
    """List employees paginated (Billing dropdown uses page_size=100)."""
    return await emp_repo.get_employees(conn, search=search, page=page, page_size=page_size)


@router.get("/{emp_no}", response_model=EmployeeOut)
async def get_employee(
    emp_no: int,
    conn: AsyncConnection = Depends(get_db),
):
    """Get single employee by ID."""
    return await emp_repo.get_employee_by_id(conn, emp_no)


@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee(
    payload: EmployeeCreate,
    conn: AsyncConnection = Depends(get_db),
):
    """Create a new employee."""
    return await emp_repo.create_employee(conn, payload.model_dump())


@router.put("/{emp_no}", response_model=EmployeeOut)
async def update_employee(
    emp_no: int,
    payload: EmployeeUpdate,
    conn: AsyncConnection = Depends(get_db),
):
    """Update an employee."""
    return await emp_repo.update_employee(conn, emp_no, payload.model_dump())


@router.delete("/{emp_no}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    emp_no: int,
    conn: AsyncConnection = Depends(get_db),
):
    """Delete an employee. 409 if they have recorded sales."""
    await emp_repo.delete_employee(conn, emp_no)
