import { Search, LogOut, UserCircle } from "lucide-react";
import { useCurrentUser, useLogout } from "../api/auth";

export default function TopBar() {
  const { data: user } = useCurrentUser();
  const logoutMutation = useLogout();

  const handleLogout = () => {
    logoutMutation.mutate();
  };

  const roleBadgeStyle = (role?: string) => {
    switch (role) {
      case "admin":
        return "bg-primary text-white border-primary";
      case "pharmacist":
        return "bg-mint text-primary border-primary/30";
      case "cashier":
        return "bg-[var(--color-blue-tint)] text-blue border-blue/30";
      default:
        return "bg-bg text-text-muted border-border";
    }
  };

  return (
    <header className="sticky top-0 z-10 flex items-center justify-between border-b border-border bg-surface px-6 py-3">
      {/* Global search */}
      <div className="relative w-80">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
        <input
          type="text"
          placeholder="Search…"
          className="w-full rounded-[var(--radius-control)] border border-border bg-bg py-2 pl-10 pr-3 text-sm placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>

      {/* User profile & Logout */}
      <div className="flex items-center gap-4">
        {user && (
          <div className="flex items-center gap-2 text-sm">
            <UserCircle className="w-5 h-5 text-text-muted" />
            <span className="font-semibold text-text">{user.username}</span>
            <span
              className={`px-2 py-0.5 rounded-full text-xs font-semibold capitalize border ${roleBadgeStyle(
                user.role
              )}`}
            >
              {user.role}
            </span>
          </div>
        )}

        <button
          onClick={handleLogout}
          disabled={logoutMutation.isPending}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--radius-control)] text-xs font-medium text-text-muted hover:text-red hover:bg-bg border border-border transition-colors"
          title="Sign out of MediDeck"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Logout</span>
        </button>
      </div>
    </header>
  );
}
