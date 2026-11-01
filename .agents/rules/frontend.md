# Frontend rules

- Structure: `src/api/` (typed client + one hooks file per resource), `src/components/` (shared UI), `src/pages/` (one folder per page), `src/styles/` (tokens).
- One fetch wrapper reads the API base URL from `VITE_API_URL`. It throws an error carrying the server's `detail` message; show that message to the user in a toast or inline.
- Data fetching with TanStack Query. Query keys are `[resource, params]`. After a mutation, invalidate the affected resources (e.g. creating a sale invalidates sales, medicines, batches, dashboard).
- Every data view has three states: loading (skeleton), empty (helpful message and action), and error (message plus retry).
- Search inputs debounce by 300 ms. Tables are server-paginated using the API's pagination.
- Forms: validate required fields before submit, show inline errors, disable the submit button while saving, and show server errors from the API.
- Destructive actions (delete, cancel bill) need a confirmation dialog. A 409 "in use" response is shown as a clear message, not a crash.
- Formatting: money as Indian rupees (`Intl.NumberFormat('en-IN')`, symbol and two decimals); dates displayed as `13 Oct 2026`.
- New Sale (POS): two-pane layout. Search medicines on the left (calls `/pos/medicines`), cart on the right. Pick the first batch (earliest expiry) by default. Editing a line's price is how discounts work; show the discount % next to it. Show the trigger's error message if the sale is rejected (e.g. insufficient stock). The "Billing as" employee dropdown is remembered in `localStorage`.
- Keyboard friendly: search autofocus, Enter adds the first result, visible focus rings.
- Layout is desktop first (min width 1024 px).
