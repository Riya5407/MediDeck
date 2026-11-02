from typing import Optional, List, Dict, Any
from psycopg import AsyncConnection
from app.pagination import paginate
from app.errors import NotFoundError


async def get_employees(
    conn: AsyncConnection,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    base_sql = """
        SELECT emp_no, emp_name, emp_role, ROUND(salary::numeric, 2)::float AS salary, phone_no
        FROM employee
    """
    where_clauses = []
    params: List[Any] = []

    if search:
        where_clauses.append("(emp_name ILIKE %s OR emp_role ILIKE %s OR phone_no ILIKE %s)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])

    inner_where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"{base_sql} {inner_where} ORDER BY emp_name ASC, emp_no ASC"

    return await paginate(conn, query, tuple(params), page=page, page_size=page_size)


async def get_employee_by_id(conn: AsyncConnection, emp_no: int) -> Dict[str, Any]:
    sql = """
        SELECT emp_no, emp_name, emp_role, ROUND(salary::numeric, 2)::float AS salary, phone_no
        FROM employee
        WHERE emp_no = %s
    """
    cur = await conn.execute(sql, (emp_no,))
    emp = await cur.fetchone()
    if not emp:
        raise NotFoundError(f"Employee {emp_no} not found")
    return dict(emp)


async def create_employee(conn: AsyncConnection, data: Dict[str, Any]) -> Dict[str, Any]:
    sql = """
        INSERT INTO employee (emp_name, emp_role, salary, phone_no)
        VALUES (%s, %s, %s, %s)
        RETURNING emp_no
    """
    cur = await conn.execute(
        sql,
        (
            data["emp_name"],
            data.get("emp_role"),
            data.get("salary"),
            data.get("phone_no"),
        ),
    )
    row = await cur.fetchone()
    return await get_employee_by_id(conn, row["emp_no"])


async def update_employee(conn: AsyncConnection, emp_no: int, data: Dict[str, Any]) -> Dict[str, Any]:
    sql = """
        UPDATE employee
        SET emp_name = %s,
            emp_role = %s,
            salary = %s,
            phone_no = %s
        WHERE emp_no = %s
        RETURNING emp_no
    """
    cur = await conn.execute(
        sql,
        (
            data["emp_name"],
            data.get("emp_role"),
            data.get("salary"),
            data.get("phone_no"),
            emp_no,
        ),
    )
    row = await cur.fetchone()
    if not row:
        raise NotFoundError(f"Employee {emp_no} not found")
    return await get_employee_by_id(conn, emp_no)


async def delete_employee(conn: AsyncConnection, emp_no: int) -> None:
    cur = await conn.execute("DELETE FROM employee WHERE emp_no = %s RETURNING emp_no", (emp_no,))
    row = await cur.fetchone()
    if not row:
        raise NotFoundError(f"Employee {emp_no} not found")

