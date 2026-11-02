interface StatusBadgeProps {
  status: "in_stock" | "low_stock" | "out_of_stock" | "expired" | "expiring_soon" | "Delivered" | "Pending" | "Cancelled" | string;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  let bgClass = "bg-mint text-primary";
  let label = status.replace(/_/g, " ");

  if (status === "in_stock" || status === "Delivered") {
    bgClass = "bg-mint text-primary";
    label = status === "in_stock" ? "In Stock" : "Delivered";
  } else if (status === "low_stock" || status === "expiring_soon" || status === "Pending") {
    bgClass = "bg-[var(--color-amber-tint)] text-text";
    label =
      status === "low_stock"
        ? "Low Stock"
        : status === "expiring_soon"
        ? "Expiring Soon"
        : "Pending";
  } else if (status === "expired" || status === "out_of_stock") {
    bgClass = "bg-[var(--color-red-tint)] text-red";
    label = status === "expired" ? "Expired" : "Out of Stock";
  } else if (status === "Cancelled") {
    bgClass = "border border-border text-text-muted";
    label = "Cancelled";
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${bgClass}`}
    >
      {label}
    </span>
  );
}

