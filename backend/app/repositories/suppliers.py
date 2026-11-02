from typing import Optional, List, Dict, Any
from psycopg import AsyncConnection
from app.pagination import paginate
from app.errors import NotFoundError


async def get_suppliers(
    conn: AsyncConnection,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    base_sql = """
        SELECT 
            s.sup_no, 
            s.sup_name, 
            s.address, 
            s.gst_no,
            COALESCE(
                ARRAY_AGG(sp.phone_no ORDER BY sp.phone_no) FILTER (WHERE sp.phone_no IS NOT NULL),
                '{}'
            ) AS phones
        FROM supplier s
        LEFT JOIN supplier_phone sp ON s.sup_no = sp.sup_no
    """
    where_clauses = []
    params: List[Any] = []

    if search:
        where_clauses.append("(s.sup_name ILIKE %s OR s.gst_no ILIKE %s)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern])

    inner_where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"""
        SELECT * FROM (
            {base_sql}
            {inner_where}
            GROUP BY s.sup_no, s.sup_name, s.address, s.gst_no
        ) q
        ORDER BY sup_name ASC, sup_no ASC
    """

    return await paginate(conn, query, tuple(params), page=page, page_size=page_size)


async def get_supplier_by_id(conn: AsyncConnection, sup_no: int) -> Dict[str, Any]:
    sql = """
        SELECT 
            s.sup_no, 
            s.sup_name, 
            s.address, 
            s.gst_no,
            COALESCE(
                ARRAY_AGG(sp.phone_no ORDER BY sp.phone_no) FILTER (WHERE sp.phone_no IS NOT NULL),
                '{}'
            ) AS phones
        FROM supplier s
        LEFT JOIN supplier_phone sp ON s.sup_no = sp.sup_no
        WHERE s.sup_no = %s
        GROUP BY s.sup_no, s.sup_name, s.address, s.gst_no
    """
    cur = await conn.execute(sql, (sup_no,))
    sup = await cur.fetchone()
    if not sup:
        raise NotFoundError(f"Supplier {sup_no} not found")
    return dict(sup)


async def create_supplier(conn: AsyncConnection, data: Dict[str, Any]) -> Dict[str, Any]:
    # Multi-table write inside current transaction
    sql = """
        INSERT INTO supplier (sup_name, address, gst_no)
        VALUES (%s, %s, %s)
        RETURNING sup_no
    """
    cur = await conn.execute(
        sql,
        (
            data["sup_name"],
            data.get("address"),
            data.get("gst_no"),
        ),
    )
    row = await cur.fetchone()
    sup_no = row["sup_no"]

    phones = data.get("phones") or []
    for phone in phones:
        if phone.strip():
            await conn.execute(
                "INSERT INTO supplier_phone (sup_no, phone_no) VALUES (%s, %s)",
                (sup_no, phone.strip()),
            )

    return await get_supplier_by_id(conn, sup_no)


async def update_supplier(conn: AsyncConnection, sup_no: int, data: Dict[str, Any]) -> Dict[str, Any]:
    # Multi-table write in single transaction
    sql = """
        UPDATE supplier
        SET sup_name = %s,
            address = %s,
            gst_no = %s
        WHERE sup_no = %s
        RETURNING sup_no
    """
    cur = await conn.execute(
        sql,
        (
            data["sup_name"],
            data.get("address"),
            data.get("gst_no"),
            sup_no,
        ),
    )
    row = await cur.fetchone()
    if not row:
        raise NotFoundError(f"Supplier {sup_no} not found")

    # Replace all phones
    await conn.execute("DELETE FROM supplier_phone WHERE sup_no = %s", (sup_no,))
    phones = data.get("phones") or []
    for phone in phones:
        if phone.strip():
            await conn.execute(
                "INSERT INTO supplier_phone (sup_no, phone_no) VALUES (%s, %s)",
                (sup_no, phone.strip()),
            )

    return await get_supplier_by_id(conn, sup_no)


async def delete_supplier(conn: AsyncConnection, sup_no: int) -> None:
    # Ensure supplier exists
    await get_supplier_by_id(conn, sup_no)
    # Delete phones first, then supplier, in single transaction
    await conn.execute("DELETE FROM supplier_phone WHERE sup_no = %s", (sup_no,))
    await conn.execute("DELETE FROM supplier WHERE sup_no = %s", (sup_no,))

