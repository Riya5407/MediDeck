# Build plan

One agent, one module per session. Start each session in a fresh conversation. Finish with `/verify`, review, commit, then move on.

## Order
| # | Session | API spec sections | Pages |
|---|---|---|---|
| 0 | Foundation | 1, 2 (health, meta, categories) | App shell, router, tokens, empty nav pages |
| 1 | Medicines | 4 | Medicines list, add/edit form |
| 2 | Batches | 5 | Batches and expiry page |
| 3 | Employees | 11 | Employees list and form |
| 4 | Customers | 7 | Customers list, form, history |
| 5 | Suppliers | 8 | Suppliers list, form |
| 6 | Sales and POS | 6 | New Sale, Sales History, bill view |
| 7 | Purchase Orders | 9 | List, create, view, receive |
| 8 | Prescriptions | 10 | List, create/edit |
| 9 | Dashboard | 3 | Dashboard |
| 10 | Reports | 12 | Reports with CSV export |
| 11 | Polish | all | Consistency pass, empty states, edge cases |

Employees come before Sales because every bill needs an employee.

## Before session 6
Make sure the database has sample data (medicines, batches with stock and valid expiry dates, customers, employees). The POS and dashboard can only be checked with real rows.

## Session 0 prompt (foundation)
> Read AGENTS.md and all files in .agents/rules/. Task: create the project foundation only.
> Backend: FastAPI app with config from .env (.env.example), psycopg connection pool, transaction helper, error handler mapping PostgreSQL errors as in the backend rules, pagination helper, and the endpoints GET /api/health, GET /api/meta, GET /api/categories from docs/API_SPEC.md, with pytest tests.
> Frontend: Vite + React + TypeScript + Tailwind, tokens from docs/design/tokens.css, the app shell (sidebar, top bar), React Router with a page for every nav item showing a simple empty state, the API client, and TanStack Query provider.
> Then update the Commands section of AGENTS.md with the exact run, test, and build commands. Plan first, then implement, then run /verify. Do not build any other module.

## Template for sessions 1 to 11
> Read AGENTS.md and the rules in .agents/rules/. Today's module: **[NAME]**. Implement section(s) **[N]** of docs/API_SPEC.md and the pages listed in docs/BUILD_PLAN.md for this session, following docs/design/DESIGN.md and the reference screenshots. Show me your plan first. Then implement the backend and frontend together, write the tests, and run /verify. Do not touch other modules or change the spec. If the spec seems wrong, stop and ask me.
