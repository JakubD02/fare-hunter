# 🛫 Fare Hunter

[![Tests](https://github.com/JakubD02/fare-hunter/actions/workflows/tests.yml/badge.svg)](https://github.com/JakubD02/fare-hunter/actions/workflows/tests.yml)

A FastAPI-based flight price tracker with price alerts and email notifications. Track flight routes, set price thresholds, and get notified when deals appear.

---

## 🎯 Features

- ✅ **User authentication**: JWT registration, login and refresh tokens
- ✅ **Flight routes**: create and manage tracked routes (origin → destination)
- ✅ **Price tracking**: background Celery job fetches prices via SerpAPI (Google Flights)
- ✅ **Price alerts**: set a threshold and get notified when the price drops below it
- ✅ **Currency conversion**: alerts can be expressed in different currencies
- ✅ **Statistics**: price statistics per route (`/routes/{route_id}/stats`)
- ✅ **Email notifications**: SendGrid for alert confirmations and price-drop emails
- ✅ **Celery Beat**: scheduled price fetch every 8 hours
- ✅ **Docker Compose**: containerized setup for app, worker, beat, database and Redis

---

## 🏗️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Web framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Validation & settings | Pydantic v2, pydantic-settings |
| Database | PostgreSQL (SQLite for local default) |
| Migrations | Alembic |
| Cache & broker | Redis |
| Task queue & scheduler | Celery 5 + Celery Beat |
| Flight data | SerpAPI |
| Email | SendGrid |
| Auth | JWT (PyJWT), passlib |
| Testing | pytest, pytest-asyncio |
| Type checking | mypy |
| Linting & formatting | Ruff |
| Package manager | uv |
| Containerization | Docker, Docker Compose |

---

## 📋 Project Structure

```
fare-hunter/
├── app/
│   ├── api/
│   │   ├── auth.py                    # Auth dependencies (CurrentUser)
│   │   └── v1/
│   │       ├── endpoints/routers/     # FastAPI routers
│   │       │   ├── alerts.py
│   │       │   ├── auth.py
│   │       │   ├── currency.py
│   │       │   ├── reference.py       # airports, airlines
│   │       │   ├── routes.py
│   │       │   └── statistics.py
│   │       └── schemas/               # Pydantic request/response models
│   │           ├── airline.py
│   │           ├── airport.py
│   │           ├── currency.py
│   │           ├── flight_price.py
│   │           ├── price_alert.py
│   │           ├── route.py
│   │           ├── token.py
│   │           └── user.py
│   ├── core/
│   │   ├── config.py                  # Settings loaded from environment (.env)
│   │   ├── constants.py               # Domain constants as frozen Pydantic models
│   │   ├── database.py                # Engine, session, get_db
│   │   ├── exceptions.py
│   │   └── security.py                # JWT and password helpers
│   ├── enums/
│   │   └── currency.py
│   ├── models/                        # SQLAlchemy models
│   │   ├── airline.py
│   │   ├── airport.py
│   │   ├── base.py
│   │   ├── flight_price.py
│   │   ├── price_alert.py
│   │   ├── route.py
│   │   └── user.py
│   ├── repositories/                  # Data access layer
│   │   ├── airline_repository.py
│   │   ├── airport_repository.py
│   │   ├── alert_repository.py
│   │   ├── flight_price_repository.py
│   │   ├── route_repository.py
│   │   └── user_repository.py
│   ├── services/                      # Business logic
│   │   ├── alert_service.py
│   │   ├── auth_service.py
│   │   ├── currency.py
│   │   ├── flight_price_provider.py   # Provider interface
│   │   ├── flight_price_service.py
│   │   ├── reference_service.py
│   │   ├── route_service.py
│   │   ├── serpapi_mock_client.py     # Mock SerpAPI client
│   │   └── user_service.py
│   ├── tasks/                         # Celery tasks
│   │   ├── email_tasks.py
│   │   └── price_tasks.py
│   ├── celery_app.py
│   └── main.py                        # FastAPI app entry point
├── alembic/                           # Database migrations
│   ├── env.py
│   └── versions/
├── data/
│   ├── airlines.json                  # Seed data
│   └── airports.json
├── scripts/
│   ├── init_db.py                     # Database initialization
│   └── seed_data.py                   # Loads data/*.json
├── tests/
│   ├── auth/                          # Login, registration, security
│   ├── routes/                        # Routes, airlines, airports, alerts, statistics
│   ├── tasks/                         # Celery tasks
│   ├── mocks/                         # Fake SerpAPI responses
│   ├── conftest.py
│   └── test_health.py
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml                     # Dependencies (managed by uv)
├── uv.lock
├── pytest.ini
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose, or
- Python 3.12+, [uv](https://docs.astral.sh/uv/), PostgreSQL 15+ and Redis 7+ for local development

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

### 2a. Run with Docker

```bash
docker-compose up -d --build
docker-compose logs app | tail -30
```

### 2b. Run locally

```bash
uv sync
uv run alembic upgrade head
uv run python scripts/init_db.py    # TODO: check the exact command for seeding
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

> TODO: verify paths against the routers in `app/api/v1/endpoints/routers/`. Routes below come from the previous README and the tests.

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/token` | Login, get access and refresh tokens |
| GET | `/auth/me` | Current user (auth required) |

### Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/routes/` | List the user's routes (auth required) |
| POST | `/routes/` | Create a route (auth required) |
| GET | `/routes/{route_id}` | Route details (auth required) |
| PATCH | `/routes/{route_id}` | Update a route (auth required) |
| DELETE | `/routes/{route_id}` | Delete a route (auth required) |
| GET | `/routes/{route_id}/stats` | Price statistics for a route (auth required) |

**Create route request:**

```json
{
  "origin_id": 1,
  "destination_id": 2,
  "departure_date": "2026-12-25",
  "return_date": "2026-12-31"
}
```

Use airport `id` values from `/airports`, not IATA codes.

### Price alerts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{route_id}/alert` | Get the alert for a route (auth required) |
| PUT | `/{route_id}/alert` | Create or update the alert (auth required) |
| DELETE | `/{route_id}/alert` | Delete the alert (auth required) |

**Create or update alert request:**

```json
{
  "threshold_price": 500,
  "is_active": true
}
```

### Reference data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/airports` | List airports |
| GET | `/airlines` | List airlines |

> TODO: add the endpoints from `currency.py`.

---

## ⚙️ Configuration

Environment variables are loaded from `.env` by `app/core/config.py`:

```bash
# Database
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/fare_hunter

# Redis & Celery
REDIS_URL=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# SerpAPI
SERPAPI_KEY=your-serpapi-key
SERPAPI_URL=https://serpapi.com/api

# SendGrid
SENDGRID_API_KEY=SG.xxxxxxxx
FROM_EMAIL=noreply@farehunter.app
APP_URL=http://localhost:8000

# App
APP_ENV=development
LOG_LEVEL=DEBUG
```

Fixed domain limits (name lengths, IATA/ICAO code lengths, password limits, etc.) are **not** environment variables. They live in `app/core/constants.py`:

```python
from app.core.constants import airline_config, user_config

airline_config.iata_code_length  # 2
user_config.password_max_length  # 72
```

---

## 🔄 How It Works

### 1. A user creates a route

- The route is saved in the database.
- A Celery task `fetch_prices_for_route` is queued.
- The worker calls SerpAPI and saves the results as `FlightPrice` records.

### 2. A user sets a price alert

- The alert is created or updated.
- A confirmation email task is queued and the worker sends it through SendGrid.

### 3. Celery Beat runs every 8 hours

1. `fetch_all_prices_periodic` runs.
2. Prices are fetched for routes with active alerts.
3. If a price is below the threshold, a price-drop email task is queued.

---

## 🧪 Testing

```bash
uv sync
uv run pytest                          # all tests
uv run pytest tests/auth -v            # one directory
uv run pytest --cov=app tests/         # with coverage
```

---

## 🔍 Code Quality

```bash
uv run mypy app                        # type checking
uv run ruff check .                    # linting
uv run ruff check . --fix              # auto-fix lint issues
uv run ruff format .                   # formatting
```

CI runs the tests and checks defined in `.github/workflows/`.

---

## 🐳 Docker Commands

```bash
docker-compose up -d                   # start all services
docker-compose down                    # stop
docker-compose down -v                 # stop and remove volumes
docker-compose build                   # rebuild images
docker-compose logs app                # API logs
docker-compose logs worker             # Celery worker logs
docker-compose logs beat               # Celery Beat logs
docker-compose exec db psql -U postgres -d fare_hunter
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

- **Passwords** are hashed with bcrypt (passlib).
- **JWT**: HS256, 15-minute access tokens, 7-day refresh tokens.
- **Database access** goes through SQLAlchemy ORM.
- **Input validation** uses Pydantic v2 models.
- **Static security checks** run in CI (Bandit).

---

## 🚧 Roadmap

- [x] JWT authentication
- [x] Route CRUD
- [x] Airport and airline reference data
- [x] Price alerts
- [x] Currency conversion for alerts
- [x] Route statistics
- [x] Email notifications (SendGrid)
- [x] Celery background jobs
- [x] Docker Compose setup
- [x] Repository layer and Alembic migrations
- [ ] Advanced analytics (price trends, best time to buy)
- [ ] Multiple alert types (availability, schedule changes)
- [ ] Deployment to Heroku/AWS

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes
4. Push the branch and open a Pull Request

---

**Happy flight hunting! 🛫✈️**
