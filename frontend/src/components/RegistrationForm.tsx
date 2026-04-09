import { useState } from "react";
import type { TripResponse } from "../types/api";

export interface RegistrationData {
  student_name: string;
  parent_name: string;
}

interface Props {
  trip: TripResponse;
  onContinue: (data: RegistrationData) => void;
  onCancel: () => void;
}

export default function RegistrationForm({ trip, onContinue, onCancel }: Props) {
  const [studentName, setStudentName] = useState("");
  const [parentName, setParentName] = useState("");
  const [errors, setErrors] = useState<Partial<RegistrationData>>({});

  function validate(): boolean {
    const next: Partial<RegistrationData> = {};
    if (!studentName.trim()) next.student_name = "Student name is required.";
    if (!parentName.trim()) next.parent_name = "Parent name is required.";
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (validate()) {
      onContinue({ student_name: studentName.trim(), parent_name: parentName.trim() });
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
          {/* Trip summary */}
          <div className="mb-6 rounded-lg bg-green-50 border border-green-200 p-4">
            <p className="text-xs font-medium text-green-700 uppercase tracking-wide mb-1">
              Booking
            </p>
            <p className="font-semibold text-gray-900">{trip.title}</p>
            <p className="text-sm text-gray-500 mt-1">
              {new Date(trip.date).toLocaleDateString("en-NZ", {
                day: "numeric",
                month: "long",
                year: "numeric",
              })}{" "}
              · {trip.location}
            </p>
            <p className="text-sm font-medium text-gray-700 mt-1">
              ${trip.cost.toFixed(2)}
            </p>
          </div>

          <h2 className="text-base font-semibold text-gray-900 mb-4">
            Student &amp; Parent Details
          </h2>

          <form onSubmit={handleSubmit} noValidate className="space-y-4">
            <div>
              <label
                htmlFor="student_name"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Student name
              </label>
              <input
                id="student_name"
                type="text"
                value={studentName}
                onChange={(e) => setStudentName(e.target.value)}
                placeholder="e.g. Jane Doe"
                className={`w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors focus:ring-2 focus:ring-green-500 ${
                  errors.student_name
                    ? "border-red-400 bg-red-50"
                    : "border-gray-300 bg-white"
                }`}
              />
              {errors.student_name && (
                <p className="mt-1 text-xs text-red-600">{errors.student_name}</p>
              )}
            </div>

            <div>
              <label
                htmlFor="parent_name"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Parent / Guardian name
              </label>
              <input
                id="parent_name"
                type="text"
                value={parentName}
                onChange={(e) => setParentName(e.target.value)}
                placeholder="e.g. John Doe"
                className={`w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors focus:ring-2 focus:ring-green-500 ${
                  errors.parent_name
                    ? "border-red-400 bg-red-50"
                    : "border-gray-300 bg-white"
                }`}
              />
              {errors.parent_name && (
                <p className="mt-1 text-xs text-red-600">{errors.parent_name}</p>
              )}
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
                Continue to payment
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
