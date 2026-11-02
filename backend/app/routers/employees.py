from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from psycopg import AsyncConnection

from app.db import get_db
from app.auth import require_roles
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
    user: dict = Depends(require_roles("admin", "pharmacist", "cashier")),
):
    """List employees paginated. Non-admin users receive only employee ID and name."""
    result = await emp_repo.get_employees(conn, search=search, page=page, page_size=page_size)
    if user.get("role") != "admin":
        sanitized_items = []
        for item in result.get("items", []):
            sanitized_items.append({
                "emp_no": item["emp_no"],
                "emp_name": item["emp_name"],
                "emp_role": item.get("emp_role"),
                "salary": None,
                "phone_no": None,
            })
        result = {**result, "items": sanitized_items}
    return result


@router.get("/{emp_no}", response_model=EmployeeOut)
async def get_employee(
    emp_no: int,
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin")),
):
    """Get single employee by ID."""
    return await emp_repo.get_employee_by_id(conn, emp_no)


@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee(
    payload: EmployeeCreate,
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin")),
):
    """Create a new employee."""
    return await emp_repo.create_employee(conn, payload.model_dump())


@router.put("/{emp_no}", response_model=EmployeeOut)
async def update_employee(
    emp_no: int,
    payload: EmployeeUpdate,
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin")),
):
    """Update an employee."""
    return await emp_repo.update_employee(conn, emp_no, payload.model_dump())


@router.delete("/{emp_no}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    emp_no: int,
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin")),
):
    """Delete an employee. 409 if they have recorded sales."""
    await emp_repo.delete_employee(conn, emp_no)
