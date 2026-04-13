# Kindo School Payments — Backend

FastAPI backend for the Kindo school trip payment challenge. The backend is organized by modules and uses an in-process event bus to coordinate booking confirmation and payment processing.

---

## Features

- List and fetch school trips
- Create bookings for trips and cancel them
- Create payments for a booking with card details (only last 4 digits stored)
- Process payments via a legacy processor integration triggered by domain events
- Confirm or fail bookings based on payment outcomes
- Build booking receipts by combining booking, trip, and payment data
- Seed endpoint to populate sample data after deployment
- Structured logging with configurable log levels
- Environment-based configuration via `.env`
- Unit and integration tests for the current module boundaries and API flow

---

## Tech Stack

| Layer | Library |
|---|---|
| Framework | FastAPI 0.135.3 |
| ORM | SQLModel 0.0.38 (SQLAlchemy + Pydantic) |
| Database | SQLite (file-based, local) |
| Server | Uvicorn 0.44.0 |
| Config | Pydantic Settings |
| Testing | pytest + pytest-asyncio + httpx |

---

## Project Structure

```
backend/
├── app/
│   ├── infrastructure/     # config, database, logging, service factories
│   ├── modules/
│   │   ├── admin/
│   │   ├── bookings/
│   │   ├── payments/
│   │   ├── receipts/
│   │   └── trips/
│   ├── shared/             # base model + event bus
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_booking_service.py
│   ├── test_integration.py
│   ├── test_trip_service.py
│   ├── test_payment_service.py
├── .env
├── kindo.db
├── requirements.txt
├── pytest.ini
└── render.yaml
```

---

## API Endpoints

### Trips

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/trips` | List all trips |
| `GET` | `/api/v1/trips/{trip_id}` | Get a trip by ID |

### Payments

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/payments` | List all payments |
| `POST` | `/api/v1/payments` | Create a payment for a booking |
| `GET` | `/api/v1/payments/{payment_id}` | Get current payment status |

**POST `/api/v1/payments` request body:**
```json
{
  "booking_id": "uuid",
  "card_number": "4111111111111111",
  "expiry_month": 12,
  "expiry_year": 2027,
  "cvv": "123"
}
```

### Bookings

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/bookings` | List all bookings |
| `GET` | `/api/v1/bookings/{booking_id}` | Get a booking by ID |
| `POST` | `/api/v1/bookings` | Create a booking for a trip |
| `DELETE` | `/api/v1/bookings/{booking_id}` | Cancel a booking |

**POST `/api/v1/bookings` request body:**
```json
{
  "trip_id": "uuid",
  "parent_name": "John Doe",
  "child_name": "Jane Doe"
}
```

### Receipts

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/receipts/bookings/{booking_id}` | Get a receipt projection for a booking |

### Admin

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/admin/seed` | Seed database with sample trips |

## Architecture

- Routers use FastAPI dependency providers such as `get_session` for request-scoped work
- Event handlers use explicit service factories so each event gets a fresh `Session`
- `BookingCreatedEvent`, `PaymentCreatedEvent`, `PaymentSucceededEvent`, and `PaymentFailedEvent` coordinate the booking/payment lifecycle
- Card data is stored only in a process-local in-memory store long enough to complete payment processing

---

## Running Locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

To seed sample data:
```bash
curl -X POST http://localhost:8000/api/v1/admin/seed
```

---

## Testing

```bash
# All tests
pytest -q

# Unit tests only
pytest tests/test_trip_service.py tests/test_booking_service.py tests/test_payment_service.py -q

# Integration flow
pytest tests/test_integration.py -q
```

**23 tests — all passing.**

Unit tests mock repositories, services, and the legacy processor where appropriate. Integration tests use an in-memory SQLite database, the real routers, and the real event bus wiring.

---

## Deployment (Render.com)

The backend is deployed on Render.com as a Web Service configured via `render.yaml`.

**Live URL:** `https://kindo-api-3y26.onrender.com`

Post-deployment, seed the database:
```bash
curl -X POST https://kindo-api-3y26.onrender.com/api/v1/admin/seed
```

Key environment variables (set in Render dashboard):

| Variable | Value |
|---|---|
| `ENVIRONMENT` | `production` |
| `LOG_LEVEL` | `INFO` |
| `CORS_ORIGINS` | Frontend URL |

---

## Assumptions & Constraints

- **Sample trips must be seeded** before local or deployed use via `/api/v1/admin/seed`
- **Card data is not stored** — only the last 4 digits of the card number are persisted, as per PCI-DSS guidance
- **Legacy processor is a stub** — the integration simulates a real processor and may return FAILED responses randomly
- **Payment processing is in-process** — suitable for the challenge, but not durable like a real queue/worker setup
- **No authentication** — all endpoints are public, including `/admin/seed`
- **SQLite is not suitable for concurrent writes** — acceptable for this challenge, not for production
- **Free-tier SQLite does not persist** between Render redeploys — data is lost on each deploy

---

## ⚠️ Not Production Ready

This backend is a challenge submission. Before going to production, the following would be required:

**Infrastructure**
- Replace SQLite with a managed relational database (PostgreSQL, MySQL)
- Containerise with Docker and define a `docker-compose.yml` for local parity with production
- CI/CD pipeline (GitHub Actions or similar) with automated test, lint, and deploy stages
- Separate environments: development, staging, production — with separate databases and configuration

**Security**
- Authentication and authorisation on all routes (OAuth2, JWT, or API keys)
- Rate limiting on payment endpoints to prevent abuse
- Secrets management via a vault (AWS Secrets Manager, HashiCorp Vault) — not `.env` files
- HTTPS enforced; CORS restricted to known frontend origins only
- Input sanitation and stricter validation on card fields

**Reliability**
- A proper payment processing system replacing the legacy stub (Stripe, Braintree, etc.)
- Idempotency keys on payment creation to prevent duplicate charges
- Dead-letter queue or retry strategy for failed background tasks
- Database migrations managed via Alembic (not `create_all` on startup)
- Database connection pooling

**Observability**
- Distributed tracing and metrics via OpenTelemetry — exportable to Grafana, Datadog, or Honeycomb
- Structured JSON logs shipped to a log aggregation service (Loki, CloudWatch, Papertrail)
- Alerting on error rates, latency spikes, and payment failure rates
- Uptime monitoring with on-call escalation (PagerDuty, Opsgenie)
