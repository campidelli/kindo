import { apiFetch } from "./client";
import type { TripResponse } from "../types/api";

export async function getTrips(): Promise<TripResponse[]> {
  return apiFetch<TripResponse[]>("/api/v1/trips");
}

export async function getFirstTrip(): Promise<TripResponse> {
  const trips = await getTrips();
  if (trips.length === 0) {
    throw new Error("No trips available.");
  }
  return trips[0];
}
