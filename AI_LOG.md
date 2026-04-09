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
