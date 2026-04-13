import { apiFetch } from "./client";
import type { BookingReceiptResponse } from "../types/api";

export async function getBookingReceipt(bookingId: string): Promise<BookingReceiptResponse> {
  return apiFetch<BookingReceiptResponse>(`/api/v1/receipts/bookings/${bookingId}`);
}