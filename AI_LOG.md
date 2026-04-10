# AI Interaction Log — Kindo Challenge

> Tracks key decisions, prompts, and outputs from each AI-assisted session using GitHub Copilot (GPT-5.4).

---

## Session 1 — 2026-04-09

### Prompt 1
> "based on the challenge file, let's plan a fastapi backend first, using restful apis. We need to have only Trips and Payments. Create a plan where we only have the very basic API using SQLite. Ensure to use the latest versions of all libs you use. Also, create a md file to keep a concise log of my interaction with you."

**AI Output — Plan approved:**
- FastAPI + SQLite, two resources only (Trips, Payments)
- Pydantic v2 + SQLAlchemy 2.x, no SQLModel
- `asyncio.to_thread()` to run blocking `LegacyPaymentProcessor`
- Only `card_last_four` stored — full card + CVV never persisted (security)
- CORS wildcard for development
- Seed script to insert a sample trip

---

### Prompt 2
> "Start implementation"

**AI actions:**
- Created `AI_LOG.md` (this file)
- Created `backend/` directory with full app structure
- Moved `legacy_payment.py` into `backend/`
- Wrote `requirements.txt`, `app/database.py`, `app/models.py`, `app/schemas.py`
- Wrote `app/services/payment_service.py` (wraps legacy processor via `asyncio.to_thread`)
- Wrote `app/routers/trips.py` and `app/routers/payments.py`
- Wrote `app/main.py` (lifespan, CORS, router registration)
- Wrote `seed.py` (inserts one sample trip)
- Installed dependencies via `pip install -r requirements.txt`
- Verified server starts and `/docs` is accessible

---

### Prompt 3
> "fastapi latest version is 0.135.3. Ensure to upgrade it and that the others are using the latest versions too"

**AI actions:**
- Updated backend dependency minimums to the latest verified installed versions
- Set FastAPI to `>=0.135.3`
- Set Uvicorn to `>=0.44.0`
- Set SQLAlchemy to `>=2.0.49`
- Set Pydantic to `>=2.12.5`
- Set `python-multipart` to `>=0.0.24`

---

### Prompt 4
> "Forget about it. Use SQLModel instead"

**AI actions:**
- Replaced `sqlalchemy` dependency with `sqlmodel`
- Migrated the database layer in `backend/app/database.py` to SQLModel `Session` and `create_engine`
- Rewrote `backend/app/models.py` from SQLAlchemy declarative models to `SQLModel, table=True` models
- Updated `backend/app/routers/trips.py` to use `select()` and `db.exec(...)`
- Updated `backend/app/routers/payments.py` to use SQLModel session types
- Updated `backend/app/main.py` to create tables with `SQLModel.metadata.create_all(...)`
- Updated `backend/seed.py` to use SQLModel sessions and reseeded the SQLite database
- Installed and verified `sqlmodel==0.0.38`
- Restarted the API and verified `GET /api/v1/trips` and `POST /api/v1/payments`

---

### Prompt 5
> "Isn't pydantic part of fastapi? Do I need it here? And why the multipart lib? Our APIs are restful"

**AI output and actions:**
- Confirmed Pydantic is used by FastAPI internally, but keeping it explicit is justified because the project imports it directly in `backend/app/schemas.py`
- Removed `python-multipart` because the API is JSON-only and does not use form submissions or file uploads
- Left `pydantic` explicit in `backend/requirements.txt` for direct version control

---

### Prompt 6
> "You are not updating the AI log"

**AI actions:**
- Reviewed the current log contents
- Appended the missing entries for dependency updates, SQLModel migration, and dependency cleanup
- Corrected the model reference in this file to `GPT-5.4`

---

### Prompt 7
> "add a gitignore file to backend folder"

**AI actions:**
- Created `backend/.gitignore` ignoring `.venv/`, `*.db`, `__pycache__`, build artifacts, `.env` files, and IDE folders

---

