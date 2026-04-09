import { apiFetch } from "./client";
import type { PaymentCreatedResponse, PaymentDetailResponse, PaymentRequest } from "../types/api";

export async function createPayment(data: PaymentRequest): Promise<PaymentCreatedResponse> {
  return apiFetch<PaymentCreatedResponse>("/api/v1/payments", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getPayment(paymentId: string): Promise<PaymentDetailResponse> {
  return apiFetch<PaymentDetailResponse>(`/api/v1/payments/${paymentId}`);
}
