from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from psycopg import AsyncConnection

from app.db import get_db
from app.schemas.purchase_orders import (
    POCreate,
    POStatusUpdate,
    POReceiveInput,
    POOut,
    POReceiveResponse,
    PaginatedPOs,
)
from app.repositories import purchase_orders as po_repo

router = APIRouter(prefix="/api/purchase-orders", tags=["purchase-orders"])


@router.get("", response_model=PaginatedPOs)
async def list_purchase_orders(
    status: Optional[str] = Query(None, description="Filter by status (Pending, Delivered, Cancelled)"),
    sup_no: Optional[int] = Query(None, description="Filter by supplier sup_no"),
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    conn: AsyncConnection = Depends(get_db),
):
    """List purchase orders newest first, paginated."""
    return await po_repo.get_purchase_orders(
        conn, status=status, sup_no=sup_no, from_date=from_date, to_date=to_date, page=page, page_size=page_size
    )


@router.get("/{pur_no}", response_model=POOut)
async def get_purchase_order(
    pur_no: int,
    conn: AsyncConnection = Depends(get_db),
):
    """Get purchase order with lines."""
    return await po_repo.get_po_by_id(conn, pur_no)


@router.post("", response_model=POOut, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    payload: POCreate,
    conn: AsyncConnection = Depends(get_db),
):
    """Create purchase order in Pending status."""
    return await po_repo.create_po(conn, payload.model_dump())


@router.patch("/{pur_no}/status", response_model=POOut)
async def update_po_status(
    pur_no: int,
    payload: POStatusUpdate,
    conn: AsyncConnection = Depends(get_db),
):
    """Cancel a purchase order (allowed only if Pending)."""
    return await po_repo.cancel_po(conn, pur_no)


@router.post("/{pur_no}/receive", response_model=POReceiveResponse)
async def receive_purchase_order(
    pur_no: int,
    payload: POReceiveInput,
    conn: AsyncConnection = Depends(get_db),
):
    """Receive order lines into inventory batches and transition order to Delivered."""
    return await po_repo.receive_po(conn, pur_no, payload.model_dump())

