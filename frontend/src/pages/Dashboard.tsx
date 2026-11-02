import React, { useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  useDashboardSummary,
  useSalesTrend,
  useStockAlerts,
} from "../api/dashboard";
import { useSales } from "../api/sales";
import {
  Package,
  ShoppingCart,
  Receipt,
  AlertTriangle,
  Clock,
  XCircle,
  RefreshCw,
  TrendingUp,
} from "lucide-react";

// ── Status badge helper ──────────────────────────────────────────────────────
const STATUS_STYLES: Record<string, string> = {
  expired: "bg-[var(--color-red-tint)] text-red border-red/20",
  out_of_stock: "bg-[var(--color-red-tint)] text-red border-red/20",
  expiring_soon: "bg-amber/20 text-amber-800 border-amber/30",
  low_stock: "bg-amber/20 text-amber-800 border-amber/30",
  in_stock: "bg-mint text-primary border-primary/20",
};
const STATUS_LABEL: Record<string, string> = {
  expired: "Expired",
  out_of_stock: "Out of Stock",
  expiring_soon: "Expiring Soon",
  low_stock: "Low Stock",
  in_stock: "In Stock",
};

function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium border ${
        STATUS_STYLES[status] ?? "bg-bg border-border text-text-muted"
      }`}
    >
      {STATUS_LABEL[status] ?? status}
    </span>
  );
}

// ── KPI Card ─────────────────────────────────────────────────────────────────
interface KpiCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  accent?: "primary" | "amber" | "red" | "blue";
  loading?: boolean;
}

const ACCENT_BG: Record<string, string> = {
  primary: "bg-mint text-primary",
  amber: "bg-amber/20 text-amber-700",
  red: "bg-[var(--color-red-tint)] text-red",
  blue: "bg-blue/10 text-blue",
};

function KpiCard({ label, value, icon, accent = "primary", loading }: KpiCardProps) {
  return (
    <div className="rounded-[var(--radius-card)] border border-border bg-surface p-5 shadow-[var(--shadow-card)] flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${ACCENT_BG[accent]}`}>
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-xs font-medium text-text-muted uppercase tracking-wide">{label}</p>
        {loading ? (
          <div className="h-7 w-20 bg-bg animate-pulse rounded mt-1" />
        ) : (
          <p className="text-2xl font-bold text-text">{value}</p>
        )}
      </div>
    </div>
  );
}

