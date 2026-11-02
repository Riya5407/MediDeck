from datetime import date
from typing import Optional, List, Dict, Any
from psycopg import AsyncConnection
from app.pagination import paginate
from app.errors import NotFoundError
from fastapi import HTTPException


async def search_pos_medicines(
    conn: AsyncConnection,
    q: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    where_q = ""
    params: List[Any] = []
    if q and q.strip():
        where_q = "WHERE m.med_name ILIKE %s"
        params.append(f"%{q.strip()}%")

    sql = f"""
        SELECT 
            m.med_no,
            m.med_name,
            m.unit,
            ROUND(m.mrp::numeric, 2)::float AS mrp,
            SUM(b.qty_in_stock)::int AS total_stock
        FROM medicine m
        JOIN medicine_batch b ON m.med_no = b.med_no
        {where_q}
        WHERE b.exp_date >= CURRENT_DATE AND b.qty_in_stock > 0
        GROUP BY m.med_no, m.med_name, m.unit, m.mrp
        HAVING SUM(b.qty_in_stock) > 0
        ORDER BY m.med_name ASC
        LIMIT %s
    """
    if where_q:
        # Re-construct properly with AND
        sql = f"""
            SELECT 
                m.med_no,
                m.med_name,
                m.unit,
                ROUND(m.mrp::numeric, 2)::float AS mrp,
                SUM(b.qty_in_stock)::int AS total_stock
            FROM medicine m
            JOIN medicine_batch b ON m.med_no = b.med_no
            WHERE m.med_name ILIKE %s AND b.exp_date >= CURRENT_DATE AND b.qty_in_stock > 0
            GROUP BY m.med_no, m.med_name, m.unit, m.mrp
            HAVING SUM(b.qty_in_stock) > 0
            ORDER BY m.med_name ASC
            LIMIT %s
        """
        params = [f"%{q.strip()}%", limit]
    else:
        params = [limit]

    cur = await conn.execute(sql, tuple(params))
    meds = await cur.fetchall()

    results = []
    for med in meds:
        med_dict = dict(med)
        b_cur = await conn.execute(
            """
            SELECT batch_no, exp_date, qty_in_stock
            FROM medicine_batch
            WHERE med_no = %s AND exp_date >= CURRENT_DATE AND qty_in_stock > 0
            ORDER BY exp_date ASC, batch_no ASC
            """,
            (med["med_no"],),
        )
        med_dict["batches"] = [dict(b) for b in await b_cur.fetchall()]
        results.append(med_dict)

    return results


async def get_sales(
    conn: AsyncConnection,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    base_sql = """
        SELECT 
            s.bill_no,
            s.sale_date,
            c.cust_name,
            e.emp_name,
            s.payment_mode,
            ROUND(s.total_amt::numeric, 2)::float AS total_amt,
            COALESCE(count(sd.med_no), 0)::int AS item_count
        FROM sale s
        LEFT JOIN customers c ON s.cust_no = c.cust_no
        LEFT JOIN employee e ON s.emp_no = e.emp_no
        LEFT JOIN sale_details sd ON s.bill_no = sd.bill_no
    """
    where_clauses = []
    params: List[Any] = []

    if from_date:
        where_clauses.append("s.sale_date >= %s")
        params.append(from_date)
    if to_date:
        where_clauses.append("s.sale_date <= %s")
        params.append(to_date)
    if search and search.strip():
        # search bill number or customer name
        if search.strip().isdigit():
            where_clauses.append("(s.bill_no = %s OR c.cust_name ILIKE %s)")
            params.extend([int(search.strip()), f"%{search.strip()}%"])
        else:
            where_clauses.append("c.cust_name ILIKE %s")
            params.append(f"%{search.strip()}%")

    inner_where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"""
        SELECT * FROM (
            {base_sql}
            {inner_where}
            GROUP BY s.bill_no, s.sale_date, c.cust_name, e.emp_name, s.payment_mode, s.total_amt
        ) q
        ORDER BY sale_date DESC, bill_no DESC
    """
    return await paginate(conn, query, tuple(params), page=page, page_size=page_size)


async def get_sale_by_id(conn: AsyncConnection, bill_no: int) -> Dict[str, Any]:
    sql = """
        SELECT 
            s.bill_no,
            s.sale_date,
            s.cust_no,
            c.cust_name,
            s.emp_no,
            e.emp_name,
            s.payment_mode,
            ROUND(s.total_amt::numeric, 2)::float AS total_amt
        FROM sale s
        LEFT JOIN customers c ON s.cust_no = c.cust_no
        LEFT JOIN employee e ON s.emp_no = e.emp_no
        WHERE s.bill_no = %s
    """
    cur = await conn.execute(sql, (bill_no,))
    sale = await cur.fetchone()
    if not sale:
        raise NotFoundError(f"Sale bill #{bill_no} not found")

    lines_sql = """
        SELECT 
            sd.med_no,
            m.med_name,
            sd.batch_no,
            sd.qty_sold,
            ROUND(sd.sale_price::numeric, 2)::float AS sale_price,
            ROUND(m.mrp::numeric, 2)::float AS mrp,
            ROUND(
                CASE 
                    WHEN COALESCE(m.mrp, 0) > 0 THEN ((m.mrp - sd.sale_price) / m.mrp * 100)::numeric 
                    ELSE 0 
                END, 2
            )::float AS discount_pct,
            ROUND((sd.qty_sold * sd.sale_price)::numeric, 2)::float AS line_total
        FROM sale_details sd
        JOIN medicine m ON sd.med_no = m.med_no
        WHERE sd.bill_no = %s
        ORDER BY sd.med_no ASC, sd.batch_no ASC
    """
    lines_cur = await conn.execute(lines_sql, (bill_no,))
    lines = await lines_cur.fetchall()

    res = dict(sale)
    res["lines"] = [dict(line) for line in lines]
    return res


async def create_sale(conn: AsyncConnection, data: Dict[str, Any]) -> Dict[str, Any]:
    lines = data["lines"]
    batch_nos = [line["batch_no"] for line in lines]
    if len(batch_nos) != len(set(batch_nos)):
        raise HTTPException(status_code=400, detail="Duplicate batch_no in same bill is not allowed")

    # Insert into sale header in single transaction
    cur = await conn.execute(
        """
        INSERT INTO sale (cust_no, emp_no, sale_date, payment_mode)
        VALUES (%s, %s, CURRENT_DATE, %s)
        RETURNING bill_no
        """,
        (data.get("cust_no"), data["emp_no"], data["payment_mode"]),
    )
    row = await cur.fetchone()
    bill_no = row["bill_no"]

    # Insert lines; database triggers compute MRP default if sale_price None, decrement stock, and update total_amt
    for line in lines:
        if line.get("sale_price") is not None:
            await conn.execute(
                """
                INSERT INTO sale_details (bill_no, med_no, batch_no, qty_sold, sale_price)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (bill_no, line["med_no"], line["batch_no"], line["qty_sold"], line["sale_price"]),
            )
        else:
            await conn.execute(
                """
                INSERT INTO sale_details (bill_no, med_no, batch_no, qty_sold)
                VALUES (%s, %s, %s, %s)
                """,
                (bill_no, line["med_no"], line["batch_no"], line["qty_sold"]),
            )

    return await get_sale_by_id(conn, bill_no)


async def cancel_sale(conn: AsyncConnection, bill_no: int) -> None:
    # Ensure bill exists
    await get_sale_by_id(conn, bill_no)
    # Delete lines first (triggers restore stock), then header, in one transaction
    await conn.execute("DELETE FROM sale_details WHERE bill_no = %s", (bill_no,))
    await conn.execute("DELETE FROM sale WHERE bill_no = %s", (bill_no,))

