import { useEffect, useState } from "react";
import { getTrips } from "../api/trips";
import type { TripResponse } from "../types/api";

interface Props {
  onBook: (trip: TripResponse) => void;
}

export default function TripList({ onBook }: Props) {
  const [trips, setTrips] = useState<TripResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getTrips()
      .then(setTrips)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Failed to load trips.")
      )
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[200px]">
        <div className="w-8 h-8 border-4 border-green-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 text-sm">
        {error}
      </div>
    );
  }

  if (trips.length === 0) {
    return (
      <p className="text-center text-gray-500 text-sm py-8">
        No trips available.
      </p>
    );
  }

  return (
    <ul className="space-y-4">
      {trips.map((trip) => (
        <li
          key={trip.id}
          className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <h2 className="text-lg font-semibold text-gray-900 truncate">
                {trip.title}
              </h2>
              <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                {trip.description}
              </p>
              <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500">
                <span>
                  📅{" "}
                  {new Date(trip.date).toLocaleDateString("en-NZ", {
                    day: "numeric",
                    month: "long",
                    year: "numeric",
                  })}
                </span>
                <span>📍 {trip.location}</span>
                <span className="font-medium text-gray-700">
                  ${trip.cost.toFixed(2)}
                </span>
              </div>
            </div>
            <button
              onClick={() => onBook(trip)}
              className="shrink-0 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 active:bg-green-800 transition-colors"
            >
              Book
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}
