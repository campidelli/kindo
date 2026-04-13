import { apiFetch } from "./client";
import type { PaymentRequest, PaymentResponse } from "../types/api";

export async function createPayment(data: PaymentRequest): Promise<PaymentResponse> {
  return apiFetch<PaymentResponse>("/api/v1/payments", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getPayment(paymentId: string): Promise<PaymentResponse> {
  return apiFetch<PaymentResponse>(`/api/v1/payments/${paymentId}`);
}