### Prompt 8
> "this should be an enum, PaymentStatus" (referring to `Payment.status: str`)

**AI actions:**
- Added `PaymentStatus(str, enum.Enum)` with `SUCCESS = "success"` and `FAILED = "failed"` to `backend/app/models.py`
- Changed `Payment.status` type from `str` to `PaymentStatus`
- Updated `backend/app/routers/payments.py` to use `PaymentStatus.SUCCESS` / `PaymentStatus.FAILED` instead of raw strings

---

### Prompt 9
> "Create a BaseModel with id uuidv4 and created_at, make the other entities inherit from it"

**AI actions:**
- Added `BaseModel(SQLModel)` to `backend/app/models.py` with `id: uuid.UUID` (default `uuid4`) and `created_at: datetime`
- Removed duplicate `id` and `created_at` fields from `Trip` and `Payment`; both now inherit from `BaseModel`
- Updated `Payment.trip_id` from `int` to `uuid.UUID`
- Updated `backend/app/schemas.py`: `TripResponse.id`, `PaymentRequest.trip_id`, `PaymentResponse.payment_id` all changed to `uuid.UUID`
- Updated `backend/app/routers/trips.py`: `trip_id` path param changed to `uuid.UUID`
- Dropped and re-seeded the SQLite DB; verified UUID ids in API response

---

### Prompt 10
> "all dates must be datetime" (referring to `Trip.date: str`)

**AI actions:**
- Changed `Trip.date` from `str` to `datetime` in `backend/app/models.py`
- Updated `TripResponse.date` from `str` to `datetime` in `backend/app/schemas.py`
- Updated `backend/seed.py` to use `datetime(2026, 6, 15)` instead of the ISO string
- Dropped and re-seeded; confirmed `date` serialises as `"2026-06-15T00:00:00"`

---

### Prompt 11
> "utcnow is deprecated."

**AI actions:**
- Replaced `default_factory=datetime.utcnow` with `default_factory=lambda: datetime.now(timezone.utc)` in `backend/app/models.py`
- Added `timezone` to the `datetime` import in both `backend/app/models.py` and `backend/seed.py`

---

### Prompt 12
> "dont forget to update the ai log"

**AI actions:**
- Appended all missing entries (Prompts 7–11) to this log

---

### Prompt 13
> "ALl http status codes should use HttpStatus lib instead of hardcoded values"

**AI actions:**
- Replaced hardcoded HTTP status integers in both routers with FastAPI `status` constants
- Updated trip not-found responses to use `status.HTTP_404_NOT_FOUND`
- Updated payment creation response to use a named status constant instead of a raw integer

---

### Prompt 14
> "service layers shouldn't be aware of schema dtos. Use primitive params instead"

**AI actions:**
- Removed DTO/schema coupling from the payment service signature
- Updated the payment router to unpack the request DTO and pass only primitive values into the service layer
- Preserved the router as the API boundary and kept the service layer independent of request schemas

---

### Prompt 15
> "Our payment API create method will generate a payment id, create the payment in the db with status pending and trigger a fastapi background_task that calls the legacy payment processor. That task will update the db when the payment is finished. The create endpoint should return 201 with the paymentId and other relevant information. We need an API to fetch the payment by id"

**AI actions:**
- Added `PENDING` to `PaymentStatus` in `backend/app/models.py`
- Created `backend/app/repositories/` with `TripRepository` and `PaymentRepository`
- Added `backend/app/services/trip_service.py` and rewrote `backend/app/services/payment_service.py` as a repository-backed service with background-processing support
- Changed `POST /api/v1/payments` to create a pending payment record first, enqueue a FastAPI `BackgroundTasks` job, and return `201 Created`
- Added `GET /api/v1/payments/{payment_id}` to fetch the current payment state
- Introduced `PaymentCreatedResponse` and `PaymentDetailResponse` in `backend/app/schemas.py`
- Slimmed the trips router to use `TripService` as well
- Fixed SQLite path resolution in `backend/app/database.py` so the DB file is stable regardless of the process working directory
- Verified end to end: `POST /api/v1/payments` returned `201` with `status: "pending"`, and `GET /api/v1/payments/{id}` returned the updated payment with final status and transaction data

