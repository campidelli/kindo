import { useRef, useState } from "react";
import TripList from "./components/TripList";
import RegistrationForm, { type RegistrationData } from "./components/RegistrationForm";
import PaymentForm, { type CardData } from "./components/PaymentForm";
import ProcessingModal from "./components/ProcessingModal";
import Toast from "./components/Toast";
import PaymentReceipt from "./components/PaymentReceipt";
import type { BookingReceiptResponse, BookingResponse, TripResponse } from "./types/api";
import { createBooking } from "./api/bookings";
import { createPayment, getPayment } from "./api/payments";
import { getBookingReceipt } from "./api/receipts";
import { ApiError } from "./api/client";

const POLL_INTERVAL_MS = 2_000;
const PAYMENT_TIMEOUT_MS = Number(import.meta.env.VITE_PAYMENT_TIMEOUT_MS || 30_000);

type Screen = "trips" | "registration" | "payment" | "success";

interface ToastState {
  message: string;
  type: "error" | "warning" | "success";
}

export default function App() {
  const [screen, setScreen] = useState<Screen>("trips");
  const [selectedTrip, setSelectedTrip] = useState<TripResponse | null>(null);
  const [currentBooking, setCurrentBooking] = useState<BookingResponse | null>(null);
  const [registration, setRegistration] = useState<RegistrationData | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [toast, setToast] = useState<ToastState | null>(null);
  const [receipt, setReceipt] = useState<BookingReceiptResponse | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  function navigate(next: Screen) {
    setToast(null);
    setScreen(next);
  }

  function stopPolling() {
    if (pollingRef.current) { clearInterval(pollingRef.current); pollingRef.current = null; }
    if (timeoutRef.current) { clearTimeout(timeoutRef.current); timeoutRef.current = null; }
  }

  function handleBook(trip: TripResponse) {
    setSelectedTrip(trip);
    setCurrentBooking(null);
    setRegistration(null);
    navigate("registration");
  }

  async function handleRegistrationContinue(data: RegistrationData) {
    try {
      const shouldReuseBooking =
        currentBooking !== null
        && selectedTrip !== null
        && currentBooking.trip_id === selectedTrip.id
        && currentBooking.parent_name === data.parent_name
        && currentBooking.child_name === data.student_name
        && currentBooking.status === "PENDING_PAYMENT";

      setRegistration(data);

      if (shouldReuseBooking) {
        navigate("payment");
        return;
      }

      const booking = await createBooking({
        trip_id: selectedTrip!.id,
        parent_name: data.parent_name,
        child_name: data.student_name,
      });

      setCurrentBooking(booking);
      navigate("payment");
    } catch (err) {
      setToast({
        message: err instanceof ApiError ? err.message : "Failed to create booking.",
        type: "error",
      });
    }
  }

  async function handlePaymentConfirm(cardData: CardData) {
    try {
      if (currentBooking === null) {
        throw new Error("Booking not found.");
      }

      const [expiryMonth, expiryYear] = cardData.expiry_date.split("/");
      const result = await createPayment({
        booking_id: currentBooking.id,
        card_number: cardData.card_number,
        expiry_month: Number(expiryMonth),
        expiry_year: Number(`20${expiryYear}`),
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
          const detail = await getPayment(result.id);
          const normalizedStatus = detail.status.toLowerCase();

          if (normalizedStatus === "success") {
            stopPolling();
            setIsProcessing(false);
            const nextReceipt = await getBookingReceipt(currentBooking.id);
            setReceipt(nextReceipt);
            setScreen("success");
            setToast({ message: "Payment confirmed!", type: "success" });
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
          onCancel={() => {
            setCurrentBooking(null);
            navigate("trips");
          }}
        />
        <Toast message={toast?.message ?? null} type={toast?.type ?? "error"} onDismiss={() => setToast(null)} />
      </>
    );
  }

  if (screen === "payment" && selectedTrip && registration && currentBooking) {
    return (
      <>
        <PaymentForm
          trip={selectedTrip}
          registration={registration}
          onConfirm={handlePaymentConfirm}
          onCancel={() => navigate("registration")}
        />
        <ProcessingModal isOpen={isProcessing} />
        <Toast message={toast?.message ?? null} type={toast?.type ?? "error"} onDismiss={() => setToast(null)} />
      </>
    );
  }

  if (screen === "success" && receipt) {
    return (
      <>
        <PaymentReceipt
          receipt={receipt}
          onDone={() => { navigate("trips"); setSelectedTrip(null); setCurrentBooking(null); setRegistration(null); setReceipt(null); }}
        />
        <Toast message={toast?.message ?? null} type={toast?.type ?? "success"} onDismiss={() => setToast(null)} />
      </>
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
