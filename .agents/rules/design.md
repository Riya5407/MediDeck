# Design rules

Follow `docs/design/DESIGN.md`. Layout reference is MediDesk (`docs/design/reference/`), recoloured with our palette. Colours come only from `docs/design/tokens.css` (copy it into `frontend/src/styles/tokens.css` and map it into the Tailwind theme).

- Sidebar (deep teal active item), top bar with global search, page title, KPI cards, white cards on a warm-white background.
- Amber is never used with white text. Amber surfaces always carry dark text.
- Status badges use the exact mapping in DESIGN.md. Never rely on colour alone: every badge has a text label.
- Keep body text at 14 px or larger and meet WCAG AA contrast.
