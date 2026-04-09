import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import PaymentReceipt from "../components/PaymentReceipt";
import type { TripResponse, PaymentDetailResponse } from "../types/api";

const sampleTrip: TripResponse = {
  id: "00000000-0000-0000-0000-000000000001",
  title: "Wellington Zoo Field Trip",
  description: "An exciting visit to Wellington Zoo.",
  date: "2026-06-15T00:00:00",
  location: "Wellington Zoo, 200 Daniell St, Newtown, Wellington",
  cost: 35.0,
  school_id: "SCH-001",
  activity_id: "ACT-ZOO-2026",
  created_at: "2026-04-01T00:00:00",
};

const samplePayment: PaymentDetailResponse = {
  id: "ab166a7a-7544-4cf7-81b9-c5e0a82551b1",
  trip_id: "00000000-0000-0000-0000-000000000001",
  student_name: "Jane Doe",
  parent_name: "John Doe",
  card_last_four: "1111",
  status: "success",
  transaction_id: "TX-123456-789",
  error_message: null,
  created_at: "2026-04-10T10:00:00",
};

describe("PaymentReceipt", () => {
  it("renders trip title and location", () => {
    render(<PaymentReceipt trip={sampleTrip} payment={samplePayment} onDone={vi.fn()} />);
    expect(screen.getByText("Wellington Zoo Field Trip")).toBeInTheDocument();
    expect(screen.getByText("Wellington Zoo, 200 Daniell St, Newtown, Wellington")).toBeInTheDocument();
  });

  it("renders student and parent names", () => {
    render(<PaymentReceipt trip={sampleTrip} payment={samplePayment} onDone={vi.fn()} />);
    expect(screen.getByText("Jane Doe")).toBeInTheDocument();
    expect(screen.getByText("John Doe")).toBeInTheDocument();
  });

  it("masks the card number showing only last 4 digits", () => {
    render(<PaymentReceipt trip={sampleTrip} payment={samplePayment} onDone={vi.fn()} />);
    expect(screen.getByText("**** **** **** 1111")).toBeInTheDocument();
  });

  it("shows the transaction ID", () => {
    render(<PaymentReceipt trip={sampleTrip} payment={samplePayment} onDone={vi.fn()} />);
    expect(screen.getByText("TXN: TX-123456-789")).toBeInTheDocument();
  });

  it("does not render transaction ID when null", () => {
    const payment = { ...samplePayment, transaction_id: null };
    render(<PaymentReceipt trip={sampleTrip} payment={payment} onDone={vi.fn()} />);
    expect(screen.queryByText(/TXN:/)).not.toBeInTheDocument();
  });

  it("renders the total amount", () => {
    render(<PaymentReceipt trip={sampleTrip} payment={samplePayment} onDone={vi.fn()} />);
    expect(screen.getByText("$35.00")).toBeInTheDocument();
  });

  it("calls onDone when Back to trips is clicked", async () => {
    const onDone = vi.fn();
    render(<PaymentReceipt trip={sampleTrip} payment={samplePayment} onDone={onDone} />);
    await userEvent.click(screen.getByRole("button", { name: /back to trips/i }));
    expect(onDone).toHaveBeenCalledOnce();
  });
});
