# /verify

Run this before declaring any module done.

1. Backend: run the full pytest suite; fix failures.
2. Backend: start the API and call each endpoint of the current module against `docs/API_SPEC.md`; confirm paths, field names, and status codes match.
3. Frontend: run the TypeScript type-check and the production build; fix all errors and warnings.
4. Frontend: open the module's pages in the browser against the real API. Check loading, empty, and error states, and one error path (for example a trigger error or a 409).
5. Search the changed code for: raw hex colours, hardcoded data, SQL built with string formatting, and writes to `qty_in_stock` or `total_amt`. Remove any found.
6. Report results as a short checklist, and list any deviation from the spec.
