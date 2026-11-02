from datetime import date
from typing import Optional, List, Dict, Any
from psycopg import AsyncConnection
from app.pagination import paginate
from app.errors import NotFoundError
from fastapi import HTTPException


async def get_purchase_orders(
    conn: AsyncConnection,
    status: Optional[str] = None,
    sup_no: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    base_sql = """
        SELECT 
            po.pur_no,
            po.sup_no,
            s.sup_name,
            po.order_date,
            po.status,
            COALESCE(ROUND(SUM(pod.qty_ordered * pod.rate)::numeric, 2), 0)::float AS total
        FROM purchase_order po
        LEFT JOIN supplier s ON po.sup_no = s.sup_no
        LEFT JOIN purchase_order_details pod ON po.pur_no = pod.pur_no
    """
    where_clauses = []
    params: List[Any] = []

    if status:
        where_clauses.append("po.status = %s")
        params.append(status)
    if sup_no:
        where_clauses.append("po.sup_no = %s")
        params.append(sup_no)
    if from_date:
        where_clauses.append("po.order_date >= %s")
        params.append(from_date)
    if to_date:
        where_clauses.append("po.order_date <= %s")
        params.append(to_date)

    inner_where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"""
        SELECT * FROM (
            {base_sql}
            {inner_where}
            GROUP BY po.pur_no, po.sup_no, s.sup_name, po.order_date, po.status
        ) q
        ORDER BY order_date DESC, pur_no DESC
    """
    return await paginate(conn, query, tuple(params), page=page, page_size=page_size)


async def get_po_by_id(conn: AsyncConnection, pur_no: int) -> Dict[str, Any]:
    sql = """
        SELECT 
            po.pur_no,
            po.sup_no,
            s.sup_name,
            po.order_date,
            po.status,
            COALESCE(ROUND(SUM(pod.qty_ordered * pod.rate)::numeric, 2), 0)::float AS total
        FROM purchase_order po
        LEFT JOIN supplier s ON po.sup_no = s.sup_no
        LEFT JOIN purchase_order_details pod ON po.pur_no = pod.pur_no
        WHERE po.pur_no = %s
        GROUP BY po.pur_no, po.sup_no, s.sup_name, po.order_date, po.status
    """
    cur = await conn.execute(sql, (pur_no,))
    po = await cur.fetchone()
    if not po:
        raise NotFoundError(f"Purchase order #{pur_no} not found")

    lines_sql = """
        SELECT 
            pod.med_no,
            m.med_name,
            pod.qty_ordered,
            ROUND(pod.rate::numeric, 2)::float AS rate,
            ROUND((pod.qty_ordered * pod.rate)::numeric, 2)::float AS line_total
        FROM purchase_order_details pod
        JOIN medicine m ON pod.med_no = m.med_no
        WHERE pod.pur_no = %s
        ORDER BY pod.med_no ASC
    """
    lines_cur = await conn.execute(lines_sql, (pur_no,))
    lines = await lines_cur.fetchall()

    res = dict(po)
    res["lines"] = [dict(line) for line in lines]
    return res


async def create_po(conn: AsyncConnection, data: Dict[str, Any]) -> Dict[str, Any]:
    # Single transaction insert
    cur = await conn.execute(
        """
        INSERT INTO purchase_order (sup_no, order_date, status)
        VALUES (%s, CURRENT_DATE, 'Pending')
        RETURNING pur_no
        """,
        (data["sup_no"],),
    )
    pur_no = (await cur.fetchone())["pur_no"]

    for line in data["lines"]:
        await conn.execute(
            """
            INSERT INTO purchase_order_details (pur_no, med_no, qty_ordered, rate)
            VALUES (%s, %s, %s, %s)
            """,
            (pur_no, line["med_no"], line["qty_ordered"], line["rate"]),
        )

    return await get_po_by_id(conn, pur_no)


async def cancel_po(conn: AsyncConnection, pur_no: int) -> Dict[str, Any]:
    po = await get_po_by_id(conn, pur_no)
    if po["status"] != "Pending":
        raise HTTPException(status_code=400, detail="Only Pending purchase orders can be cancelled")

    await conn.execute("UPDATE purchase_order SET status = 'Cancelled' WHERE pur_no = %s", (pur_no,))
    return await get_po_by_id(conn, pur_no)


async def receive_po(conn: AsyncConnection, pur_no: int, data: Dict[str, Any]) -> Dict[str, Any]:
    po = await get_po_by_id(conn, pur_no)
    if po["status"] != "Pending":
        raise HTTPException(status_code=400, detail="Only Pending purchase orders can be received")

    po_lines = {l["med_no"]: l for l in po["lines"]}
    receive_lines = data["lines"]
    received_med_nos = [l["med_no"] for l in receive_lines]

    if set(received_med_nos) != set(po_lines.keys()) or len(received_med_nos) != len(po_lines):
        raise HTTPException(
            status_code=400,
            detail="Every med_no in the purchase order must appear exactly once in received lines",
        )

    # In one transaction: insert one medicine_batch per line, then set status to Delivered
    created_batches = []
    for line in receive_lines:
        med_no = line["med_no"]
        ordered_line = po_lines[med_no]
        qty = line.get("qty_received") if line.get("qty_received") is not None else ordered_line["qty_ordered"]
        pur_price = ordered_line["rate"]

        b_cur = await conn.execute(
            """
            INSERT INTO medicine_batch (med_no, mfg_date, exp_date, qty_in_stock, pur_price)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING batch_no
            """,
            (med_no, line.get("mfg_date"), line["exp_date"], qty, pur_price),
        )
        batch_no = (await b_cur.fetchone())["batch_no"]
        created_batches.append(batch_no)

    await conn.execute("UPDATE purchase_order SET status = 'Delivered' WHERE pur_no = %s", (pur_no,))
    updated_po = await get_po_by_id(conn, pur_no)
    updated_po["created_batches"] = created_batches
    return updated_po

