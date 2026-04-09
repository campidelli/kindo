import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import Toast from "../components/Toast";

describe("Toast", () => {
  it("renders nothing when message is null", () => {
    const { container } = render(
      <Toast message={null} type="error" onDismiss={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });

  it("renders the message text", () => {
    render(<Toast message="Something went wrong" type="error" onDismiss={vi.fn()} />);
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });

  it("applies error styles", () => {
    render(<Toast message="Error" type="error" onDismiss={vi.fn()} />);
    expect(screen.getByText("Error").closest("div")).toHaveClass("border-red-300");
  });

  it("applies warning styles", () => {
    render(<Toast message="Warning" type="warning" onDismiss={vi.fn()} />);
    expect(screen.getByText("Warning").closest("div")).toHaveClass("border-amber-300");
  });

  it("applies success styles", () => {
    render(<Toast message="Done!" type="success" onDismiss={vi.fn()} />);
    expect(screen.getByText("Done!").closest("div")).toHaveClass("border-green-300");
  });

  it("calls onDismiss when dismiss button is clicked", async () => {
    const onDismiss = vi.fn();
    render(<Toast message="Hello" type="success" onDismiss={onDismiss} />);
    await userEvent.click(screen.getByRole("button", { name: /dismiss/i }));
    expect(onDismiss).toHaveBeenCalledOnce();
  });
});
