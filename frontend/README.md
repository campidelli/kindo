# Kindo Frontend

React + TypeScript single-page application for school trip payments, backed by the Kindo FastAPI backend.

---

## Tech Stack

- **React 19** with TypeScript
- **Vite 8** (build + dev server)
- **Tailwind CSS 4** (utility-first styling)
- **card-validator** — Luhn-based card number, expiry, and CVV validation
- **Vitest + Testing Library** — unit and component tests

---

## Getting Started

```bash
cd frontend
npm install
cp .env.example .env      # set VITE_API_URL if needed
npm run dev               # http://localhost:5173
```

### Available Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start local dev server with HMR |
| `npm run build` | Type-check + production build |
| `npm test` | Run test suite (vitest) |
| `npm run lint` | ESLint |

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Base URL of the backend API |
| `VITE_PAYMENT_TIMEOUT_MS` | `30000` | How long to poll before showing a "taking too long" warning |

Copy `.env.example` to `.env` for local development. Production values are set in `render.yaml`.

---

## Screen Flow

The app is a linear wizard with four screens managed in `App.tsx`.

```
Trips  ──book──▶  Registration  ──continue──▶  Payment  ──submit──▶  Receipt
                       │                           │
                    cancel                      cancel
                       │                           │
                       ▼                           ▼
                     Trips                    Registration
```

### 1 — Trip List

Fetches available trips from `GET /api/v1/trips` and displays them as cards.

_Screenshot placeholder_
![Trip List](docs/screenshots/01-trip-list.png)

---

### 2 — Registration Form

Collects **student name** and **parent/guardian name** before payment.  
Both fields are required and trimmed on submit.

_Screenshot placeholder_
![Registration Form](docs/screenshots/02-registration.png)

---

### 3 — Payment Form

Collects card details with live formatting and validation:
- **Cardholder name** — pre-filled from parent name, editable
- **Card number** — formatted in groups of 4, validated via Luhn algorithm
- **Expiry date** — auto-formatted to `MM/YY`
- **CVV** — 3 digits

On submit, calls `POST /api/v1/payments` then polls `GET /api/v1/payments/{id}` every 2 seconds. A full-screen **Processing** modal blocks interaction during polling.

_Screenshot placeholder_
![Payment Form](docs/screenshots/03-payment.png)

---

### 4 — Payment Receipt

Shown on `status: "success"`. Styled as a thermal EFTPOS receipt (pale yellow, monospace font, serrated edges). Displays:
- Trip title, date, and location
- Student and parent names
- Masked card number (`**** **** **** XXXX`)
- Transaction ID
- Total paid

A green **"Payment confirmed!"** toast appears in the top-right corner.

_Screenshot placeholder_
![Payment Receipt](docs/screenshots/04-receipt.png)

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Payment polling returns `failed` | Red error toast with the API's `error_message` |
| Payment exceeds `VITE_PAYMENT_TIMEOUT_MS` | Amber warning toast — user can retry |
| Network / API error during polling | Red error toast with error detail |
| Failed to submit payment | Red error toast |

---

## Assumptions & Constraints

- **One active trip per session.** The wizard does not support a cart or multiple trips.
- **Card data is never stored client-side.** Only the masked number is displayed on the receipt; full card details are sent once to the backend and not retained.
- **Polling only** — no WebSocket or webhook support. The frontend polls every 2 seconds until success, failure, or timeout.
- **Single school.** `school_id` is hardcoded in the backend seed; the frontend has no school-selection step.
- **No authentication.** Any user can browse trips and submit a payment. Auth is out of scope for this challenge.
- **No payment retry flow.** If a payment fails, the user navigates back to the trip list and starts over.
- **Mobile-first layout** with a max-width of `2xl` (672 px). Not optimised for wide desktop layouts.
- **English (NZ) locale only.** Dates and currency are formatted for `en-NZ`.

---

## Deployment

Deployed as a Render Static Site. See `render.yaml` for the build config.

Production URL: **https://kindo-8r9m.onrender.com**
