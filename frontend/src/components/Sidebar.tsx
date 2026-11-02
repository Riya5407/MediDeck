import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Pill,
  Package,
  ShoppingCart,
  ClipboardList,
  Users,
  Truck,
  FileBox,
  FileText,
  UserCog,
  BarChart3,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

interface NavItem {
  label: string;
  to: string;
  icon: LucideIcon;
}

const navItems: NavItem[] = [
  { label: "Dashboard", to: "/", icon: LayoutDashboard },
  { label: "Medicines", to: "/medicines", icon: Pill },
  { label: "Batches & Expiry", to: "/batches", icon: Package },
  { label: "New Sale", to: "/new-sale", icon: ShoppingCart },
  { label: "Sales History", to: "/sales", icon: ClipboardList },
  { label: "Customers", to: "/customers", icon: Users },
  { label: "Suppliers", to: "/suppliers", icon: Truck },
  { label: "Purchase Orders", to: "/purchase-orders", icon: FileBox },
  { label: "Prescriptions", to: "/prescriptions", icon: FileText },
  { label: "Employees", to: "/employees", icon: UserCog },
  { label: "Reports", to: "/reports", icon: BarChart3 },
];

export default function Sidebar() {
  return (
    <aside
      className="fixed top-0 left-0 h-screen flex flex-col bg-primary text-white"
      style={{ width: "var(--sidebar-width)" }}
    >
      {/* Logo */}
      <div className="flex items-center gap-1 px-5 py-4 border-b border-white/10">
        <img
          src="/logo.png"
          alt="MediDeck Logo"
          className="h-15 w-25 object-contain rounded-md shrink-0 shadow-sm"
        />
        <div className="text-xl font-bold tracking-wide select-none flex items-center">
          <span className="text-white">Medi</span>
          <span className="text-mint ml-0.5">Deck</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 pb-4">
        <ul className="space-y-1">
          {navItems.map(({ label, to, icon: Icon }) => (
            <li key={to}>
              <NavLink
                to={to}
                end={to === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${isActive
                    ? "bg-white/20 text-white"
                    : "text-white/70 hover:bg-white/10 hover:text-white"
                  }`
                }
              >
                <Icon className="h-5 w-5 shrink-0" />
                {label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}

