from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from psycopg import AsyncConnection

from app.db import get_db
from app.schemas.sales import (
    PosMedicineOut,
    SaleCreate,
    SaleDetailOut,
    PaginatedSales,
)
from app.repositories import sales as sales_repo

router = APIRouter(tags=["sales"])


@router.get("/api/pos/medicines", response_model=List[PosMedicineOut])
async def pos_medicines(
    q: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    conn: AsyncConnection = Depends(get_db),
):
    """POS medicine search returning sellable batches with stock, soonest expiry first."""
    return await sales_repo.search_pos_medicines(conn, q=q, limit=limit)


@router.get("/api/sales", response_model=PaginatedSales)
async def list_sales(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    search: Optional[str] = Query(None, description="Search by bill number or customer name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    conn: AsyncConnection = Depends(get_db),
):
    """List sales bills paginated, newest first."""
    return await sales_repo.get_sales(
        conn, from_date=from_date, to_date=to_date, search=search, page=page, page_size=page_size
    )


@router.get("/api/sales/{bill_no}", response_model=SaleDetailOut)
async def get_sale(
    bill_no: int,
    conn: AsyncConnection = Depends(get_db),
):
    """Get sale detail with lines and discount percentages."""
    return await sales_repo.get_sale_by_id(conn, bill_no)


@router.post("/api/sales", response_model=SaleDetailOut, status_code=status.HTTP_201_CREATED)
async def create_sale(
    payload: SaleCreate,
    conn: AsyncConnection = Depends(get_db),
):
    """Create bill. Triggers reduce stock and calculate total_amt."""
    return await sales_repo.create_sale(conn, payload.model_dump())


@router.delete("/api/sales/{bill_no}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_sale(
    bill_no: int,
    conn: AsyncConnection = Depends(get_db),
):
    """Cancel bill. Deletes lines first (trigger restores stock), then sale."""
    await sales_repo.cancel_sale(conn, bill_no)

