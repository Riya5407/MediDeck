from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from psycopg import AsyncConnection

from app.db import get_db
from app.schemas.prescriptions import (
    PrescriptionCreate,
    PrescriptionUpdate,
    PrescriptionOut,
    PaginatedPrescriptions,
)
from app.repositories import prescriptions as pres_repo

router = APIRouter(prefix="/api/prescriptions", tags=["prescriptions"])


@router.get("", response_model=PaginatedPrescriptions)
async def list_prescriptions(
    cust_no: Optional[int] = Query(None, description="Filter by customer"),
    search: Optional[str] = Query(None, description="Search doctor or customer"),
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    conn: AsyncConnection = Depends(get_db),
):
    """List prescriptions paginated."""
    return await pres_repo.get_prescriptions(
        conn, cust_no=cust_no, search=search, from_date=from_date, to_date=to_date, page=page, page_size=page_size
    )


@router.get("/{pres_no}", response_model=PrescriptionOut)
async def get_prescription(
    pres_no: int,
    conn: AsyncConnection = Depends(get_db),
):
    """Get single prescription with line items."""
    return await pres_repo.get_prescription_by_id(conn, pres_no)


@router.post("", response_model=PrescriptionOut, status_code=status.HTTP_201_CREATED)
async def create_prescription(
    payload: PrescriptionCreate,
    conn: AsyncConnection = Depends(get_db),
):
    """Create a new prescription record."""
    return await pres_repo.create_prescription(conn, payload.model_dump())


@router.put("/{pres_no}", response_model=PrescriptionOut)
async def update_prescription(
    pres_no: int,
    payload: PrescriptionUpdate,
    conn: AsyncConnection = Depends(get_db),
):
    """Update prescription and replace its items."""
    return await pres_repo.update_prescription(conn, pres_no, payload.model_dump())


@router.delete("/{pres_no}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prescription(
    pres_no: int,
    conn: AsyncConnection = Depends(get_db),
):
    """Delete prescription and details."""
    await pres_repo.delete_prescription(conn, pres_no)

