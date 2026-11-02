"""Dashboard router — section 3 of API_SPEC.md."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from psycopg import AsyncConnection

from app.db import get_db
from app.repositories import dashboard as dash_repo

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
async def get_summary(conn: AsyncConnection = Depends(get_db)):
    """KPI summary cards."""
    return await dash_repo.get_summary(conn)


@router.get("/sales-trend")
async def get_sales_trend(
    days: int = Query(7, ge=1, le=90),
    conn: AsyncConnection = Depends(get_db),
):
    """Daily sales totals for the last N days, zero-filled."""
    return await dash_repo.get_sales_trend(conn, days=days)


@router.get("/stock-alerts")
async def get_stock_alerts(
    limit: int = Query(10, ge=1, le=100),
    conn: AsyncConnection = Depends(get_db),
):
    """Batches not in_stock, worst status first."""
    return await dash_repo.get_stock_alerts(conn, limit=limit)

