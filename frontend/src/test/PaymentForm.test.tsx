import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import PaymentForm from "../components/PaymentForm";
import type { TripResponse } from "../types/api";
import type { RegistrationData } from "../components/RegistrationForm";

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

const sampleRegistration: RegistrationData = {
  student_name: "Jane Doe",
  parent_name: "John Doe",
};

function renderForm(onConfirm = vi.fn(), onCancel = vi.fn()) {
  render(
    <PaymentForm
      trip={sampleTrip}
      registration={sampleRegistration}
      onConfirm={onConfirm}
      onCancel={onCancel}
    />
  );
}

describe("PaymentForm", () => {
  it("renders the order summary with trip and registration details", () => {
    renderForm();

    expect(screen.getByText("Wellington Zoo Field Trip")).toBeInTheDocument();
    expect(screen.getByText(/Jane Doe/)).toBeInTheDocument();
    expect(screen.getByText(/John Doe/)).toBeInTheDocument();
    expect(screen.getAllByText(/35\.00/).length).toBeGreaterThan(0);
  });

  it("shows validation errors when submitted empty", async () => {
    renderForm();

    // Clear the pre-filled cardholder name before submitting
    const cardholderInput = screen.getByLabelText(/cardholder name/i);
    await userEvent.clear(cardholderInput);

    await userEvent.click(screen.getByRole("button", { name: /pay/i }));

    expect(screen.getByText("Enter the cardholder name.")).toBeInTheDocument();
    expect(screen.getByText("Enter a valid card number.")).toBeInTheDocument();
    expect(screen.getByText("Enter a valid expiry date (MM/YY).")).toBeInTheDocument();
    expect(screen.getByText("Enter a valid 3-digit CVV.")).toBeInTheDocument();
  });

  it("formats the card number in groups of 4 as user types", async () => {
    renderForm();

    const input = screen.getByLabelText(/card number/i);
    await userEvent.type(input, "4111111111111111");

    expect(input).toHaveValue("4111 1111 1111 1111");
  });

  it("formats the expiry date with a slash after MM", async () => {
    renderForm();

    const input = screen.getByLabelText(/expiry date/i);
    await userEvent.type(input, "1230");

    expect(input).toHaveValue("12/30");
  });

  it("calls onConfirm with stripped card number when form is valid", async () => {
    const onConfirm = vi.fn();
    renderForm(onConfirm);

    const cardInput = screen.getByLabelText(/card number/i) as HTMLInputElement;
    const expiryInput = screen.getByLabelText(/expiry date/i) as HTMLInputElement;
    const cvvInput = screen.getByLabelText(/cvv/i) as HTMLInputElement;

    await userEvent.type(cardInput, "4111111111111111");
    await userEvent.type(expiryInput, "1228");
    await userEvent.type(cvvInput, "123");

    // Verify inputs are formatted correctly before submit
    expect(cardInput.value).toBe("4111 1111 1111 1111");
    expect(expiryInput.value).toBe("12/28");
    expect(cvvInput.value).toBe("123");

    await userEvent.click(screen.getByRole("button", { name: /pay/i }));

    expect(onConfirm).toHaveBeenCalledOnce();
    expect(onConfirm).toHaveBeenCalledWith({
      cardholder_name: "John Doe",
      card_number: "4111111111111111",
      expiry_date: "12/28",
      cvv: "123",
    });
  });

  it("calls onCancel when the Cancel button is clicked", async () => {
    const onCancel = vi.fn();
    renderForm(vi.fn(), onCancel);

    await userEvent.click(screen.getByRole("button", { name: /cancel/i }));

    expect(onCancel).toHaveBeenCalledOnce();
  });
});
