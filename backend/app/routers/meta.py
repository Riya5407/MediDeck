"""Meta endpoints: /api/health, /api/meta, /api/categories."""
from fastapi import APIRouter, Depends

from app.config import settings
from app.db import get_db

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/health")
async def health(conn=Depends(get_db)):
    """Health check – also verifies the database connection."""
    await conn.execute("SELECT 1")
    return {"status": "ok"}


@router.get("/meta")
async def meta():
    """Return application-level constants."""
    return {
        "payment_modes": [m.strip() for m in settings.PAYMENT_MODES.split(",")],
        "po_statuses": ["Pending", "Delivered", "Cancelled"],
        "low_stock_threshold": settings.LOW_STOCK_THRESHOLD,
        "expiry_warning_days": settings.EXPIRY_WARNING_DAYS,
    }


@router.get("/categories")
async def categories(conn=Depends(get_db)):
    """Return distinct medicine categories."""
    cur = await conn.execute(
        "SELECT DISTINCT category FROM medicine ORDER BY category"
    )
    rows = await cur.fetchall()
    return [row["category"] for row in rows]
