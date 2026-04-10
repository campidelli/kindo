# Kindo School Payments — Backend

FastAPI backend for the Kindo school trip payment challenge. Manages trips and processes payments via a legacy payment processor integration.

---

## Features

- List and fetch school trips
- Create payments for a trip with card details (only last 4 digits stored)
- Asynchronous payment processing via a legacy processor integration — does not block the API response
- Poll payment status by ID (PENDING → SUCCESS / FAILED)
- Seed endpoint to populate sample data after deployment
- Structured logging with configurable log levels
- Environment-based configuration via `.env`

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
│   ├── core/           # config, database, logging
│   ├── enums/          # PaymentStatus enum
│   ├── models/         # SQLModel table definitions
│   ├── schemas/        # Pydantic request/response schemas
│   ├── repositories/   # Data access layer
│   ├── services/       # Business logic
│   ├── routers/        # API route handlers
│   ├── integrations/   # Legacy payment processor wrapper
│   └── data/           # seed.py + kindo.db (SQLite)
├── tests/
│   ├── test_trip_service.py
│   ├── test_payment_service.py
│   ├── test_trips_integration.py
│   └── test_payments_integration.py
├── .env
├── .env.example
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
| `GET` | `/api/v1/payments` | List all payments (most recent first) |
| `POST` | `/api/v1/payments` | Create a payment (returns `201 PENDING`) |
| `GET` | `/api/v1/payments/{payment_id}` | Get current payment status |

**POST `/api/v1/payments` request body:**
```json
{
  "trip_id": "uuid",
  "student_name": "Jane Doe",
  "parent_name": "John Doe",
  "card_number": "4111111111111111",
  "expiry_date": "12/27",
  "cvv": "123"
}
```

Payment processing runs as a background task. Poll `GET /api/v1/payments/{id}` to check the result (`PENDING`, `SUCCESS`, or `FAILED`).

### Admin

| Method | Path | Description |
|---|---|---|
| `POST` | `/admin/seed` | Seed database with sample trip |
| `GET` | `/admin/health` | Health check |

---

## Running Locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env

# Start the server
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

To seed sample data:
```bash
curl -X POST http://localhost:8000/admin/seed
# or run directly
python -m app.data.seed
```

---

## Testing

```bash
# All tests
pytest tests/ -v

# Unit tests only (services, no I/O)
pytest tests/test_trip_service.py tests/test_payment_service.py -v

# Integration tests only (full HTTP flow, in-memory SQLite)
pytest tests/test_trips_integration.py tests/test_payments_integration.py -v
```

**28 tests — 15 unit, 13 integration — all passing in ~0.3s.**

Unit tests mock all repositories and the legacy processor. Integration tests use an in-memory SQLite database and FastAPI's `TestClient`. No network or file I/O required.

---

## Deployment (Render.com)

The backend is deployed on Render.com as a Web Service configured via `render.yaml`.

**Live URL:** `https://kindo-api-3y26.onrender.com`

Post-deployment, seed the database:
```bash
curl -X POST https://kindo-api-3y26.onrender.com/admin/seed
```

Key environment variables (set in Render dashboard):

| Variable | Value |
|---|---|
| `ENVIRONMENT` | `production` |
| `LOG_LEVEL` | `INFO` |
| `CORS_ORIGINS` | Frontend URL |

---

## Assumptions & Constraints

- **One active trip** is seeded as sample data; the UI assumes at least one trip exists
- **Card data is not stored** — only the last 4 digits of the card number are persisted, as per PCI-DSS guidance
- **Legacy processor is a stub** — the integration simulates a real processor and may return FAILED responses randomly
- **Payment status is eventually consistent** — clients must poll `GET /api/v1/payments/{id}` to get the final result
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