---

### Prompt 16
> "I have moved some components around, validate those changes"

**AI actions:**
- Verified import paths after file reorganization
- Found incorrect imports using `from backend.app.core.database` in routers and main.py
- Fixed all three files to use `from app.core.database` instead
- Created `app/integrations/` package with `legacy_payment_processor.py` stub
- Fixed `payment_service.py` to import from the new integrations package
- Validated all imports resolve correctly and the app initializes

---

### Prompt 17
> "create a dataclass to be passed here instead of these primitives"

**AI actions:**
- Created `CreatePaymentData` dataclass with trip_id, student_name, parent_name, card_number, expiry_date, cvv
- Updated `PaymentService.create_pending_payment()` to accept `data: CreatePaymentData` instead of individual parameters
- Updated the payments router to instantiate and pass `CreatePaymentData` to the service
- Validated imports and app initialization

---

### Prompt 18
> "why there are two kindo.db? one in the data folder and another outside of it?"

**AI actions:**
- Identified root cause: database path in `app/core/database.py` was resolving to `app/kindo.db` instead of `app/data/kindo.db`
- Fixed path resolution from `Path(__file__).resolve().parent.parent / "kindo.db"` to `Path(__file__).resolve().parent.parent / "data" / "kindo.db"`

---

### Prompt 19
> "I want that kindo.db location be in the data folder"

**AI actions:**
- Already implemented; database now correctly resolves to `backend/app/data/kindo.db`

---

### Prompt 20
> "do I need this file?" (referring to `app/__init__.py`)

**AI output:**
- Confirmed that `app/__init__.py` is necessary; it marks the directory as a Python package and allows the import system to resolve `from app.x import y` statements
- Same applies to all `__init__.py` files in subfolders

---

### Prompt 21
> "add a .env file to send relevant config to the application and add logs to the application too"

**AI actions:**
- Added `pydantic-settings>=2.9.1` to `requirements.txt` and installed it
- Created `app/core/config.py` with `Settings` dataclass that reads from `.env` file
  - Configurable: `app_name`, `app_version`, `log_level`, `cors_origins`, `database_path`
- Created `app/core/logging.py` with `configure_logging()` and `get_logger()` helpers
- Created `.env` with default development settings
- Created `.env.example` as a template for teammates
- Updated `app/main.py` to:
  - Import and use `settings` for app title, version, CORS origins
  - Call `configure_logging()` in the startup lifespan
  - Log startup messages including database path
- Updated `app/services/payment_service.py` to:
  - Import logger and use `get_logger(__name__)`
  - Log successful payment creation with PENDING status
  - Log payment processing results (SUCCESS/FAILED)
  - Log warnings for failed payment processor calls
- Updated `app/core/database.py` to use `settings.database_path` instead of hardcoded path

---

### Prompt 22
> "add logger.error when we raise errors"

**AI actions:**
- Added `logger.error()` calls in `payment_service.py` before each exception raise:
  - `create_pending_payment`: logs when trip not found
  - `process_pending_payment`: logs when payment not found, logs when trip not found during processing (includes both trip ID and payment ID)

---

### Prompt 23
> "remove this file from .gitignore" (referring to `.env.example`)

**AI actions:**
- Changed `.gitignore` from `env.*` to `env.local`
- Now `.env.example` is tracked by git while `.env` (with secrets) remains ignored

---

### Prompt 24
> "write unit tests for the services not for routers or repositories"

