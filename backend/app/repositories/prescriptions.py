from datetime import date
from typing import Optional, List, Dict, Any
from psycopg import AsyncConnection
from app.pagination import paginate
from app.errors import NotFoundError


async def get_prescriptions(
    conn: AsyncConnection,
    cust_no: Optional[int] = None,
    search: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    base_sql = """
        SELECT 
            p.pres_no,
            p.cust_no,
            c.cust_name,
            p.doc_name,
            p.pres_date,
            p.diagnosis,
            COALESCE(count(pd.med_no), 0)::int AS item_count
        FROM prescription p
        LEFT JOIN customers c ON p.cust_no = c.cust_no
        LEFT JOIN prescription_details pd ON p.pres_no = pd.pres_no
    """
    where_clauses = []
    params: List[Any] = []

    if cust_no:
        where_clauses.append("p.cust_no = %s")
        params.append(cust_no)
    if from_date:
        where_clauses.append("p.pres_date >= %s")
        params.append(from_date)
    if to_date:
        where_clauses.append("p.pres_date <= %s")
        params.append(to_date)
    if search and search.strip():
        where_clauses.append("(p.doc_name ILIKE %s OR c.cust_name ILIKE %s)")
        pattern = f"%{search.strip()}%"
        params.extend([pattern, pattern])

    inner_where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"""
        SELECT * FROM (
            {base_sql}
            {inner_where}
            GROUP BY p.pres_no, p.cust_no, c.cust_name, p.doc_name, p.pres_date, p.diagnosis
        ) q
        ORDER BY pres_date DESC, pres_no DESC
    """
    return await paginate(conn, query, tuple(params), page=page, page_size=page_size)


async def get_prescription_by_id(conn: AsyncConnection, pres_no: int) -> Dict[str, Any]:
    sql = """
        SELECT 
            p.pres_no,
            p.cust_no,
            c.cust_name,
            p.doc_name,
            p.pres_date,
            p.diagnosis
        FROM prescription p
        LEFT JOIN customers c ON p.cust_no = c.cust_no
        WHERE p.pres_no = %s
    """
    cur = await conn.execute(sql, (pres_no,))
    pres = await cur.fetchone()
    if not pres:
        raise NotFoundError(f"Prescription #{pres_no} not found")

    items_sql = """
        SELECT 
            pd.med_no,
            m.med_name,
            pd.dosage,
            pd.duration
        FROM prescription_details pd
        JOIN medicine m ON pd.med_no = m.med_no
        WHERE pd.pres_no = %s
        ORDER BY pd.med_no ASC
    """
    items_cur = await conn.execute(items_sql, (pres_no,))
    items = await items_cur.fetchall()

    res = dict(pres)
    res["items"] = [dict(item) for item in items]
    return res


async def create_prescription(conn: AsyncConnection, data: Dict[str, Any]) -> Dict[str, Any]:
    # Single transaction insert
    cur = await conn.execute(
        """
        INSERT INTO prescription (cust_no, doc_name, pres_date, diagnosis)
        VALUES (%s, %s, %s, %s)
        RETURNING pres_no
        """,
        (data.get("cust_no"), data.get("doc_name"), data["pres_date"], data.get("diagnosis")),
    )
    pres_no = (await cur.fetchone())["pres_no"]

    for item in data.get("items") or []:
        await conn.execute(
            """
            INSERT INTO prescription_details (pres_no, med_no, dosage, duration)
            VALUES (%s, %s, %s, %s)
            """,
            (pres_no, item["med_no"], item.get("dosage"), item.get("duration")),
        )

    return await get_prescription_by_id(conn, pres_no)


async def update_prescription(conn: AsyncConnection, pres_no: int, data: Dict[str, Any]) -> Dict[str, Any]:
    # Ensure exists
    await get_prescription_by_id(conn, pres_no)

    await conn.execute(
        """
        UPDATE prescription
        SET cust_no = %s,
            doc_name = %s,
            pres_date = %s,
            diagnosis = %s
        WHERE pres_no = %s
        """,
        (data.get("cust_no"), data.get("doc_name"), data["pres_date"], data.get("diagnosis"), pres_no),
    )

    # Replace items list
    await conn.execute("DELETE FROM prescription_details WHERE pres_no = %s", (pres_no,))
    for item in data.get("items") or []:
        await conn.execute(
            """
            INSERT INTO prescription_details (pres_no, med_no, dosage, duration)
            VALUES (%s, %s, %s, %s)
            """,
            (pres_no, item["med_no"], item.get("dosage"), item.get("duration")),
        )

    return await get_prescription_by_id(conn, pres_no)


async def delete_prescription(conn: AsyncConnection, pres_no: int) -> None:
    await get_prescription_by_id(conn, pres_no)
    await conn.execute("DELETE FROM prescription_details WHERE pres_no = %s", (pres_no,))
    await conn.execute("DELETE FROM prescription WHERE pres_no = %s", (pres_no,))

