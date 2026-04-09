import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import RegistrationForm from "../components/RegistrationForm";
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

describe("RegistrationForm", () => {
  it("renders the trip summary", () => {
    render(
      <RegistrationForm trip={sampleTrip} onContinue={() => {}} onCancel={() => {}} />
    );

    expect(screen.getByText("Wellington Zoo Field Trip")).toBeInTheDocument();
    expect(screen.getByText(/\$35\.00/)).toBeInTheDocument();
  });

  it("shows validation errors when submitted empty", async () => {
    render(
      <RegistrationForm trip={sampleTrip} onContinue={() => {}} onCancel={() => {}} />
    );

    await userEvent.click(screen.getByRole("button", { name: /continue/i }));

    expect(screen.getByText("Student name is required.")).toBeInTheDocument();
    expect(screen.getByText("Parent name is required.")).toBeInTheDocument();
  });

  it("calls onContinue with trimmed values when form is valid", async () => {
    const onContinue = vi.fn();

    render(
      <RegistrationForm trip={sampleTrip} onContinue={onContinue} onCancel={() => {}} />
    );

    await userEvent.type(screen.getByLabelText(/student name/i), "  Jane Doe  ");
    await userEvent.type(screen.getByLabelText(/parent/i), "  John Doe  ");
    await userEvent.click(screen.getByRole("button", { name: /continue/i }));

    expect(onContinue).toHaveBeenCalledOnce();
    expect(onContinue).toHaveBeenCalledWith({
      student_name: "Jane Doe",
      parent_name: "John Doe",
    });
  });

  it("does not call onContinue when only one field is filled", async () => {
    const onContinue = vi.fn();

    render(
      <RegistrationForm trip={sampleTrip} onContinue={onContinue} onCancel={() => {}} />
    );

    await userEvent.type(screen.getByLabelText(/student name/i), "Jane Doe");
    await userEvent.click(screen.getByRole("button", { name: /continue/i }));

    expect(onContinue).not.toHaveBeenCalled();
    expect(screen.getByText("Parent name is required.")).toBeInTheDocument();
  });

  it("calls onCancel when the Cancel button is clicked", async () => {
    const onCancel = vi.fn();

    render(
      <RegistrationForm trip={sampleTrip} onContinue={() => {}} onCancel={onCancel} />
    );

    await userEvent.click(screen.getByRole("button", { name: /cancel/i }));

    expect(onCancel).toHaveBeenCalledOnce();
  });
});
