from typing import Optional, List, Dict, Any
from psycopg import AsyncConnection
from app.pagination import paginate
from app.errors import NotFoundError


async def get_customers(
    conn: AsyncConnection,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    base_sql = "SELECT cust_no, cust_name, age, phone_no, address FROM customers"
    where_clauses = []
    params: List[Any] = []

    if search:
        where_clauses.append("(cust_name ILIKE %s OR phone_no ILIKE %s)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern])

    inner_where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"{base_sql} {inner_where} ORDER BY cust_name ASC, cust_no ASC"

    return await paginate(conn, query, tuple(params), page=page, page_size=page_size)


async def get_customer_by_id(conn: AsyncConnection, cust_no: int) -> Dict[str, Any]:
    sql = "SELECT cust_no, cust_name, age, phone_no, address FROM customers WHERE cust_no = %s"
    cur = await conn.execute(sql, (cust_no,))
    cust = await cur.fetchone()
    if not cust:
        raise NotFoundError(f"Customer {cust_no} not found")
    return dict(cust)


async def create_customer(conn: AsyncConnection, data: Dict[str, Any]) -> Dict[str, Any]:
    sql = """
        INSERT INTO customers (cust_name, age, phone_no, address)
        VALUES (%s, %s, %s, %s)
        RETURNING cust_no
    """
    cur = await conn.execute(
        sql,
        (
            data["cust_name"],
            data.get("age"),
            data.get("phone_no"),
            data.get("address"),
        ),
    )
    row = await cur.fetchone()
    return await get_customer_by_id(conn, row["cust_no"])


async def update_customer(conn: AsyncConnection, cust_no: int, data: Dict[str, Any]) -> Dict[str, Any]:
    sql = """
        UPDATE customers
        SET cust_name = %s,
            age = %s,
            phone_no = %s,
            address = %s
        WHERE cust_no = %s
        RETURNING cust_no
    """
    cur = await conn.execute(
        sql,
        (
            data["cust_name"],
            data.get("age"),
            data.get("phone_no"),
            data.get("address"),
            cust_no,
        ),
    )
    row = await cur.fetchone()
    if not row:
        raise NotFoundError(f"Customer {cust_no} not found")
    return await get_customer_by_id(conn, cust_no)


async def delete_customer(conn: AsyncConnection, cust_no: int) -> None:
    cur = await conn.execute("DELETE FROM customers WHERE cust_no = %s RETURNING cust_no", (cust_no,))
    row = await cur.fetchone()
    if not row:
        raise NotFoundError(f"Customer {cust_no} not found")


async def get_customer_history(conn: AsyncConnection, cust_no: int) -> Dict[str, Any]:
    # Ensure customer exists
    await get_customer_by_id(conn, cust_no)

    sales_sql = """
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
        WHERE s.cust_no = %s
        GROUP BY s.bill_no, s.sale_date, c.cust_name, e.emp_name, s.payment_mode, s.total_amt
        ORDER BY s.sale_date DESC, s.bill_no DESC
    """
    sales_cur = await conn.execute(sales_sql, (cust_no,))
    sales = await sales_cur.fetchall()

    pres_sql = """
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
        WHERE p.cust_no = %s
        GROUP BY p.pres_no, p.cust_no, c.cust_name, p.doc_name, p.pres_date, p.diagnosis
        ORDER BY p.pres_date DESC, p.pres_no DESC
    """
    pres_cur = await conn.execute(pres_sql, (cust_no,))
    prescriptions = await pres_cur.fetchall()

    return {
        "sales": [dict(s) for s in sales],
        "prescriptions": [dict(p) for p in prescriptions],
    }

