import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";
import Dashboard from "./pages/Dashboard";
import Medicines from "./pages/Medicines";
import Batches from "./pages/Batches";
import NewSale from "./pages/NewSale";
import SalesHistory from "./pages/SalesHistory";
import Customers from "./pages/Customers";
import Suppliers from "./pages/Suppliers";
import PurchaseOrders from "./pages/PurchaseOrders";
import Prescriptions from "./pages/Prescriptions";
import Employees from "./pages/Employees";
import Reports from "./pages/Reports";

export default function App() {
  return (
    <div className="flex min-h-screen bg-bg text-text">
      <Sidebar />
      <div className="flex flex-1 flex-col" style={{ marginLeft: "var(--sidebar-width)" }}>
        <TopBar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/medicines" element={<Medicines />} />
            <Route path="/batches" element={<Batches />} />
            <Route path="/new-sale" element={<NewSale />} />
            <Route path="/sales" element={<SalesHistory />} />
            <Route path="/customers" element={<Customers />} />
            <Route path="/suppliers" element={<Suppliers />} />
            <Route path="/purchase-orders" element={<PurchaseOrders />} />
            <Route path="/prescriptions" element={<Prescriptions />} />
            <Route path="/employees" element={<Employees />} />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

