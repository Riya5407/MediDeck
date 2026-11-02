import { render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { describe, it, expect } from "vitest";
import App from "../src/App";

const queryClient = new QueryClient();

describe("App smoke test", () => {
  it("renders the sidebar with all 11 navigation items", () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/"]}>
          <App />
        </MemoryRouter>
      </QueryClientProvider>
    );

    const sidebar = screen.getByRole("complementary");
    const expectedNavItems = [
      "Dashboard",
      "Medicines",
      "Batches & Expiry",
      "New Sale",
      "Sales History",
      "Customers",
      "Suppliers",
      "Purchase Orders",
      "Prescriptions",
      "Employees",
      "Reports",
    ];

    expectedNavItems.forEach((item) => {
      expect(within(sidebar).getByText(item)).toBeInTheDocument();
    });

    expect(within(sidebar).getByAltText("MediDeck Logo")).toBeInTheDocument();
    expect(within(sidebar).getByText("Medi")).toBeInTheDocument();
    expect(within(sidebar).getByText("Deck")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Search…")).toBeInTheDocument();
  });
});
