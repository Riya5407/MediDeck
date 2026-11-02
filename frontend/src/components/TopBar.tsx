import { Search } from "lucide-react";

export default function TopBar() {
  return (
    <header
      className="sticky top-0 z-10 flex items-center justify-between border-b border-border bg-surface px-6 py-3"
    >
      {/* Global search */}
      <div className="relative w-80">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
        <input
          type="text"
          placeholder="Search…"
          className="w-full rounded-[var(--radius-control)] border border-border bg-bg py-2 pl-10 pr-3 text-sm placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>

      {/* Employee label */}
      <span className="text-sm text-text-muted">Staff</span>
    </header>
  );
}

