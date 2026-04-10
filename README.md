# Kindo — School Payments

A school trip payment platform that lets parents browse available trips and pay for their child's place using a credit or debit card. Built with FastAPI and React as a full-stack challenge submission.

---

## Live Demo

| | URL |
|---|---|
| Frontend | https://kindo-8r9m.onrender.com |
| Backend API docs (Swagger) | https://kindo-api-3y26.onrender.com/docs |

---

## Detailed Documentation

- [Backend README](backend/README.md) — setup, architecture, API reference, testing
- [Frontend README](frontend/README.md) — setup, screen flow, screenshots, component overview
- [AI Log](AI_LOG.md) — prompts and decisions made during AI-assisted development

---

## Capabilities

**Trip browsing**
- List all available school trips with title, description, date, location, and cost
- View individual trip details

**Payment flow**
- Multi-step wizard: trip selection → student & parent registration → card entry → receipt
- Card validation via Luhn algorithm (card number, expiry, CVV)
- Card number auto-formatted in groups of 4; auto-advances to the next field on completion
- Payment processing via a legacy processor integration (runs as a background task — does not block the API response)
- Real-time polling every 2 seconds until the payment resolves to `success` or `failed`
- Configurable payment timeout (default 30 s) — shows a warning toast if processing takes too long
- Error toasts for failed payments, network errors, and validation failures
- On success, displays a thermal EFTPOS-style receipt with masked card number

**Backend**
- `GET /api/v1/trips` — list all trips
- `GET /api/v1/trips/{id}` — get a trip by ID
- `GET /api/v1/payments` — list all payments
- `POST /api/v1/payments` — create a payment (returns `201 PENDING`)
- `GET /api/v1/payments/{id}` — poll payment status
- `POST /api/v1/admin/seed` — seed sample trip data
- `GET /api/v1/admin/health` — health check

**Security**
- Full card number and CVV are never stored — only the last 4 digits are persisted
- Input validated at both the frontend (card-validator) and backend (Pydantic)

---

## Constraints & Assumptions

- **One active trip per session** — the wizard does not support a cart or multiple trips
- **No authentication** — all endpoints are public; auth is out of scope for this challenge
- **SQLite** — not suitable for concurrent writes; acceptable for a single-instance challenge deployment
- **SQLite does not persist between Render redeploys** — data is lost on each deploy; re-seed after deployment
- **Legacy processor is a stub** — simulates a real processor with random SUCCESS/FAILED outcomes
- **Payment status is eventually consistent** — clients must poll to get the final result
- **No payment retry** — if a payment fails, the user navigates back to the trip list and starts over
- **English (NZ) locale** — dates and currency are formatted for `en-NZ`
- **Single school** — `school_id` is hardcoded in the seed data; no school-selection step

---

## Next Steps (Production Readiness)

**Infrastructure**
- Replace SQLite with a managed PostgreSQL database
- Containerise with Docker; define `docker-compose.yml` for local parity with production
- CI/CD pipeline (GitHub Actions) with automated test, lint, and deploy stages
- Separate environments: development, staging, production — with isolated databases and configuration
- Database migrations via Alembic instead of `create_all` on startup

**Security**
- Authentication and authorisation on all routes (OAuth2 / JWT)
- Rate limiting on payment endpoints to prevent abuse
- CORS restricted to known frontend origins only
- Secrets management via a vault (AWS Secrets Manager, HashiCorp Vault)
- HTTPS enforced end-to-end

**Reliability**
- Replace the legacy processor stub with a real payment gateway (Stripe, Braintree)
- Idempotency keys on payment creation to prevent duplicate charges
- Dead-letter queue or retry strategy for failed background tasks
- Database connection pooling
- WebSocket or webhook support to replace polling

**Product**
- Authentication and user accounts — parents should only see their own payments
- Payment history and receipt re-download
- Email confirmation on successful payment
- Admin dashboard to manage trips, view all payments, and issue refunds
