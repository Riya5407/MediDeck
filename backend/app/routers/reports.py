"""Reports router — section 12 of API_SPEC.md."""
import csv
import io
from typing import Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from psycopg import AsyncConnection

from app.db import get_db
from app.auth import require_roles
from app.repositories import reports as reports_repo

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _default_dates() -> tuple[date, date]:
    to_d = date.today()
    from_d = to_d - timedelta(days=30)
    return from_d, to_d


def _csv_response(rows: list[dict], filename: str) -> StreamingResponse:
    if not rows:
        content = ""
    else:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
        content = buf.getvalue()
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/sales-by-date")
async def sales_by_date(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    format: Optional[str] = Query(None),
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin", "cashier")),
):
    df, dt = _default_dates()
    data = await reports_repo.sales_by_date(
        conn,
        from_date=from_date or df,
        to_date=to_date or dt,
    )
    if format == "csv":
        return _csv_response([dict(r) for r in data], "sales-by-date.csv")
    return data


@router.get("/top-medicines")
async def top_medicines(
    limit: int = Query(10, ge=1, le=100),
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    format: Optional[str] = Query(None),
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin", "cashier")),
):
    df, dt = _default_dates()
    data = await reports_repo.top_medicines(
        conn,
        limit=limit,
        from_date=from_date or df,
        to_date=to_date or dt,
    )
    if format == "csv":
        return _csv_response([dict(r) for r in data], "top-medicines.csv")
    return data


@router.get("/expired-stock")
async def expired_stock(
    format: Optional[str] = Query(None),
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin", "pharmacist")),
):
    data = await reports_repo.expired_stock(conn)
    if format == "csv":
        rows = [dict(r) for r in data["items"]]
        return _csv_response(rows, "expired-stock.csv")
    return data


@router.get("/purchases-by-supplier")
async def purchases_by_supplier(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    format: Optional[str] = Query(None),
    conn: AsyncConnection = Depends(get_db),
    _user: dict = Depends(require_roles("admin")),
):
    df, dt = _default_dates()
    data = await reports_repo.purchases_by_supplier(
        conn,
        from_date=from_date or df,
        to_date=to_date or dt,
    )
    if format == "csv":
        return _csv_response([dict(r) for r in data], "purchases-by-supplier.csv")
    return data
