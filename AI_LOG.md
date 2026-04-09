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
