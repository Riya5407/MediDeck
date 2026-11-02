"""Reports repository — section 12 of API_SPEC.md."""
from datetime import date
from typing import Any, Dict, List
from psycopg import AsyncConnection


async def sales_by_date(
    conn: AsyncConnection,
    from_date: date,
    to_date: date,
) -> List[Dict[str, Any]]:
    cur = await conn.execute("""
        SELECT
            sale_date::text AS date,
            COUNT(*)::int   AS bills,
            ROUND(COALESCE(SUM(total_amt), 0)::numeric, 2)::float AS total
        FROM sale
        WHERE sale_date BETWEEN %s AND %s
        GROUP BY sale_date
        ORDER BY sale_date ASC
    """, (from_date, to_date))
    rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def top_medicines(
    conn: AsyncConnection,
    limit: int,
    from_date: date,
    to_date: date,
) -> List[Dict[str, Any]]:
    cur = await conn.execute("""
        SELECT
            m.med_no,
            m.med_name,
            SUM(sd.qty_sold)::int                                    AS qty_sold,
            ROUND(SUM(sd.qty_sold * sd.sale_price)::numeric, 2)::float AS revenue
        FROM sale_details sd
        JOIN medicine m ON m.med_no = sd.med_no
        JOIN sale s ON s.bill_no = sd.bill_no
        WHERE s.sale_date BETWEEN %s AND %s
        GROUP BY m.med_no, m.med_name
        ORDER BY revenue DESC
        LIMIT %s
    """, (from_date, to_date, limit))
    rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def expired_stock(conn: AsyncConnection) -> Dict[str, Any]:
    cur = await conn.execute("""
        SELECT
            b.batch_no,
            b.med_no,
            m.med_name,
            b.mfg_date,
            b.exp_date,
            b.qty_in_stock,
            b.pur_price,
            (b.exp_date - CURRENT_DATE)::int AS days_to_expiry,
            'expired'::text AS status,
            ROUND((b.qty_in_stock * COALESCE(b.pur_price, 0))::numeric, 2)::float AS value
        FROM medicine_batch b
        JOIN medicine m ON m.med_no = b.med_no
        WHERE b.exp_date < CURRENT_DATE AND b.qty_in_stock > 0
        ORDER BY b.exp_date ASC
    """)
    rows = await cur.fetchall()
    items = [dict(r) for r in rows]
    total_value = round(sum(r["value"] for r in items), 2)
    return {"items": items, "total_value": total_value}


async def purchases_by_supplier(
    conn: AsyncConnection,
    from_date: date,
    to_date: date,
) -> List[Dict[str, Any]]:
    cur = await conn.execute("""
        SELECT
            s.sup_no,
            s.sup_name,
            COUNT(po.pur_no)::int AS orders,
            ROUND(
                COALESCE(SUM(pod.qty_ordered * pod.rate), 0)::numeric, 2
            )::float AS total
        FROM supplier s
        JOIN purchase_order po ON po.sup_no = s.sup_no
        LEFT JOIN purchase_order_details pod ON pod.pur_no = po.pur_no
        WHERE po.status != 'Cancelled'
          AND po.order_date BETWEEN %s AND %s
        GROUP BY s.sup_no, s.sup_name
        ORDER BY total DESC
    """, (from_date, to_date))
    rows = await cur.fetchall()
    return [dict(r) for r in rows]

