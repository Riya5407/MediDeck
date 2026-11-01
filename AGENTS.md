# MediDesk: Pharmacy Management System

Internal tool for the staff of ONE pharmacy (pharmacist, cashier, manager). It is NOT customer-facing: customers are only records attached to bills and prescriptions. Built as a DBMS lab project, so the SQL should be readable and explainable.

## Sources of truth: read before writing any code
- `docs/API_SPEC.md`: the API contract. Never change it. If it looks wrong or incomplete, stop and ask the user.
- `docs/db/`: the database. Final schema = `pharmacy_schema.sql`, then `01_schema_fixes.sql`, then `02_triggers.sql`.
- `docs/design/DESIGN.md`, `docs/design/tokens.css`, `docs/design/reference/`: the visual design (MediDesk layout, custom palette).
- `docs/BUILD_PLAN.md`: module order. Work on ONE module per session.

## Stack
- Backend: Python 3.12, FastAPI, psycopg 3 with psycopg_pool, Pydantic v2, pytest.
- Frontend: Vite, React, TypeScript, Tailwind CSS, React Router, TanStack Query, Recharts.
- Database: PostgreSQL (already exists and is migrated).

## Hard rules
1. Raw SQL only, no ORM. Always parameterised queries; never build SQL with f-strings or concatenation.
2. No hardcoded data or config. No mock data in the UI: every number and row comes from the API. Config comes from `.env` (commit `.env.example`).
3. Do not change the database schema: no new tables, columns, constraints, or triggers. If you think one is needed, stop and ask.
4. Stock and bill totals are maintained by database triggers. Never write `medicine_batch.qty_in_stock` or `sale.total_amt` from application code.
5. No login or authentication.
6. Any write touching more than one table runs in a single transaction.
7. Pass database error messages (trigger errors especially) to the UI as described in API_SPEC section 1.
8. The frontend talks only to the API. API types live in `frontend/src/api/types.ts` and mirror the spec exactly.
9. Use design tokens only. No raw hex colours inside components.
10. Stay inside the current module. Do not refactor or restyle other modules.

## Repo layout
```
backend/   app/{main.py, config.py, db.py, errors.py, routers/, repositories/, schemas/}  tests/
frontend/  src/{api/, components/, pages/, styles/}
docs/      API_SPEC.md  db/  design/  BUILD_PLAN.md
.agents/   rules/  workflows/
```

## Definition of done for every module
- Endpoints match the spec exactly (paths, fields, status codes).
- pytest covers each endpoint, including at least one error case.
- The page works against the real API with loading, empty, and error states.
- `/verify` passes.
- Final message lists what was built and any place you deviated from the spec (ideally none).

## Commands
The foundation session records the exact run, test, and build commands here once they exist.
