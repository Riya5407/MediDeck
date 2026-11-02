from typing import Optional, List, Dict, Any
from psycopg import AsyncConnection
from app.config import settings
from app.pagination import paginate
from app.errors import NotFoundError


def _batch_base_sql() -> str:
    """SQL selecting batch fields with derived status and days_to_expiry according to API_SPEC."""
    return f"""
        SELECT 
            b.batch_no,
            b.med_no,
            m.med_name,
            b.mfg_date,
            b.exp_date,
            b.qty_in_stock,
            ROUND(b.pur_price::numeric, 2)::float AS pur_price,
            CASE 
                WHEN b.exp_date < CURRENT_DATE THEN 'expired'
                WHEN b.qty_in_stock = 0 THEN 'out_of_stock'
                WHEN b.exp_date <= CURRENT_DATE + {settings.EXPIRY_WARNING_DAYS} THEN 'expiring_soon'
                WHEN b.qty_in_stock <= {settings.LOW_STOCK_THRESHOLD} THEN 'low_stock'
                ELSE 'in_stock'
            END AS status,
            (b.exp_date - CURRENT_DATE) AS days_to_expiry
        FROM medicine_batch b
        JOIN medicine m ON b.med_no = m.med_no
    """


async def get_batch_counts(conn: AsyncConnection) -> Dict[str, int]:
    """Calculate counts: total, expired, expiring_soon, valid (exp_date >= CURRENT_DATE)."""
    sql = f"""
        SELECT 
            COUNT(*)::int AS total,
            COUNT(CASE WHEN exp_date < CURRENT_DATE THEN 1 END)::int AS expired,
            COUNT(CASE WHEN exp_date >= CURRENT_DATE AND exp_date <= CURRENT_DATE + {settings.EXPIRY_WARNING_DAYS} THEN 1 END)::int AS expiring_soon,
            COUNT(CASE WHEN exp_date >= CURRENT_DATE THEN 1 END)::int AS valid
        FROM medicine_batch
    """
    cur = await conn.execute(sql)
    row = await cur.fetchone()
    return {
        "total": row["total"] or 0,
        "expired": row["expired"] or 0,
        "expiring_soon": row["expiring_soon"] or 0,
        "valid": row["valid"] or 0,
    }


async def get_batches(
    conn: AsyncConnection,
    search: Optional[str] = None,
    status: Optional[str] = None,
    med_no: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    base_sql = _batch_base_sql()
    where_clauses = []
    params: List[Any] = []

    if search:
        where_clauses.append("m.med_name ILIKE %s")
        params.append(f"%{search}%")

    if med_no is not None:
        where_clauses.append("b.med_no = %s")
        params.append(med_no)

    inner_where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    wrapped_query = f"SELECT * FROM ({base_sql} {inner_where}) q"

    if status:
        wrapped_query += " WHERE status = %s"
        params.append(status)

    wrapped_query += " ORDER BY exp_date ASC, batch_no ASC"

    paginated_result = await paginate(conn, wrapped_query, tuple(params), page=page, page_size=page_size)
    counts = await get_batch_counts(conn)
    paginated_result["counts"] = counts
    return paginated_result


async def get_batch_by_id(conn: AsyncConnection, batch_no: int) -> Dict[str, Any]:
    sql = f"{_batch_base_sql()} WHERE b.batch_no = %s"
    cur = await conn.execute(sql, (batch_no,))
    batch = await cur.fetchone()
    if not batch:
        raise NotFoundError(f"Batch {batch_no} not found")
    return dict(batch)


async def create_batch(conn: AsyncConnection, data: Dict[str, Any]) -> Dict[str, Any]:
    sql = """
        INSERT INTO medicine_batch (med_no, mfg_date, exp_date, qty_in_stock, pur_price)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING batch_no
    """
    cur = await conn.execute(
        sql,
        (
            data["med_no"],
            data.get("mfg_date"),
            data.get("exp_date"),
            data["qty_in_stock"],
            data.get("pur_price"),
        ),
    )
    row = await cur.fetchone()
    return await get_batch_by_id(conn, row["batch_no"])


async def update_batch(conn: AsyncConnection, batch_no: int, data: Dict[str, Any]) -> Dict[str, Any]:
    sql = """
        UPDATE medicine_batch
        SET med_no = %s,
            mfg_date = %s,
            exp_date = %s,
            qty_in_stock = %s,
            pur_price = %s
        WHERE batch_no = %s
        RETURNING batch_no
    """
    cur = await conn.execute(
        sql,
        (
            data["med_no"],
            data.get("mfg_date"),
            data.get("exp_date"),
            data["qty_in_stock"],
            data.get("pur_price"),
            batch_no,
        ),
    )
    row = await cur.fetchone()
    if not row:
        raise NotFoundError(f"Batch {batch_no} not found")
    return await get_batch_by_id(conn, batch_no)


async def delete_batch(conn: AsyncConnection, batch_no: int) -> None:
    cur = await conn.execute("DELETE FROM medicine_batch WHERE batch_no = %s RETURNING batch_no", (batch_no,))
    row = await cur.fetchone()
    if not row:
        raise NotFoundError(f"Batch {batch_no} not found")

