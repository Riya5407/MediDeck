"""Generic server-side pagination helper."""
from typing import Any


async def paginate(
    conn,
    base_query: str,
    params: tuple = (),
    *,
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100,
) -> dict[str, Any]:
    """Run a paginated query and return {items, total, page, page_size}.

    ``base_query`` must NOT include LIMIT/OFFSET – this function appends them.
    The same ``params`` are used for both the count and the data query.
    """
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20
    page_size = min(page_size, max_page_size)
    offset = (page - 1) * page_size

    # total count
    count_sql = f"SELECT count(*) AS cnt FROM ({base_query}) _sub"
    async with conn.cursor() as cur:
        await cur.execute(count_sql, params)
        row = await cur.fetchone()
        total = row["cnt"]

    # page slice
    data_sql = f"{base_query} LIMIT %s OFFSET %s"
    async with conn.cursor() as cur:
        await cur.execute(data_sql, (*params, page_size, offset))
        items = await cur.fetchall()

    return {"items": items, "total": total, "page": page, "page_size": page_size}
