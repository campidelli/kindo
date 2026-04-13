import { apiFetch } from "./client";
import type { PaymentRequest, PaymentResponse } from "../types/api";

export async function createPayment(data: PaymentRequest, signal?: AbortSignal): Promise<PaymentResponse> {
  return apiFetch<PaymentResponse>("/api/v1/payments", {
    method: "POST",
    body: JSON.stringify(data),
    signal,
  });
}

export async function getPayment(paymentId: string, signal?: AbortSignal): Promise<PaymentResponse> {
  return apiFetch<PaymentResponse>(`/api/v1/payments/${paymentId}`, { signal });
}
