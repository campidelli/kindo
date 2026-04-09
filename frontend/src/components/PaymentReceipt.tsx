import type { TripResponse, PaymentDetailResponse } from "../types/api";

interface Props {
  trip: TripResponse;
  payment: PaymentDetailResponse;
  onDone: () => void;
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4">
      <span className="text-stone-500">{label}</span>
      <span className="text-right text-stone-800">{value}</span>
    </div>
  );
}

function Divider() {
  return (
    <p className="my-3 select-none overflow-hidden tracking-widest text-stone-400">
      {"- ".repeat(20)}
    </p>
  );
}

export default function PaymentReceipt({ trip, payment, onDone }: Props) {
  const paidAt = new Date(payment.created_at);
  const tripDate = new Date(trip.date);

  const formattedPaidAt = paidAt.toLocaleString("en-NZ", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });

  const formattedTripDate = tripDate.toLocaleDateString("en-NZ", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  const maskedCard = `**** **** **** ${payment.card_last_four}`;

  return (
    <div className="flex min-h-screen flex-col items-center bg-stone-100 px-4 py-10">
      {/* Receipt paper */}
      <div
        className="w-full max-w-sm font-mono text-xs leading-relaxed shadow-xl"
        style={{ backgroundColor: "#fffde7" }}
      >
        {/* Top serrated edge */}
        <div
          className="h-4 w-full"
          style={{
            background:
              "linear-gradient(-45deg, #fffde7 25%, transparent 25%) 0 0," +
              "linear-gradient(45deg, #fffde7 25%, transparent 25%) 0 0," +
              "linear-gradient(-45deg, transparent 75%, #fffde7 75%)," +
              "linear-gradient(45deg, transparent 75%, #fffde7 75%)",
            backgroundSize: "16px 16px",
            backgroundColor: "#d6d3d1",
          }}
        />

        <div className="px-6 pb-8 pt-6">
          {/* Header */}
          <div className="mb-4 text-center">
            <p className="text-lg font-bold uppercase tracking-widest text-stone-800">
              KINDO
            </p>
            <p className="text-stone-500">School Payments</p>
            <p className="mt-1 text-stone-400">{formattedPaidAt}</p>
          </div>

          <Divider />

          {/* Transaction */}
          <div className="mb-1 text-center font-bold uppercase tracking-widest text-stone-700">
            ✓ APPROVED
          </div>
          {payment.transaction_id && (
            <div className="mb-2 text-center text-stone-400">
              TXN: {payment.transaction_id}
            </div>
          )}

          <Divider />

          {/* Trip details */}
          <p className="mb-2 font-bold uppercase tracking-wider text-stone-600">
            TRIP
          </p>
          <div className="space-y-1">
            <p className="font-bold text-stone-800">{trip.title}</p>
            <Row label="Date" value={formattedTripDate} />
            <Row label="Location" value={trip.location} />
          </div>

          <Divider />

          {/* People */}
          <p className="mb-2 font-bold uppercase tracking-wider text-stone-600">
            STUDENT
          </p>
          <div className="space-y-1">
            <Row label="Name" value={payment.student_name} />
            <Row label="Parent" value={payment.parent_name} />
          </div>

          <Divider />

          {/* Payment */}
          <p className="mb-2 font-bold uppercase tracking-wider text-stone-600">
            PAYMENT
          </p>
          <div className="space-y-1">
            <Row label="Card" value={maskedCard} />
            <Row label="Method" value="CREDIT / DEBIT" />
          </div>

          <Divider />

          {/* Total */}
          <div className="flex justify-between text-base font-bold text-stone-800">
            <span>TOTAL PAID</span>
            <span>${trip.cost.toFixed(2)}</span>
          </div>

          <Divider />

          <p className="mt-2 text-center text-stone-400">
            Thank you for using Kindo!
          </p>
          <p className="text-center text-stone-400">
            Please retain this receipt.
          </p>
        </div>

        {/* Bottom serrated edge */}
        <div
          className="h-4 w-full rotate-180"
          style={{
            background:
              "linear-gradient(-45deg, #fffde7 25%, transparent 25%) 0 0," +
              "linear-gradient(45deg, #fffde7 25%, transparent 25%) 0 0," +
              "linear-gradient(-45deg, transparent 75%, #fffde7 75%)," +
              "linear-gradient(45deg, transparent 75%, #fffde7 75%)",
            backgroundSize: "16px 16px",
            backgroundColor: "#d6d3d1",
          }}
        />
      </div>

      <button
        onClick={onDone}
        className="mt-8 rounded-lg bg-green-600 px-8 py-2.5 text-sm font-medium text-white hover:bg-green-700 transition-colors"
      >
        Back to trips
      </button>
    </div>
  );
}
