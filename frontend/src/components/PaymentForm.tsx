import { useRef, useState } from "react";
import { number as validateCardNumber, expirationDate as validateExpiry, cvv as validateCVV } from "card-validator";
import type { TripResponse } from "../types/api";
import type { RegistrationData } from "./RegistrationForm";

export interface CardData {
  cardholder_name: string;
  card_number: string;
  expiry_date: string;
  cvv: string;
}

interface Props {
  trip: TripResponse;
  registration: RegistrationData;
  onConfirm: (data: CardData) => void;
  onCancel: () => void;
}

type CardErrors = Partial<CardData>;

function formatCardNumber(value: string): string {
  return value
    .replace(/\D/g, "")
    .slice(0, 16)
    .replace(/(.{4})/g, "$1 ")
    .trim();
}

function formatExpiry(value: string): string {
  const digits = value.replace(/\D/g, "").slice(0, 4);
  if (digits.length >= 3) return `${digits.slice(0, 2)}/${digits.slice(2)}`;
  return digits;
}

export default function PaymentForm({ trip, registration, onConfirm, onCancel }: Props) {
  const [cardholderName, setCardholderName] = useState(registration.parent_name);
  const [cardNumber, setCardNumber] = useState("");
  const [expiryDate, setExpiryDate] = useState("");
  const [cvv, setCvv] = useState("");
  const [errors, setErrors] = useState<CardErrors>({});

  const cardNumberRef = useRef<HTMLInputElement>(null);
  const expiryRef = useRef<HTMLInputElement>(null);
  const cvvRef = useRef<HTMLInputElement>(null);

  function validate(): boolean {
    const next: CardErrors = {};

    if (!cardholderName.trim()) {
      next.cardholder_name = "Enter the cardholder name.";
    }

    const rawCard = cardNumber.replace(/\s/g, "");
    
    // Validate card number
    const cardValidation = validateCardNumber(rawCard);
    if (!cardValidation.isValid) {
      next.card_number = "Enter a valid card number.";
    }
    
    // Validate expiry date
    if (!expiryDate) {
      next.expiry_date = "Enter a valid expiry date (MM/YY).";
    } else {
      const expiryValidation = validateExpiry(expiryDate);
      if (!expiryValidation.isValid) {
        next.expiry_date = "Enter a valid expiry date (MM/YY).";
      }
    }
    
    // Validate CVV
    const cvvValidation = validateCVV(cvv);
    if (!cvvValidation.isValid) {
      next.cvv = "Enter a valid 3-digit CVV.";
    }
    
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (validate()) {
      onConfirm({
        cardholder_name: cardholderName.trim(),
        card_number: cardNumber.replace(/\s/g, ""),
        expiry_date: expiryDate,
        cvv,
      });
    }
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
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          {/* Order summary */}
          <div className="mb-6 rounded-lg bg-green-50 border border-green-200 p-4">
            <p className="text-xs font-medium text-green-700 uppercase tracking-wide mb-1">
              Order summary
            </p>
            <p className="font-semibold text-gray-900">{trip.title}</p>
            <p className="text-sm text-gray-500 mt-0.5">
              {registration.student_name} · Parent: {registration.parent_name}
            </p>
            <p className="text-sm font-semibold text-gray-800 mt-2">
              Total: ${trip.cost.toFixed(2)}
            </p>
          </div>

          <h2 className="text-base font-semibold text-gray-900 mb-4">
            Payment Details
          </h2>

          <form onSubmit={handleSubmit} noValidate className="space-y-4">
            {/* Cardholder name */}
            <div>
              <label
                htmlFor="cardholder_name"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Cardholder name
              </label>
              <input
                id="cardholder_name"
                type="text"
                placeholder="Name on card"
                value={cardholderName}
                onChange={(e) => setCardholderName(e.target.value)}
                className={`w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors focus:ring-2 focus:ring-green-500 ${
                  errors.cardholder_name ? "border-red-400 bg-red-50" : "border-gray-300 bg-white"
                }`}
              />
              {errors.cardholder_name && (
                <p className="mt-1 text-xs text-red-600">{errors.cardholder_name}</p>
              )}
            </div>

            {/* Card number */}
            <div>
              <label
                htmlFor="card_number"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Card number
              </label>
              <input
                id="card_number"
                ref={cardNumberRef}
                type="text"
                inputMode="numeric"
                placeholder="1234 5678 9012 3456"
                value={cardNumber}
                onChange={(e) => {
                  const formatted = formatCardNumber(e.target.value);
                  setCardNumber(formatted);
                  if (formatted.length === 19) expiryRef.current?.focus();
                }}
                className={`w-full rounded-lg border px-3 py-2 text-sm font-mono outline-none transition-colors focus:ring-2 focus:ring-green-500 ${
                  errors.card_number ? "border-red-400 bg-red-50" : "border-gray-300 bg-white"
                }`}
              />
              {errors.card_number && (
                <p className="mt-1 text-xs text-red-600">{errors.card_number}</p>
              )}
            </div>

            {/* Expiry + CVV row */}
            <div className="flex gap-3">
              <div className="flex-1">
                <label
                  htmlFor="expiry_date"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Expiry date
                </label>
                <input
                  id="expiry_date"
                  ref={expiryRef}
                  type="text"
                  inputMode="numeric"
                  placeholder="MM/YY"
                  value={expiryDate}
                  onChange={(e) => {
                    const formatted = formatExpiry(e.target.value);
                    setExpiryDate(formatted);
                    if (formatted.length === 5) cvvRef.current?.focus();
                  }}
                  className={`w-full rounded-lg border px-3 py-2 text-sm font-mono outline-none transition-colors focus:ring-2 focus:ring-green-500 ${
                    errors.expiry_date ? "border-red-400 bg-red-50" : "border-gray-300 bg-white"
                  }`}
                />
                {errors.expiry_date && (
                  <p className="mt-1 text-xs text-red-600">{errors.expiry_date}</p>
                )}
              </div>

              <div className="w-28">
                <label
                  htmlFor="cvv"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  CVV
                </label>
                <input
                  id="cvv"
                  ref={cvvRef}
                  type="text"
                  inputMode="numeric"
                  placeholder="123"
                  maxLength={3}
                  value={cvv}
                  onChange={(e) => setCvv(e.target.value.replace(/\D/g, "").slice(0, 3))}
                  className={`w-full rounded-lg border px-3 py-2 text-sm font-mono outline-none transition-colors focus:ring-2 focus:ring-green-500 ${
                    errors.cvv ? "border-red-400 bg-red-50" : "border-gray-300 bg-white"
                  }`}
                />
                {errors.cvv && (
                  <p className="mt-1 text-xs text-red-600">{errors.cvv}</p>
                )}
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={onCancel}
                className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 active:bg-gray-100 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 active:bg-green-800 transition-colors"
              >
                Pay ${trip.cost.toFixed(2)}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
