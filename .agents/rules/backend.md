# Backend rules

- One router and one repository module per resource (`routers/medicines.py`, `repositories/medicines.py`). Routers handle HTTP; repositories hold the SQL.
- Use one `psycopg_pool.ConnectionPool` created at startup from `DATABASE_URL`. Use `dict_row` so rows map to Pydantic models.
- Use a connection context manager that commits on success and rolls back on any exception. Multi-table writes use a single connection and transaction.
- Pagination helper: `page`, `page_size` (default 20, max 100), returns `{items, total, page, page_size}`. Run the count and the page query with the same filters.
- Error mapping in one place (`errors.py`) as a FastAPI exception handler, always returning `{"detail": "..."}`:
  - SQLSTATE P0001 (trigger RAISE EXCEPTION) -> 400, message unchanged
  - 23514 check violation -> 400, friendly message naming the field
  - 23503 foreign key violation on delete -> 409 "Cannot delete: this record is in use"
  - 23505 unique violation -> 409
  - no row -> 404
- Derived statuses (stock, expiry) are computed in SQL using `LOW_STOCK_THRESHOLD` and `EXPIRY_WARNING_DAYS` from config, exactly as defined in API_SPEC section 1. Do not store them.
- Search filters use `ILIKE` with parameters. Sort orders must be deterministic (add the primary key as a tiebreaker).
- Return dates as ISO strings, money as numbers rounded to 2 places.
- Tests run against a real PostgreSQL database named by `DATABASE_URL_TEST`, with each test wrapped in a transaction that is rolled back. Never run tests against the main database.
- Add CORS from `CORS_ORIGINS` in config.
