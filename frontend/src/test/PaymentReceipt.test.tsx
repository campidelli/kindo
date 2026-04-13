import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import PaymentReceipt from "../components/PaymentReceipt";
import type { BookingReceiptResponse } from "../types/api";

const sampleReceipt: BookingReceiptResponse = {
  booking: {
    id: "booking-1",
    trip_id: "00000000-0000-0000-0000-000000000001",
    status: "CONFIRMED",
    parent_name: "John Doe",
    child_name: "Jane Doe",
    created_at: "2026-04-10T10:00:00",
  },
  trip: {
    id: "00000000-0000-0000-0000-000000000001",
    title: "Wellington Zoo Field Trip",
    description: "An exciting visit to Wellington Zoo.",
    date: "2026-06-15T00:00:00",
    location: "Wellington Zoo, 200 Daniell St, Newtown, Wellington",
    cost: 35.0,
    school_id: "SCH-001",
    activity_id: "ACT-ZOO-2026",
  },
  payment: {
    id: "ab166a7a-7544-4cf7-81b9-c5e0a82551b1",
    booking_id: "booking-1",
    card_last_four: "1111",
    status: "SUCCESS",
    transaction_id: "TX-123456-789",
    error_message: null,
    created_at: "2026-04-10T10:00:00",
  },
};

describe("PaymentReceipt", () => {
  it("renders trip title and location", () => {
    render(<PaymentReceipt receipt={sampleReceipt} onDone={vi.fn()} />);
    expect(screen.getByText("Wellington Zoo Field Trip")).toBeInTheDocument();
    expect(screen.getByText("Wellington Zoo, 200 Daniell St, Newtown, Wellington")).toBeInTheDocument();
  });

  it("renders student and parent names", () => {
    render(<PaymentReceipt receipt={sampleReceipt} onDone={vi.fn()} />);
    expect(screen.getByText("Jane Doe")).toBeInTheDocument();
    expect(screen.getByText("John Doe")).toBeInTheDocument();
  });

  it("masks the card number showing only last 4 digits", () => {
    render(<PaymentReceipt receipt={sampleReceipt} onDone={vi.fn()} />);
    expect(screen.getByText("**** **** **** 1111")).toBeInTheDocument();
  });

  it("shows the transaction ID", () => {
    render(<PaymentReceipt receipt={sampleReceipt} onDone={vi.fn()} />);
    expect(screen.getByText("TXN: TX-123456-789")).toBeInTheDocument();
  });

  it("does not render transaction ID when null", () => {
    const receipt = {
      ...sampleReceipt,
      payment: { ...sampleReceipt.payment, transaction_id: null },
    };
    render(<PaymentReceipt receipt={receipt} onDone={vi.fn()} />);
    expect(screen.queryByText(/TXN:/)).not.toBeInTheDocument();
  });

  it("renders the total amount", () => {
    render(<PaymentReceipt receipt={sampleReceipt} onDone={vi.fn()} />);
    expect(screen.getByText("$35.00")).toBeInTheDocument();
  });

  it("calls onDone when Back to trips is clicked", async () => {
    const onDone = vi.fn();
    render(<PaymentReceipt receipt={sampleReceipt} onDone={onDone} />);
    await userEvent.click(screen.getByRole("button", { name: /back to trips/i }));
    expect(onDone).toHaveBeenCalledOnce();
  });
});
