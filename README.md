# 🛫 Fare Hunter

[![Tests](https://github.com/JakubD02/fare-hunter/actions/workflows/tests.yml/badge.svg)](https://github.com/JakubD02/fare-hunter/actions/workflows/tests.yml)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![code style: ruff](https://img.shields.io/badge/code%20style-ruff-261230.svg)](https://github.com/astral-sh/ruff)
[![types: mypy](https://img.shields.io/badge/types-mypy-blue.svg)](https://mypy-lang.org/)

A FastAPI flight price tracker with price alerts and email notifications. Track routes, set a price threshold, and get an email when the price drops below it.

---

## 🎯 Features

- ✅ **User authentication**: JWT registration, login and refresh tokens
- ✅ **Flight routes**: create and manage tracked routes (origin → destination), each in its own currency (PLN, EUR, USD, GBP)
- ✅ **Price tracking**: background Celery job fetches prices via SerpAPI (Google Flights)
- ✅ **Price alerts**: set a threshold and get notified when the price drops below it, with a 24h cooldown
- ✅ **Statistics & history**: min / max / average price per route and paginated price history
- ✅ **Currency conversion**: `/currency/convert` endpoint with live exchange rates
- ✅ **Email notifications**: SendGrid for alert confirmations and price-drop emails
- ✅ **Celery Beat**: scheduled price fetch every 8 hours, with retries on SerpAPI rate limits and 5xx errors
- ✅ **Docker Compose**: API, worker, beat, PostgreSQL and Redis, started in the right order via healthchecks

---

## 🏗️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Web framework | FastAPI |
| ORM | SQLAlchemy 2.1 |
| Validation & settings | Pydantic v2, pydantic-settings |
| Database | PostgreSQL |
| Migrations | Alembic |
| Cache & broker | Redis |
| Task queue & scheduler | Celery 5 + Celery Beat |
| Flight data | SerpAPI (Google Flights) |
| Email | SendGrid |
| Auth | JWT (PyJWT), bcrypt |
| Testing | pytest |
| Type checking | mypy |
| Linting & formatting | Ruff |
| Security scanning | Bandit, pip-audit, Gitleaks |
| Package manager | uv |
| Containerization | Docker, Docker Compose |

---

## 📋 Project Structure

```
fare-hunter/
├── .github/workflows/
│   └── tests.yml                       # CI: tests, Ruff, mypy, Alembic, Bandit, pip-audit, Gitleaks
├── app/
│   ├── api/
│   │   ├── auth.py                     # CurrentUser dependency (JWT → User)
│   │   └── v1/
│   │       ├── dependencies.py         # DbSession, PaginationDep, *ServiceDep
│   │       ├── endpoints/routers/      # FastAPI routers
│   │       │   ├── alerts.py
│   │       │   ├── auth.py
│   │       │   ├── currency.py
│   │       │   ├── reference.py        # airports, airlines
│   │       │   ├── routes.py
│   │       │   └── statistics.py       # stats, price history
│   │       └── schemas/                # Pydantic request/response models
│   ├── core/
│   │   ├── config.py                   # Settings from .env and domain limits
│   │   ├── database.py                 # Engine, SessionLocal, get_db
│   │   ├── exceptions.py
│   │   └── security.py                 # JWT and password hashing
│   ├── enums/
│   │   └── currency.py
│   ├── models/                         # SQLAlchemy models
│   ├── repositories/                   # Data access layer
│   │   ├── base_repository.py          # Generic BaseRepository[ModelT]
│   │   ├── airline_repository.py
│   │   ├── airport_repository.py
│   │   ├── alert_repository.py
│   │   ├── flight_price_repository.py
│   │   ├── route_repository.py
│   │   └── user_repository.py
│   ├── services/                       # Business logic and external APIs
│   │   ├── factories.py                # build_*_service(db), shared by API and tasks
│   │   ├── alert_rules.py              # Price alert decision rules and cooldown
│   │   ├── alert_service.py
│   │   ├── auth_service.py
│   │   ├── currency.py
│   │   ├── email_service.py
│   │   ├── flight_price_provider.py    # FlightPriceProvider protocol
│   │   ├── flight_price_service.py
│   │   ├── reference_service.py
│   │   ├── route_service.py
│   │   ├── serpapi_mock_client.py      # Mock SerpAPI client (dev/testing)
│   │   ├── serpapi_provider.py         # SerpApiFlightProvider (Google Flights)
│   │   └── user_service.py
│   ├── tasks/                          # Celery tasks
│   │   ├── email_tasks.py
│   │   └── price_tasks.py
│   ├── celery_app.py
│   └── main.py                         # FastAPI app entry point
├── alembic/                            # Database migrations
│   ├── env.py
│   └── versions/
├── data/
│   ├── airlines.json                   # Seed data
│   └── airports.json
├── scripts/
│   ├── init_db.py                      # Database initialization
│   ├── seed_data.py                    # Loads data/*.json
│   ├── test_sendgrid.py                # Manual SendGrid smoke test
│   └── test_serpapi.py                 # Manual SerpAPI smoke test
├── tests/
│   ├── conftest.py
│   ├── mocks/
│   │   └── serpapi_fake.py             # Fake SerpAPI responses
│   ├── unit/
│   │   ├── core/                       # JWT and password helpers
│   │   └── schemas/                    # Pydantic schema validation
│   └── integration/
│       ├── auth/                       # Login, registration
│       ├── routes/                     # Airlines, airports, alerts, routes, statistics
│       ├── tasks/                      # Celery price task
│       └── test_health.py
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml                      # Dependencies and tool config (uv, Ruff, mypy, Bandit)
└── uv.lock
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose, or
- Python 3.12+, [uv](https://docs.astral.sh/uv/), PostgreSQL and Redis for local development

### 1. Clone and configure

```bash
git clone https://github.com/JakubD02/fare-hunter.git
cd fare-hunter

cp .env.example .env
```

Fill in `.env` (see [Configuration](#️-configuration)). To generate a JWT secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2a. Run with Docker (recommended)

```bash
docker compose up --build
```

Compose waits for PostgreSQL and Redis to be healthy, runs the Alembic migrations, loads the seed data and starts the API, the Celery worker and Celery Beat.

### 2b. Run locally

```bash
uv sync
uv run alembic upgrade head
uv run python -m scripts.init_db
uv run uvicorn app.main:app --reload
```

### 3. Try the API

Swagger UI: http://localhost:8000/docs

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"first_name": "John", "email": "john@example.com", "password": "SecurePass123!"}'

# Login
curl -X POST http://localhost:8000/auth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=john@example.com&password=SecurePass123!'

# Current user
curl http://localhost:8000/auth/me -H "Authorization: Bearer $TOKEN"

# Reference data (no auth)
curl http://localhost:8000/airports
curl http://localhost:8000/airlines
```

---

## 📱 API Endpoints

List endpoints accept `limit` and `offset` query parameters for pagination.

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/token` | Login, get access and refresh tokens |
| POST | `/auth/refresh` | Get a new access token from a refresh token |
| GET | `/auth/me` | Current user |

### Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/routes/` | List the user's routes |
| POST | `/routes/` | Create a route and queue the first price fetch |
| GET | `/routes/{route_id}` | Route details |
| PATCH | `/routes/{route_id}` | Update a route |
| DELETE | `/routes/{route_id}` | Delete a route |

**Create route request:**

```json
{
  "origin_id": "6f1c2a3e-...",
  "destination_id": "9b7d4e1f-...",
  "departure_date": "2026-12-25",
  "return_date": "2026-12-31",
  "currency": "PLN"
}
```

`origin_id` and `destination_id` are airport `id` values (UUIDs) from `/airports`, not IATA codes. `return_date` is optional (one-way flight), `currency` defaults to `PLN`.

### Price alerts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/routes/{route_id}/alert` | Get the alert for a route |
| PUT | `/routes/{route_id}/alert` | Create or update the alert |
| DELETE | `/routes/{route_id}/alert` | Delete the alert |

**Create or update alert request:**

```json
{
  "threshold_price": 500,
  "is_active": true
}
```

The threshold is expressed in the route's currency.

### Statistics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/routes/{route_id}/stats` | Min / max / average price from the last 30 days |
| GET | `/routes/{route_id}/history` | Paginated price history, newest first |

### Reference data & utilities

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/airports` | List airports |
| GET | `/airlines` | List airlines |
| GET | `/currency/convert?amount=100&base=USD&quote=PLN` | Convert an amount between currencies |
| GET | `/health` | Health check |


---

## ⚙️ Configuration

Environment variables are loaded from `.env` by `app/core/config.py`:

```bash
# Database
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5434/fare_hunter

# Redis & Celery
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# SerpAPI
SERPAPI_KEY=your-serpapi-key
SERPAPI_URL=https://serpapi.com

# SendGrid
SENDGRID_API_KEY=SG.xxxxxxxx
FROM_EMAIL=noreply@farehunter.app
APP_URL=http://localhost:8000

# App
APP_ENV=development
LOG_LEVEL=DEBUG
```

The values above point to the services exposed by Docker Compose (PostgreSQL on port `5434`, Redis on `6379`), so you can run the API locally against the containers. Inside Compose, `DATABASE_URL` and `REDIS_URL` are overridden to use the service names (`db`, `redis`).

Fixed domain limits (name lengths, IATA/ICAO code lengths, password limits, etc.) are **not** environment variables. They are defined as frozen config models in `app/core/config.py`:

```python
from app.core.config import settings

settings.airline.iata_code_length  # 2
settings.user_config.password_max_length  # 72
```

---

## 🔄 How It Works

### 1. A user creates a route

- The route is saved in the database.
- `fetch_prices_for_route` is queued immediately, so the first price appears without waiting for the schedule.

### 2. A user sets a price alert

- `PUT /routes/{route_id}/alert` creates or updates the alert.
- `send_alert_confirmation_email_task` is queued and the worker sends a confirmation email.

### 3. Celery Beat runs every 8 hours (00:00, 08:00, 16:00 Warsaw time)

1. `fetch_all_prices_periodic` queues a `fetch_prices_for_route` task for each active route with a future departure date.
2. Each task fetches offers from SerpAPI and saves the cheapest one as a `FlightPrice`. Rate limits (429) and server errors (5xx) are retried with exponential backoff.
3. If the price is below the alert threshold and the alert is not in its 24h cooldown, the price is committed first and then `send_price_drop_email_task` is queued.
4. The email task checks the cooldown again (so duplicate tasks don't send duplicate emails), sends the email and only then sets `last_notified_at`. If sending fails after all retries, the alert stays un-notified and the next run tries again.

---

## 🧪 Testing

```bash
uv run pytest                          # all tests
uv run pytest tests/unit               # unit tests only
uv run pytest tests/integration -v     # integration tests only
uv run pytest --cov=app                # with coverage
```

Live smoke tests (real API calls, use your keys):

```bash
uv run python -m scripts.test_serpapi                       # SerpAPI
uv run python -m scripts.test_sendgrid you@example.com      # SendGrid
```

---

## 🔍 Code Quality & Security

```bash
uv run ruff check .                    # linting
uv run ruff check . --fix              # auto-fix lint issues
uv run ruff format .                   # formatting
uv run mypy app                        # type checking
uvx bandit -r app                      # static security analysis
uv run pip-audit                       # known vulnerabilities in dependencies
```

All of the above run in CI on every push and pull request (`.github/workflows/tests.yml`), together with Alembic migration checks and a Gitleaks secret scan of the full git history.

---

## 🐳 Docker Commands

```bash
docker compose up --build              # build and start all services
docker compose up -d                   # start in the background
docker compose down                    # stop
docker compose down -v                 # stop and remove volumes (database data)
docker compose up --build -V           # rebuild after changing dependencies
docker compose logs -f app             # API logs
docker compose logs -f worker          # Celery worker logs
docker compose logs -f beat            # Celery Beat logs
docker compose exec db psql -U postgres -d fare_hunter
```

---

## ⏱️ Running Celery Locally

Redis must be running. Start the worker and beat in separate terminals:

```bash
uv run celery -A app.celery_app worker --loglevel=info --pool=solo
uv run celery -A app.celery_app beat --loglevel=info
```

`--pool=solo` is needed on macOS, where the default prefork pool fails with the current Celery version. Trigger the periodic fetch manually for testing:

```bash
uv run celery -A app.celery_app call app.tasks.price_tasks.fetch_all_prices_periodic
```

---

## 🗄️ Database Migrations

Schema changes go through Alembic:

```bash
uv run alembic revision --autogenerate -m "describe the change"
uv run alembic upgrade head
uv run alembic downgrade -1
```

---

## 🔐 Security

- **Passwords** are hashed with bcrypt.
- **JWT**: HS256, 15-minute access tokens, 7-day refresh tokens, with a token type check (access vs refresh).
- **Ownership checks**: every user-facing query is scoped to the current user, so users can't read or modify other users' routes and alerts.
- **Database access** goes through the SQLAlchemy ORM with bound parameters (no raw SQL string building).
- **Input validation** uses Pydantic v2 models.
- **Secrets** live in `.env`, which is git-ignored.
- **CI security checks**: Bandit (static analysis), pip-audit (dependency CVEs), Gitleaks (secrets in git history).

---

## 🚧 Roadmap

- [x] JWT authentication
- [x] Route CRUD
- [x] Airport and airline reference data
- [x] Price alerts with cooldown
- [x] Route statistics and price history
- [x] Email notifications (SendGrid)
- [x] Celery background jobs with retries
- [x] Docker Compose setup with healthchecks
- [x] Repository layer with generic `BaseRepository` and Alembic migrations
- [x] Service factories shared by the API and Celery tasks
- [x] SerpAPI flight price provider
- [x] CI with tests, type checking and security scanning
- [ ] Advanced analytics (price trends, best time to buy)
- [ ] Multiple alert types (availability, schedule changes)
- [ ] Deployment

---


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes
4. Push the branch and open a Pull Request

---

**Happy flight hunting! 🛫✈️**