**AI actions:**
- Added `pytest>=8.3.5` and `pytest-asyncio>=0.26.0` to `requirements.txt` and installed
- Created `pytest.ini` with `asyncio_mode = auto`
- Created `tests/` package with `__init__.py` and `conftest.py`
- Added factory helpers in `conftest.py`: `make_trip()`, `make_payment()`, `mock_session()`
- Created `tests/test_trip_service.py` with 4 tests covering `get_all()` and `get_by_id()` (with all branches)
- Created `tests/test_payment_service.py` with 9 tests covering:
  - `create_pending_payment()`: creates with PENDING status, extracts card last 4, raises when trip not found
  - `get_payment_by_id()`: found, not found
  - `process_pending_payment()`: updates to SUCCESS, updates to FAILED with error message, raises when payment not found, raises when trip not found during processing
- All repositories and legacy processor mocked — no database or network I/O required
- Ran `pytest -v`: **13/13 tests passing**

---

### Prompt 25
> "let's add some integration tests now"

**AI actions:**
- Added `httpx>=0.28.1` to `requirements.txt` and installed
- Added `conftest.py` `client` fixture using `TestClient` with in-memory SQLite database (overrides `get_session` dependency)
- Created `tests/test_trips_integration.py` with 4 tests:
  - `GET /api/v1/trips` returns 200 with empty list on clean DB
  - `GET /api/v1/trips/{id}` returns 404 for unknown UUID
  - `GET /api/v1/trips` returns list with seeded trip
  - `GET /api/v1/trips/{id}` returns seeded trip by ID
- Created `tests/test_payments_integration.py` with 8 tests:
  - `POST /api/v1/payments` returns 201 with PENDING status
  - `POST /api/v1/payments` returns 404 when trip not found
  - `POST /api/v1/payments` returns 422 when body is missing required fields
  - `GET /api/v1/payments/{id}` returns 404 for unknown UUID
  - `GET /api/v1/payments/{id}` returns PENDING payment just after creation
  - Full background task flow: POST creates PENDING, background task runs, GET returns SUCCESS or FAILED
- Ran `pytest -v`: **25/25 tests passing in ~0.3s**

---

### Prompt 26
> "add a new endpoint to retry the payment via paymentId"

**AI actions:**
- Added `PATCH /api/v1/payments/{payment_id}/retry` endpoint to `app/routers/payments.py`
- Returns 404 if payment not found
- Returns 409 if payment is not in FAILED status
- Creates a new background task to reprocess the payment
- Returns 200 with the current payment state
- Added unit test for the retry service logic in `tests/test_payment_service.py`
- Added integration tests for the retry endpoint in `tests/test_payments_integration.py`
- All tests passing

---

### Prompt 27
> "undo it, If I need I create a new payment"

**AI actions:**
- Removed `PATCH /api/v1/payments/{payment_id}/retry` endpoint from `app/routers/payments.py`
- Removed retry-related unit and integration tests
- Reverted to 25/25 tests passing

---

### Prompt 28
> "I want to deploy this backend to some free service, what do you suggest?"

**AI output:**
- Compared Render.com, Fly.io, Vercel, Netlify, and Heroku
- Recommended **Render.com** as the best fit: free tier for web services, auto-deploy from GitHub, supports Python natively, minimal configuration required

---

### Prompt 29
> "I also need to deploy the frontend...if I could use one platform, it would be ideal"

**AI output:**
- Confirmed Render.com handles both: Web Service for FastAPI backend, Static Site (free, unlimited) for frontend
- Outlined CORS configuration needed to connect the two services

---

### Prompt 30
> "what about (Vercel, Netlify, Heroku?)"

**AI output:**
- Compared all four platforms in detail for Python + frontend support
- Reaffirmed Render.com recommendation: only platform with truly free backend (Python) + frontend static site

---

### Prompt 31
> "how can I integrate render.com to my app?"

**AI output:**
- Provided step-by-step Render.com integration guide:
  - Create Web Service on Render, connect GitHub repo
  - Configure build/start commands, environment variables
  - Created `backend/render.yaml` deployment config (Python 3.13, auto-build/start, env vars)

---

