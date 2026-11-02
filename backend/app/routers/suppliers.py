from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from psycopg import AsyncConnection

from app.db import get_db
from app.auth import require_roles
from app.schemas.suppliers import (
    SupplierCreate,
    SupplierUpdate,
    SupplierOut,
    PaginatedSuppliers,
)
from app.repositories import suppliers as sup_repo

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


@router.get("", response_model=PaginatedSuppliers)
async def list_suppliers(
    search: Optional[str] = Query(None, description="Search by name or GST"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin", "pharmacist")),
):
    """List suppliers with aggregated phones and pagination."""
    return await sup_repo.get_suppliers(conn, search=search, page=page, page_size=page_size)


@router.get("/{sup_no}", response_model=SupplierOut)
async def get_supplier(
    sup_no: int,
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin", "pharmacist")),
):
    """Get single supplier by ID."""
    return await sup_repo.get_supplier_by_id(conn, sup_no)


@router.post("", response_model=SupplierOut, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    payload: SupplierCreate,
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin", "pharmacist")),
):
    """Create a new supplier with optional phones in single transaction."""
    return await sup_repo.create_supplier(conn, payload.model_dump())


@router.put("/{sup_no}", response_model=SupplierOut)
async def update_supplier(
    sup_no: int,
    payload: SupplierUpdate,
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin", "pharmacist")),
):
    """Update supplier and replace phone list."""
    return await sup_repo.update_supplier(conn, sup_no, payload.model_dump())


@router.delete("/{sup_no}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    sup_no: int,
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin", "pharmacist")),
):
    """Delete supplier and phones. 409 if purchase orders exist."""
    await sup_repo.delete_supplier(conn, sup_no)
