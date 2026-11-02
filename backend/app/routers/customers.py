from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from psycopg import AsyncConnection

from app.db import get_db
from app.schemas.customers import (
    CustomerCreate,
    CustomerUpdate,
    CustomerOut,
    PaginatedCustomers,
    CustomerHistoryOut,
)
from app.repositories import customers as cust_repo

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=PaginatedCustomers)
async def list_customers(
    search: Optional[str] = Query(None, description="Search by name or phone"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    conn: AsyncConnection = Depends(get_db),
):
    """List customers with search and pagination."""
    return await cust_repo.get_customers(conn, search=search, page=page, page_size=page_size)


@router.get("/{cust_no}", response_model=CustomerOut)
async def get_customer(
    cust_no: int,
    conn: AsyncConnection = Depends(get_db),
):
    """Get single customer by ID."""
    return await cust_repo.get_customer_by_id(conn, cust_no)


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate,
    conn: AsyncConnection = Depends(get_db),
):
    """Create a new customer."""
    return await cust_repo.create_customer(conn, payload.model_dump())


@router.put("/{cust_no}", response_model=CustomerOut)
async def update_customer(
    cust_no: int,
    payload: CustomerUpdate,
    conn: AsyncConnection = Depends(get_db),
):
    """Update a customer."""
    return await cust_repo.update_customer(conn, cust_no, payload.model_dump())


@router.delete("/{cust_no}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    cust_no: int,
    conn: AsyncConnection = Depends(get_db),
):
    """Delete a customer. 409 if they have bills or prescriptions."""
    await cust_repo.delete_customer(conn, cust_no)


@router.get("/{cust_no}/history", response_model=CustomerHistoryOut)
async def get_customer_history(
    cust_no: int,
    conn: AsyncConnection = Depends(get_db),
):
    """Get customer purchase and prescription history."""
    return await cust_repo.get_customer_history(conn, cust_no)