### Prompt 32
> "Start implementation"

**AI actions:**
- Updated `render.yaml` to add `ENVIRONMENT=production` env var
- Updated `app/core/config.py` to add `environment` field and `get_cors_origins()` method:
  - Development: returns `["*"]`
  - Production: restricts to specific frontend URLs
- Updated `app/main.py` to call `settings.get_cors_origins()` instead of `settings.cors_origins`
- Updated `.env.example` with `ENVIRONMENT` variable documentation
- Created `RENDER_DEPLOYMENT.md` — comprehensive step-by-step deployment guide for backend and frontend

---

### Prompt 33
> "I need to run the seed after the deployment, how do I do it?"

**AI actions:**
- Added `POST /admin/seed` endpoint to `app/main.py` — triggers `app/data/seed.py` via HTTP after deployment
- Added `GET /health` endpoint for monitoring/load balancers
- Updated `RENDER_DEPLOYMENT.md` to document post-deployment seed curl command

---

### Prompt 34
> "add a proper route file for seeding"

**AI actions:**
- Created `app/routers/admin.py` with dedicated admin router (tags: `["admin"]`)
  - `POST /seed` — triggers database seeding
  - `GET /health` — health check endpoint
- Updated `app/main.py` to import `admin` router and register with `/admin` prefix
- Removed inline endpoint definitions from `main.py`

---

### Prompt 35
> "update the endpoint to kindo-api-3y26.onrender.com and the correct paths"

**AI actions:**
- Updated all placeholder URLs in `RENDER_DEPLOYMENT.md` from `kindo-api.onrender.com` to `kindo-api-3y26.onrender.com`
- Updated health check path from `/health` to `/admin/health` to match the new admin router prefix
- Updated seed path from `/admin/seed` to `/admin/seed` (confirmed correct)
- Updated frontend `VITE_API_URL` examples to point to deployed endpoint

---

## Session 2 — 2026-04-10

### Prompt 36
> "Find another suitable card validator lib, it doesn't make sense to do the validation and formatting of it manually"

**AI actions:**
- Researched alternatives; selected **`creditcardutils`** (lightweight, no ESM/CJS issues in test environments)
- Installed `creditcardutils` and removed manual regex validation from `PaymentForm.tsx`
- Used `validateCardNumber`, `validateCardExpiry`, `validateCardCVC` from the library
- All 16 tests passed

---

### Prompt 37
> "undo the library part. I want to use https://www.npmjs.com/package/card-validator instead"

**AI actions:**
- Uninstalled `creditcardutils`, installed `card-validator@10.0.4`
- Updated imports to `number`, `expirationDate`, `cvv` from `card-validator`
- Discovered `expirationDate()` requires the full `MM/YY` string, not separate arguments — fixed
- Removed stale `card-validator` entry from `package.json` (was left from previous attempt)
- All 16 tests passed

---

### Prompt 38
> "add the cardholder name field, pre fill it with the parent name"

**AI actions:**
- Added `cardholder_name: string` to `CardData` interface
- Added `cardholderName` state, pre-filled from `registration.parent_name`
- Added required validation ("Enter the cardholder name.")
- Added the field to the form UI above the card number field
- Updated `PaymentForm.test.tsx` to expect `cardholder_name: "John Doe"` in the `onConfirm` call
- All 16 tests passed

---

### Prompt 39
> "Now wire the payment form with the api. I need a processing payment blocking modal, keep polling the api to get the payment details until the status changes to success. Add a configurable (via env) timeout that closes the modal and displays a message that the payment is taking too long. Also, add an error toast if an error happens during the process"

**AI actions:**
- Created `ProcessingModal.tsx` — full-screen overlay with spinner, blocks interaction during polling
- Created `Toast.tsx` — top-right dismissable toast with `error` and `warning` variants
- Rewrote `App.tsx` to wire the full payment flow:
  - `POST /api/v1/payments` on form submit
  - Polls `GET /api/v1/payments/{id}` every 2 seconds via `setInterval`
  - `status: "success"` → navigates to success screen
  - `status: "failed"` → shows error toast with `error_message`
  - Network/API error → shows error toast
  - Timeout (configurable via `VITE_PAYMENT_TIMEOUT_MS`, default 30s) → shows warning toast
