from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from psycopg import AsyncConnection

from app.db import get_db
from app.auth import require_roles
from app.schemas.batches import (
    BatchCreate,
    BatchUpdate,
    BatchOut,
    PaginatedBatches,
)
from app.repositories import batches as batch_repo

router = APIRouter(prefix="/api/batches", tags=["batches"])


@router.get("", response_model=PaginatedBatches)
async def list_batches(
    search: Optional[str] = Query(None, description="Search by medicine name"),
    status: Optional[str] = Query(None, description="Filter by status (expired, out_of_stock, expiring_soon, low_stock, in_stock)"),
    med_no: Optional[int] = Query(None, description="Filter by med_no"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin", "pharmacist", "cashier")),
):
    """List batches ordered soonest expiry first, with summary counts."""
    return await batch_repo.get_batches(
        conn, search=search, status=status, med_no=med_no, page=page, page_size=page_size
    )


@router.post("", response_model=BatchOut, status_code=status.HTTP_201_CREATED)
async def create_batch(
    payload: BatchCreate,
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin", "pharmacist")),
):
    """Create a new medicine batch."""
    return await batch_repo.create_batch(conn, payload.model_dump())


@router.put("/{batch_no}", response_model=BatchOut)
async def update_batch(
    batch_no: int,
    payload: BatchUpdate,
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin", "pharmacist")),
):
    """Update a batch."""
    return await batch_repo.update_batch(conn, batch_no, payload.model_dump())


@router.delete("/{batch_no}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_batch(
    batch_no: int,
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin", "pharmacist")),
):
    """Delete a batch. Fails with 409 if sold from."""
    await batch_repo.delete_batch(conn, batch_no)
