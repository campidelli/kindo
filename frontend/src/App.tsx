import { useRef, useState } from "react";
import TripList from "./components/TripList";
import RegistrationForm, { type RegistrationData } from "./components/RegistrationForm";
import PaymentForm, { type CardData } from "./components/PaymentForm";
import ProcessingModal from "./components/ProcessingModal";
import Toast from "./components/Toast";
import type { TripResponse } from "./types/api";
import { createPayment, getPayment } from "./api/payments";
import { ApiError } from "./api/client";

const POLL_INTERVAL_MS = 2_000;
const PAYMENT_TIMEOUT_MS = Number(import.meta.env.VITE_PAYMENT_TIMEOUT_MS ?? 30_000);

type Screen = "trips" | "registration" | "payment" | "success";

interface ToastState {
  message: string;
  type: "error" | "warning";
}

export default function App() {
  const [screen, setScreen] = useState<Screen>("trips");
  const [selectedTrip, setSelectedTrip] = useState<TripResponse | null>(null);
  const [registration, setRegistration] = useState<RegistrationData | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [toast, setToast] = useState<ToastState | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  function stopPolling() {
    if (pollingRef.current) { clearInterval(pollingRef.current); pollingRef.current = null; }
    if (timeoutRef.current) { clearTimeout(timeoutRef.current); timeoutRef.current = null; }
  }

  function handleBook(trip: TripResponse) {
    setSelectedTrip(trip);
    setScreen("registration");
  }

  function handleRegistrationContinue(data: RegistrationData) {
    setRegistration(data);
    setScreen("payment");
  }

  async function handlePaymentConfirm(cardData: CardData) {
    try {
      const result = await createPayment({
        trip_id: selectedTrip!.id,
        student_name: registration!.student_name,
        parent_name: registration!.parent_name,
        card_number: cardData.card_number,
        expiry_date: cardData.expiry_date,
        cvv: cardData.cvv,
      });

      setIsProcessing(true);

      timeoutRef.current = setTimeout(() => {
        stopPolling();
        setIsProcessing(false);
        setToast({
          message: "Payment is taking too long. Please try again or contact support.",
          type: "warning",
        });
      }, PAYMENT_TIMEOUT_MS);

      pollingRef.current = setInterval(async () => {
        try {
          const detail = await getPayment(result.payment_id);
          const normalizedStatus = detail.status.toLowerCase();

          if (normalizedStatus === "success") {
            stopPolling();
            setIsProcessing(false);
            setScreen("success");
          } else if (normalizedStatus === "failed") {
            stopPolling();
            setIsProcessing(false);
            setToast({
              message: detail.error_message ?? "Payment failed. Please try again.",
              type: "error",
            });
          }
        } catch (err) {
          stopPolling();
          setIsProcessing(false);
          setToast({
            message: err instanceof ApiError ? err.message : "An unexpected error occurred.",
            type: "error",
          });
        }
      }, POLL_INTERVAL_MS);
    } catch (err) {
      setToast({
        message: err instanceof ApiError ? err.message : "Failed to submit payment.",
        type: "error",
      });
    }
  }

  if (screen === "registration" && selectedTrip) {
    return (
      <>
        <RegistrationForm
          trip={selectedTrip}
          onContinue={handleRegistrationContinue}
          onCancel={() => setScreen("trips")}
        />
        <Toast message={toast?.message ?? null} type={toast?.type ?? "error"} onDismiss={() => setToast(null)} />
      </>
    );
  }

  if (screen === "payment" && selectedTrip && registration) {
    return (
      <>
        <PaymentForm
          trip={selectedTrip}
          registration={registration}
          onConfirm={handlePaymentConfirm}
          onCancel={() => setScreen("registration")}
        />
        <ProcessingModal isOpen={isProcessing} />
        <Toast message={toast?.message ?? null} type={toast?.type ?? "error"} onDismiss={() => setToast(null)} />
      </>
    );
  }

  if (screen === "success" && selectedTrip && registration) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white border-b border-gray-200">
          <div className="mx-auto max-w-2xl px-4 py-4">
            <h1 className="text-xl font-bold text-green-700">Kindo</h1>
            <p className="text-xs text-gray-500">School Payments</p>
          </div>
        </header>
        <main className="mx-auto max-w-2xl px-4 py-12 text-center">
          <div className="inline-flex size-16 items-center justify-center rounded-full bg-green-100 mb-4">
            <svg className="size-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-1">Payment successful!</h2>
          <p className="text-sm text-gray-500 mb-1">{selectedTrip.title}</p>
          <p className="text-sm text-gray-500 mb-6">
            {registration.student_name} · Parent: {registration.parent_name}
          </p>
          <button
            onClick={() => { setScreen("trips"); setSelectedTrip(null); setRegistration(null); }}
            className="rounded-lg bg-green-600 px-6 py-2 text-sm font-medium text-white hover:bg-green-700 transition-colors"
          >
            Back to trips
          </button>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="mx-auto max-w-2xl px-4 py-4">
          <h1 className="text-xl font-bold text-green-700">Kindo</h1>
          <p className="text-xs text-gray-500">School Payments</p>
        </div>
      </header>

      <main className="mx-auto max-w-2xl px-4 py-6">
        <h2 className="mb-4 text-base font-semibold text-gray-700">
          Available Trips
        </h2>
        <TripList onBook={handleBook} />
      </main>
    </div>
  );
}