- Added `VITE_PAYMENT_TIMEOUT_MS=30000` to `.env`
- Added success screen with checkmark and "Back to trips" button
- All 16 tests passed

---

### Prompt 40
> "show the toast on the top right"

**AI actions:**
- Changed `Toast.tsx` positioning from `bottom-5 right-5` to `top-5 right-5`

---

### Prompt 41
> "This is the response you are receiving, it should be not timing out" (API returning `status: "success"` lowercase)

**AI actions:**
- Fixed status comparison: polling used `"SUCCESS"` (uppercase) but API returns `"success"` (lowercase)
- Updated `PaymentDetailResponse.status` type from `"PENDING" | "SUCCESS" | "FAILED"` to lowercase equivalents
- Updated both polling comparisons in `App.tsx`

---

### Prompt 42
> "can you ignore the case?"

**AI actions:**
- Added `detail.status.toLowerCase()` before comparison so any casing from the API works
- Changed `PaymentDetailResponse.status` type from union to `string` to reflect the real API contract

---

### Prompt 43
> "No overload matches this call. The last overload gave the following error. Object literal may only specify known properties, and 'test' does not exist in type 'UserConfigExport'."

**AI output:**
- Explained the error: `defineConfig` from `vite` doesn't know about the `test` key; need to import from `vitest/config` instead
- Updated `vite.config.ts` import from `'vite'` to `'vitest/config'`
- Error resolved, 16 tests still passing

---

### Prompt 44
> "let's deploy this front end to render"

**AI actions:**
- Created `frontend/render.yaml` as a Render Static Site blueprint:
  - `runtime: static`, `rootDir: frontend`, `buildCommand: npm ci && npm run build`, `staticPublishPath: ./dist`
  - SPA rewrite rule: `/* → /index.html`
  - Env vars: `VITE_API_URL` and `VITE_PAYMENT_TIMEOUT_MS`
- Added `VITE_PAYMENT_TIMEOUT_MS` to `.env.example` and `.env.production`
- Fixed a TypeScript build blocker: removed unused `waitFor` import in `RegistrationForm.test.tsx`
- Production build passed: 3 files, 216 kB JS

---

### Prompt 45
> "add the remaining env vars here, and the cors should be from https://kindo-8r9m.onrender.com/"

**AI actions:**
- Updated `backend/render.yaml` to add all missing env vars: `APP_NAME`, `APP_VERSION`, `DATABASE_PATH`
- Set `CORS_ORIGINS` to `'["https://kindo-8r9m.onrender.com"]'`

---

### Prompt 46
> "why am I getting CORS error when I run the application on render?"

**AI analysis and actions:**
- Root cause: `get_cors_origins()` in `app/core/config.py` hardcoded `"kindo-frontend.onrender.com"` in production, completely ignoring the `CORS_ORIGINS` env var
- Fixed `get_cors_origins()` to simply `return self.cors_origins`
- `CORS_ORIGINS` from `render.yaml` is now the single source of truth

---

### Prompt 47
> "these settings should be getting the values from the environment variables"

