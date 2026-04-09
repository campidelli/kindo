import { useState } from "react";
import TripList from "./components/TripList";
import RegistrationForm, { type RegistrationData } from "./components/RegistrationForm";
import type { TripResponse } from "./types/api";

type Screen = "trips" | "registration";

export default function App() {
  const [screen, setScreen] = useState<Screen>("trips");
  const [selectedTrip, setSelectedTrip] = useState<TripResponse | null>(null);

  function handleBook(trip: TripResponse) {
    setSelectedTrip(trip);
    setScreen("registration");
  }

  function handleRegistrationContinue(data: RegistrationData) {
    // Payment step will go here
    console.log("Registration data:", data);
  }

  if (screen === "registration" && selectedTrip) {
    return (
      <RegistrationForm
        trip={selectedTrip}
        onContinue={handleRegistrationContinue}
        onCancel={() => setScreen("trips")}
      />
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
