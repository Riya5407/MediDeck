from typing import Optional, List, Dict, Any
from psycopg import AsyncConnection
from app.config import settings
from app.pagination import paginate
from app.errors import NotFoundError


def _medicine_select_sql() -> str:
    """Base SQL expression that computes total_stock, status, and nearest_expiry in SQL."""
    return f"""
        SELECT 
            m.med_no,
            m.med_name,
            m.category,
            m.manufacturer,
            m.unit,
            ROUND(m.mrp::numeric, 2)::float AS mrp,
            COALESCE(stk.total_stock, 0)::int AS total_stock,
            CASE 
                WHEN COALESCE(stk.total_stock, 0) = 0 THEN 'out_of_stock'
                WHEN COALESCE(stk.total_stock, 0) <= {settings.LOW_STOCK_THRESHOLD} THEN 'low_stock'
                ELSE 'in_stock'
            END AS status,
            stk.nearest_expiry
        FROM medicine m
        LEFT JOIN (
            SELECT 
                b.med_no,
                SUM(CASE WHEN b.exp_date >= CURRENT_DATE THEN b.qty_in_stock ELSE 0 END) AS total_stock,
                MIN(CASE WHEN b.qty_in_stock > 0 THEN b.exp_date ELSE NULL END) AS nearest_expiry
            FROM medicine_batch b
            GROUP BY b.med_no
        ) stk ON m.med_no = stk.med_no
    """


async def get_medicines(
    conn: AsyncConnection,
    search: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    base_sql = _medicine_select_sql()
    where_clauses = []
    params: List[Any] = []

    if search:
        where_clauses.append("(m.med_name ILIKE %s OR m.manufacturer ILIKE %s)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern])

    if category:
        where_clauses.append("m.category = %s")
        params.append(category)

    inner_where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    wrapped_query = f"SELECT * FROM ({base_sql} {inner_where}) q"

    if status:
        wrapped_query += " WHERE status = %s"
        params.append(status)

    wrapped_query += " ORDER BY med_name ASC, med_no ASC"

    return await paginate(conn, wrapped_query, tuple(params), page=page, page_size=page_size)


async def get_medicine_by_id(conn: AsyncConnection, med_no: int) -> Dict[str, Any]:
    base_sql = _medicine_select_sql()
    query = f"{base_sql} WHERE m.med_no = %s"
    
    cur = await conn.execute(query, (med_no,))
    med = await cur.fetchone()
    if not med:
        raise NotFoundError(f"Medicine with med_no {med_no} not found")

    batch_query = f"""
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
        WHERE b.med_no = %s
        ORDER BY b.exp_date ASC, b.batch_no ASC
    """
    batch_cur = await conn.execute(batch_query, (med_no,))
    batches = await batch_cur.fetchall()

    med_dict = dict(med)
    med_dict["batches"] = batches
    return med_dict


async def create_medicine(conn: AsyncConnection, data: Dict[str, Any]) -> Dict[str, Any]:
    query = """
        INSERT INTO medicine (med_name, category, manufacturer, unit, mrp)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING med_no
    """
    cur = await conn.execute(
        query,
        (
            data["med_name"],
            data.get("category"),
            data.get("manufacturer"),
            data.get("unit"),
            data.get("mrp"),
        ),
    )
    row = await cur.fetchone()
    return await get_medicine_by_id(conn, row["med_no"])


async def update_medicine(conn: AsyncConnection, med_no: int, data: Dict[str, Any]) -> Dict[str, Any]:
    query = """
        UPDATE medicine
        SET med_name = %s,
            category = %s,
            manufacturer = %s,
            unit = %s,
            mrp = %s
        WHERE med_no = %s
        RETURNING med_no
    """
    cur = await conn.execute(
        query,
        (
            data["med_name"],
            data.get("category"),
            data.get("manufacturer"),
            data.get("unit"),
            data.get("mrp"),
            med_no,
        ),
    )
    row = await cur.fetchone()
    if not row:
        raise NotFoundError(f"Medicine with med_no {med_no} not found")
    return await get_medicine_by_id(conn, med_no)


async def delete_medicine(conn: AsyncConnection, med_no: int) -> None:
    cur = await conn.execute("DELETE FROM medicine WHERE med_no = %s RETURNING med_no", (med_no,))
    row = await cur.fetchone()
    if not row:
        raise NotFoundError(f"Medicine with med_no {med_no} not found")