**AI actions:**
- Removed `Path(__file__)` anchor from `database_path` default — replaced with a plain relative string `"app/data/kindo.db"`
- Changed `env_file` path from `Path(__file__).resolve().parent.parent.parent / ".env"` to `".env"` (relative to working directory, matching Render's working dir)
- Changed `database_path` type from `Path` to `str` to avoid implicit path resolution
- All six settings now read cleanly from process environment variables with `.env` as a local fallback

---

### Prompt 48
> "add one more trip to the auckland aquarium"

**AI actions:**
- Added Auckland Aquarium trip (Kelly Tarlton's) to `backend/app/data/seed.py`
- Refactored seed logic to check per-trip by `activity_id` instead of skipping all if any trip exists
- New trip: cost `$42.00`, date `2026-07-22`, location `Kelly Tarlton's Sea Life Aquarium, Auckland`, school/activity ID `ACT-AQU-2026`

---

### Prompt 49
> "create a nice PaymentReceipt component, I want something that looks like a EFTPOS receipt"

**AI actions:**
- Created `frontend/src/components/PaymentReceipt.tsx`:
  - Pale yellow background (`#fffde7`), monospace font, serrated top/bottom edges via CSS gradient
  - Sections: header (KINDO + timestamp), `✓ APPROVED` + transaction ID, trip details, student/parent, payment (masked card `**** **** **** XXXX`), total paid
  - Card masked using `card_last_four` from `PaymentDetailResponse` — full number never displayed
- Updated `App.tsx` to store `PaymentDetailResponse` in state on success and pass it to `PaymentReceipt`
- Replaced the plain success screen with `PaymentReceipt`
- Production build passed

---

### Prompt 50
> "show a success toast on the top right to indicate the payment has been confirmed"

**AI actions:**
- Added `"success"` type to `Toast.tsx` with green colour variant (`bg-green-50 / border-green-300 / text-green-800`)
- Updated `ToastState` type in `App.tsx` to include `"success"`
- Set toast to `{ message: "Payment confirmed!", type: "success" }` when polling detects success
- Rendered `<Toast>` alongside `<PaymentReceipt>` on the success screen

---

### Prompt 51
> "are the unit tests up to date?"

**AI analysis and actions:**
- Found 3 gaps: missing cardholder validation test, no Toast tests, no PaymentReceipt tests
- Fixed `PaymentForm.test.tsx`: added `userEvent.clear()` on the pre-filled cardholder field before testing blank-submit, then asserts all 4 validation errors including `"Enter the cardholder name."`
- Created `Toast.test.tsx` (6 tests): null renders nothing, message text, all three colour variants, dismiss callback
- Created `PaymentReceipt.test.tsx` (7 tests): trip/location, names, masked card, transaction ID, null transaction ID, total, back button
- All 29 tests passing across 5 test files

---

### Prompt 52
> "redo the readme file for the front end, keep it simple, include the assumptions and constraints. Also include the screen flows descriptions and placeholder for the screenshots. Also update the AI log file"

**AI actions:**
- Replaced boilerplate Vite README with a proper `frontend/README.md` covering: tech stack, getting started, env vars, screen flow diagram, per-screen descriptions with screenshot placeholders, error handling table, assumptions & constraints, deployment URL
- Updated `AI_LOG.md` with all frontend session entries (Prompts 36–52)

---

### Prompt 53
> "for the backend, add a new endpoint to list all payments. Keep the docs up to date"

**AI actions:**
- Added `list_all()` to `PaymentRepository` using `select(Payment).order_by(created_at.desc())`
- Added `list_payments()` to `PaymentService` delegating to the repository
- Added `PaymentListResponse` schema with `payments: list[PaymentDetailResponse]` and `total: int`
- Exported `PaymentListResponse` from `app/schemas/__init__.py`
- Added `GET /api/v1/payments` endpoint to `app/routers/payments.py` returning `PaymentListResponse`
- Updated `backend/README.md` payments table with the new endpoint

---

### Prompt 54
> "update the unit and integration tests, as well as the readme file and the ai log"

**AI actions:**
- Added `TestListPayments` class to `tests/test_payment_service.py` with 2 unit tests: returns all payments, returns empty list
- Added 2 integration tests to `tests/test_integration.py`: `GET /api/v1/payments` returns empty list with correct shape; returns all payments with correct total
- Updated test count in `backend/README.md` from 25 to 28 (15 unit, 13 integration)
- Updated `AI_LOG.md` (this entry)

