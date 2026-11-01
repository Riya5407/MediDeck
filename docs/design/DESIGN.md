# MediDesk Design Guide

Layout reference: MediDesk screenshots in `reference/` (ref-1 and ref-2 are the base). Other screenshots are secondary: ref-6 (PharmaCare Pro) for clean table styling, ref-4 (ShelfLifePro) for the expiry summary cards on the Batches page. Use only the features listed in `API_SPEC.md`; some screenshots show features we do not have (GST, images, barcodes, login, accounting).

## Palette (see tokens.css)
| Role | Token | Hex |
|---|---|---|
| Primary | primary | #075E5A |
| Soft surface | mint | #DDF2EB |
| Page background | bg | #FAFAF7 |
| Warning / highlight | amber | #F3B65B |
| Info / secondary | blue | #2F7DB5 |
| Danger | red | #C8453B |
| Body text | text | #17302F |

## Layout
- Fixed left sidebar (240 px): logo "MediDesk", nav items with icons, active item has primary-coloured background with white text.
- Top bar: global search, then an "employee" label on the right. No login.
- Content area: warm-white background, page title, then white cards (12 px radius, subtle shadow, 1 px border).
- Pages: Dashboard, Medicines, Batches and Expiry, New Sale, Sales History, Customers, Suppliers, Purchase Orders, Prescriptions, Employees, Reports.

## Components
- **KPI card:** mint icon tile, label (muted), large number.
- **Table:** white card, header row in bg colour with muted uppercase labels, row hover in mint at low opacity, 1 px row dividers, pagination at the bottom.
- **Primary button:** primary background, white text. **Secondary:** white with primary border and text. **Danger:** red text, red tint on hover.
- **Inputs:** 8 px radius, 1 px border, primary focus ring.

## Status badges (always text plus colour)
| Status | Background | Text |
|---|---|---|
| in_stock, Delivered | mint | primary |
| low_stock, expiring_soon, Pending | amber-tint | text (dark) |
| expired, out_of_stock | red-tint | red |
| Cancelled | border | text-muted |
| info | blue-tint | blue |

## Charts
Sales trend: primary line with mint area fill. Second series (if any): blue. Never use amber or red for chart series.

## Rules
- Amber never carries white text.
- Minimum body text 14 px, WCAG AA contrast.
- Desktop first.
