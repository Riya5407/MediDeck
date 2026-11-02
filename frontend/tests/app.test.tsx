import { render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { describe, it, expect, beforeEach } from "vitest";
import App from "../src/App";

describe("App tests with Authentication", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
  });

  it("renders the login screen when unauthenticated", () => {
    queryClient.setQueryData(["auth", "me"], null);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/login"]}>
          <App />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByPlaceholderText("Enter username")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Enter password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });

  it("renders the sidebar with all 11 navigation items when authenticated as admin", () => {
    queryClient.setQueryData(["auth", "me"], { username: "admin", role: "admin" });

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

  it("filters out restricted navigation items when authenticated as cashier", () => {
    queryClient.setQueryData(["auth", "me"], { username: "cashier", role: "cashier" });

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/"]}>
          <App />
        </MemoryRouter>
      </QueryClientProvider>
    );

    const sidebar = screen.getByRole("complementary");

    // Cashier allowed items
    expect(within(sidebar).getByText("Dashboard")).toBeInTheDocument();
    expect(within(sidebar).getByText("Medicines")).toBeInTheDocument();
    expect(within(sidebar).getByText("New Sale")).toBeInTheDocument();
    expect(within(sidebar).getByText("Sales History")).toBeInTheDocument();

    // Cashier restricted items should NOT be in the sidebar
    expect(within(sidebar).queryByText("Employees")).not.toBeInTheDocument();
    expect(within(sidebar).queryByText("Purchase Orders")).not.toBeInTheDocument();
    expect(within(sidebar).queryByText("Suppliers")).not.toBeInTheDocument();
    expect(within(sidebar).queryByText("Prescriptions")).not.toBeInTheDocument();
  });
});
