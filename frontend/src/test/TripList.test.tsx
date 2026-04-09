import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import TripList from "../components/TripList";
import * as tripsApi from "../api/trips";
import type { TripResponse } from "../types/api";

const sampleTrip: TripResponse = {
  id: "00000000-0000-0000-0000-000000000001",
  title: "Wellington Zoo Field Trip",
  description: "An exciting visit to Wellington Zoo.",
  date: "2026-06-15T00:00:00",
  location: "Wellington Zoo",
  cost: 35.0,
  school_id: "SCH-001",
  activity_id: "ACT-ZOO-2026",
  created_at: "2026-04-01T00:00:00",
};

describe("TripList", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("shows a spinner while loading", () => {
    vi.spyOn(tripsApi, "getTrips").mockReturnValue(new Promise(() => {}));

    render(<TripList onBook={() => {}} />);

    expect(document.querySelector(".animate-spin")).toBeInTheDocument();
  });

  it("shows an error message when the API fails", async () => {
    vi.spyOn(tripsApi, "getTrips").mockRejectedValue(new Error("Network error"));

    render(<TripList onBook={() => {}} />);

    await waitFor(() =>
      expect(screen.getByText("Network error")).toBeInTheDocument()
    );
  });

  it("shows an empty state when there are no trips", async () => {
    vi.spyOn(tripsApi, "getTrips").mockResolvedValue([]);

    render(<TripList onBook={() => {}} />);

    await waitFor(() =>
      expect(screen.getByText("No trips available.")).toBeInTheDocument()
    );
  });

  it("renders a trip card with title, location, and cost", async () => {
    vi.spyOn(tripsApi, "getTrips").mockResolvedValue([sampleTrip]);

    render(<TripList onBook={() => {}} />);

    await waitFor(() =>
      expect(screen.getByText("Wellington Zoo Field Trip")).toBeInTheDocument()
    );
    expect(screen.getAllByText(/Wellington Zoo/).length).toBeGreaterThan(0);
    expect(screen.getByText(/35\.00/)).toBeInTheDocument();
  });

  it("calls onBook with the trip when the Book button is clicked", async () => {
    vi.spyOn(tripsApi, "getTrips").mockResolvedValue([sampleTrip]);
    const onBook = vi.fn();

    render(<TripList onBook={onBook} />);

    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Book" })).toBeInTheDocument()
    );
    await userEvent.click(screen.getByRole("button", { name: "Book" }));

    expect(onBook).toHaveBeenCalledOnce();
    expect(onBook).toHaveBeenCalledWith(sampleTrip);
  });
});