// ── Main Dashboard ───────────────────────────────────────────────────────────
export default function Dashboard() {
  const [trendDays, setTrendDays] = useState(7);

  const { data: summary, isLoading: sumLoading, refetch: refetchSum } = useDashboardSummary();
  const { data: trend, isLoading: trendLoading } = useSalesTrend(trendDays);
  const { data: alerts, isLoading: alertsLoading } = useStockAlerts(8);
  const { data: recentSales, isLoading: salesLoading } = useSales({ page: 1, page_size: 5 });

  const fmtCurrency = (n: number) =>
    "₹" + n.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const fmtDate = (d: string) => new Date(d).toLocaleDateString("en-IN");
  const fmtShortDate = (d: string) =>
    new Date(d + "T00:00:00").toLocaleDateString("en-IN", { day: "numeric", month: "short" });

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text">Dashboard</h1>
          <p className="text-sm text-text-muted mt-1">
            {new Date().toLocaleDateString("en-IN", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
          </p>
        </div>
        <button
          onClick={() => refetchSum()}
          className="inline-flex items-center gap-2 px-3 py-1.5 border border-border rounded-[var(--radius-control)] text-sm text-text-muted hover:text-text hover:bg-bg transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Refresh
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <KpiCard
          label="Medicines"
          value={summary?.total_medicines ?? "—"}
          icon={<Package className="w-5 h-5" />}
          accent="primary"
          loading={sumLoading}
        />
        <KpiCard
          label="Today's Revenue"
          value={summary ? fmtCurrency(summary.todays_sales) : "—"}
          icon={<TrendingUp className="w-5 h-5" />}
          accent="primary"
          loading={sumLoading}
        />
        <KpiCard
          label="Today's Bills"
          value={summary?.todays_bills ?? "—"}
          icon={<Receipt className="w-5 h-5" />}
          accent="blue"
          loading={sumLoading}
        />
        <KpiCard
          label="Low Stock"
          value={summary?.low_stock_count ?? "—"}
          icon={<ShoppingCart className="w-5 h-5" />}
          accent="amber"
          loading={sumLoading}
        />
        <KpiCard
          label="Expiring Soon"
          value={summary?.expiring_soon_count ?? "—"}
          icon={<Clock className="w-5 h-5" />}
          accent="amber"
          loading={sumLoading}
        />
        <KpiCard
          label="Expired"
          value={summary?.expired_count ?? "—"}
          icon={<XCircle className="w-5 h-5" />}
          accent="red"
          loading={sumLoading}
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Sales Trend Chart */}
        <div className="xl:col-span-2 rounded-[var(--radius-card)] border border-border bg-surface p-5 shadow-[var(--shadow-card)]">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-text">Sales Trend</h2>
            <div className="flex gap-1">
              {[7, 14, 30].map((d) => (
                <button
                  key={d}
                  onClick={() => setTrendDays(d)}
                  className={`px-2.5 py-1 rounded-[var(--radius-control)] text-xs font-medium transition-colors ${
                    trendDays === d
                      ? "bg-primary text-white"
                      : "border border-border text-text-muted hover:text-text hover:bg-bg"
                  }`}
                >
                  {d}d
                </button>
              ))}
            </div>
          </div>

          {trendLoading ? (
            <div className="h-48 bg-bg animate-pulse rounded-[var(--radius-control)]" />
          ) : !trend?.length ? (
            <div className="h-48 flex items-center justify-center text-sm text-text-muted">No sales data.</div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={trend} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
                <defs>
                  <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#075E5A" stopOpacity={0.18} />
                    <stop offset="95%" stopColor="#075E5A" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis
                  dataKey="date"
                  tickFormatter={fmtShortDate}
                  tick={{ fontSize: 11, fill: "var(--color-text-muted)" }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tickFormatter={(v: any) => `₹${v}`}
                  tick={{ fontSize: 11, fill: "var(--color-text-muted)" }}
                  axisLine={false}
                  tickLine={false}
                  width={60}
                />
                <Tooltip
                  formatter={(value: any) => [fmtCurrency(Number(value) || 0), "Revenue"]}
                  labelFormatter={(label: any) => fmtShortDate(String(label))}
                  contentStyle={{
                    borderRadius: "var(--radius-card)",
                    border: "1px solid var(--color-border)",
                    fontSize: "12px",
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="total"
                  stroke="#075E5A"
                  strokeWidth={2}
                  fill="url(#trendGrad)"
                  dot={false}
                  activeDot={{ r: 4, fill: "#075E5A" }}
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Stock Alerts */}
        <div className="rounded-[var(--radius-card)] border border-border bg-surface shadow-[var(--shadow-card)] flex flex-col">
          <div className="px-5 py-4 border-b border-border flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <h2 className="text-base font-semibold text-text">Stock Alerts</h2>
          </div>
          {alertsLoading ? (
            <div className="p-4 space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-10 bg-bg animate-pulse rounded" />
              ))}
            </div>
          ) : !alerts?.length ? (
            <div className="flex-1 flex items-center justify-center p-6">
              <p className="text-sm text-text-muted text-center">
                ✅ All batches are in good shape.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-border overflow-y-auto max-h-72">
              {alerts.map((alert) => (
                <div key={alert.batch_no} className="px-4 py-3 flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-text truncate">{alert.med_name}</p>
                    <p className="text-xs text-text-muted">
                      Batch #{alert.batch_no} · Qty: {alert.qty_in_stock}
                      {alert.exp_date ? ` · Exp: ${fmtDate(alert.exp_date)}` : ""}
                    </p>
                  </div>
                  <StatusBadge status={alert.status} />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recent Sales */}
      <div className="rounded-[var(--radius-card)] border border-border bg-surface overflow-hidden shadow-[var(--shadow-card)]">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <h2 className="text-base font-semibold text-text">Recent Sales</h2>
          <a
            href="/sales"
            className="text-xs text-primary hover:underline font-medium"
          >
            View all →
          </a>
        </div>
        {salesLoading ? (
          <div className="p-4 space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-10 bg-bg animate-pulse rounded" />
            ))}
          </div>
        ) : !recentSales?.items?.length ? (
          <div className="p-8 text-center text-sm text-text-muted">No sales today yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-bg border-b border-border text-xs uppercase text-text-muted tracking-wider">
                <tr>
                  <th className="px-5 py-3 text-left">Bill #</th>
                  <th className="px-5 py-3 text-left">Date</th>
                  <th className="px-5 py-3 text-left">Customer</th>
                  <th className="px-5 py-3 text-left">Employee</th>
                  <th className="px-5 py-3 text-left">Payment</th>
                  <th className="px-5 py-3 text-right">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {recentSales.items.map((sale) => (
                  <tr key={sale.bill_no} className="hover:bg-mint/20 transition-colors">
                    <td className="px-5 py-3 font-mono text-text">#{sale.bill_no}</td>
                    <td className="px-5 py-3 text-text-muted">{fmtDate(sale.sale_date)}</td>
                    <td className="px-5 py-3 text-text">{sale.cust_name || <span className="italic text-text-muted">Walk-in</span>}</td>
                    <td className="px-5 py-3 text-text">{sale.emp_name || "—"}</td>
                    <td className="px-5 py-3">
                      <span className="inline-block px-2 py-0.5 text-xs rounded border border-border bg-bg text-text">
                        {sale.payment_mode}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-right font-semibold text-text">{fmtCurrency(sale.total_amt)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
