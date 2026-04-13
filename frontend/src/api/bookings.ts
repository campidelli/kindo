import { apiFetch } from "./client";
import type { BookingResponse } from "../types/api";

export interface CreateBookingRequest {
  trip_id: string;
  parent_name: string;
  child_name: string;
}

export async function createBooking(data: CreateBookingRequest): Promise<BookingResponse> {
  return apiFetch<BookingResponse>("/api/v1/bookings", {
    method: "POST",
    body: JSON.stringify(data),
  });
}