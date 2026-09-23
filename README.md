# 🛫 Fare Hunter

A FastAPI-based flight price tracker with real-time alerts and email notifications. Track flight prices, set price thresholds, and get notified when deals appear.

---

## 🎯 Features

- ✅ **User Authentication** - JWT-based registration, login, refresh tokens
- ✅ **Flight Routes** - Create & manage tracked flight routes (origin → destination)
- ✅ **Price Tracking** - Async background job fetches flight prices via SerpAPI
- ✅ **Price Alerts** - Set thresholds; get notified when price drops below
- ✅ **Email Notifications** - SendGrid integration for alert confirmations & price drops
- ✅ **Celery Background Tasks** - Scheduled price fetches (3/day via Celery Beat)
- ✅ **Docker & Docker Compose** - Full containerized setup (app, worker, beat, postgres, redis)

---

## 🏗️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Web Framework** | FastAPI 0.104+ |
| **ORM** | SQLAlchemy 2.0 with Pydantic v2 |
| **Database** | PostgreSQL 15 |
| **Cache & Broker** | Redis 7 |
| **Task Queue** | Celery 5.3 |
| **Scheduler** | Celery Beat |
| **Email** | SendGrid API |
| **Flight Data** | SerpAPI (Google Flights scraper) |
| **Auth** | JWT (PyJWT) |
| **Validation** | Pydantic v2 |
| **Testing** | pytest + pytest-asyncio |
| **Containerization** | Docker & Docker Compose |
| **Linting** | Ruff |

---

## 📋 Project Structure

```
fare-hunter/
├── app/
│   ├── core/
│   │   ├── config.py           # Settings, env vars, Celery config
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── security.py         # JWT, password hashing, auth deps
│   ├── models/
│   │   ├── base.py             # DeclarativeBase for SQLAlchemy 2.0
│   │   ├── user.py             # User model (id, email, password, created_at)
│   │   ├── route.py            # Route (origin, destination, dates)
│   │   ├── flight_price.py     # FlightPrice (price, airline, currency)
│   │   ├── price_alert.py      # PriceAlert (threshold, is_active)
│   │   ├── airport.py          # Airport (iata_code, name, city, country)
│   │   └── airline.py          # Airline (iata_code, name)
│   ├── schemas/
│   │   ├── user.py             # UserCreate, UserRead
│   │   ├── route.py            # RouteCreate, RouteRead, RouteUpdate
│   │   ├── price_alert.py      # PriceAlertCreate, PriceAlertRead
│   │   ├── flight_price.py     # FlightPriceRead
│   │   ├── airport.py          # AirportRead
│   │   ├── airline.py          # AirlineRead
│   │   └── token.py            # TokenRead
│   ├── routers/
│   │   ├── auth.py             # POST /auth/register, /auth/token, /auth/me
│   │   ├── routes.py           # GET/POST/PATCH /routes/
│   │   ├── alerts.py           # GET/PUT/DELETE /{route_id}/alert
│   │   ├── reference.py        # GET /airports, /airlines
│   │   └── statistics.py       # GET /routes/{route_id}/stats (optional)
│   ├── services/
│   │   ├── auth_service.py     # User registration, password verification
│   │   ├── routes_service.py   # Route CRUD operations
│   │   ├── alert_service.py    # Alert upsert, removal
│   │   ├── email_service.py    # SendGrid email sending
│   │   ├── flight_price_service.py  # SerpAPI integration
│   │   └── reference_service.py     # Airport/airline queries
│   ├── tasks/
│   │   ├── price_tasks.py      # fetch_prices_for_route, fetch_all_prices_periodic
│   │   └── email_tasks.py      # send_alert_confirmation_email, send_price_drop_email
│   ├── database.py             # SQLAlchemy engine, SessionLocal, get_db
│   ├── celery_app.py           # Celery app initialization
│   ├── main.py                 # FastAPI app with lifespan
│   └── constants/              # Constants for models (max lengths, defaults)
├── init_db.py                  # Database initialization + seed data
├── docker-compose.yml          # 5 services: app, worker, beat, postgres, redis
├── Dockerfile                  # Multi-stage build
├── requirements.txt            # Python dependencies
├── alembic/                    # Database migrations (optional, using init_db.py instead)
├── tests/
│   ├── conftest.py             # pytest fixtures (db, client, test user)
│   ├── auth/                   # Auth endpoint tests
│   ├── routes/                 # Routes endpoint tests
│   ├── alerts/                 # Alerts endpoint tests
│   ├── statistics/             # Statistics endpoint tests
│   └── mocks/                  # Mock data for tests
├── .github/workflows/
│   └── tests.yml               # GitHub Actions CI/CD
├── .env.example                # Environment variables template
├── pytest.ini                  # pytest configuration
└── README.md                   # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.13+ (for local development)
- PostgreSQL 15+ (if running outside Docker)
- Redis 7+ (if running outside Docker)

### 1. Clone & Setup

```bash
git clone https://github.com/JakubD02/fare-hunter.git
cd fare-hunter

# Create .env from template
cp .env.example .env

# Edit .env with your keys:
# - SERPAPI_KEY (from https://serpapi.com)
# - SENDGRID_API_KEY (from https://sendgrid.com)
# - JWT_SECRET_KEY (generate: python -c "import secrets; print(secrets.token_urlsafe(32))")
```

### 2. Start Docker Containers

```bash
# Build images
docker-compose build

# Start all services (app, worker, beat, postgres, redis)
docker-compose up -d

# Wait 20 seconds for database to initialize
sleep 20

# Check logs
docker-compose logs app | tail -30
```

### 3. Test the API

```bash
# Register a user
curl -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "first_name": "John",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'

# Response:
# {
#   "id": "uuid",
#   "email": "john@example.com",
#   "first_name": "John",
#   "is_active": true,
#   "created_at": "2026-09-23T..."
# }

# Login & get token
curl -X POST http://localhost:8000/auth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=john@example.com&password=SecurePass123!'

# Response:
# {
#   "access_token": "eyJ...",
#   "refresh_token": "eyJ...",
#   "token_type": "bearer"
# }

# Save token
TOKEN="eyJ..."

# Get current user
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"

# List airports (no auth required)
curl -X GET http://localhost:8000/airports

# List airlines (no auth required)
curl -X GET http://localhost:8000/airlines
```

Open **Swagger UI**: http://localhost:8000/docs

---

## 📱 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/token` | Login, get access + refresh tokens |
| GET | `/auth/me` | Get current user (requires auth) |

### Routes (Flight Tracking)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/routes/` | List user's routes (requires auth) |
| POST | `/routes/` | Create new route (requires auth) |
| GET | `/routes/{route_id}` | Get route details (requires auth) |
| PATCH | `/routes/{route_id}` | Update route (requires auth) |
| DELETE | `/routes/{route_id}` | Delete route (requires auth) |

**Create Route Request:**
```json
{
  "origin_id": 1,
  "destination_id": 2,
  "departure_date": "2026-12-25",
  "return_date": "2026-12-31"
}
```

**Note:** Use airport `id` from `/airports` endpoint, not IATA codes.

### Price Alerts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{route_id}/alert` | Get alert for route (requires auth) |
| PUT | `/{route_id}/alert` | Create or update alert (requires auth) |
| DELETE | `/{route_id}/alert` | Delete alert (requires auth) |

**Create/Update Alert Request:**
```json
{
  "threshold_price": 500,
  "is_active": true
}
```

### Reference Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/airports` | List all airports |
| GET | `/airlines` | List all airlines |

**Airport Response:**
```json
[
  {
    "id": 1,
    "iata_code": "JFK",
    "name": "John F. Kennedy International",
    "city": "New York",
    "country": "United States",
    "country_code": "US"
  }
]
```

---

## ⚙️ Configuration

All settings are managed via environment variables in `.env`:

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

# Email (SendGrid)
SENDGRID_API_KEY=SG.xxxxxxxx
FROM_EMAIL=noreply@farehunter.app

# Flight Data (SerpAPI)
SERPAPI_KEY=your-serpapi-key

# App
APP_URL=http://localhost:8000
APP_ENV=development
LOG_LEVEL=DEBUG
```

---

## 🔄 How It Works

### 1. User Creates a Route

```bash
curl -X POST http://localhost:8000/routes/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "origin_id": 1,
    "destination_id": 2,
    "departure_date": "2026-12-25",
    "return_date": "2026-12-31"
  }'
```

**Behind the scenes:**
- ✅ Route created in DB
- ✅ Celery task `fetch_prices_for_route(route_id)` queued immediately
- Worker picks it up → calls SerpAPI → saves FlightPrice

### 2. User Sets a Price Alert

```bash
curl -X PUT http://localhost:8000/1/alert \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "threshold_price": 500,
    "is_active": true
  }'
```

**Behind the scenes:**
- ✅ Alert created/updated in DB
- ✅ Celery task `send_alert_confirmation_email_task` queued
- Worker sends confirmation email via SendGrid

### 3. Celery Beat Scheduler Runs Every 8 Hours

Every 8 hours (3 times/day), Celery Beat:
1. Triggers `fetch_all_prices_periodic` task
2. Worker fetches prices for all routes with active alerts
3. If price < threshold: `send_price_drop_email_task` queued
4. Worker sends notification email to user

---

## 🧪 Testing

Run tests locally:

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run specific test
pytest tests/auth/test_register.py -v

# Run with coverage
pytest --cov=app --cov-report=html
```

**Test Structure:**
- `tests/auth/` - Login, registration, JWT
- `tests/routes/` - Create, list, update, delete routes
- `tests/alerts/` - Alert CRUD

---

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v

# Rebuild images
docker-compose build

# View logs
docker-compose logs app          # FastAPI logs
docker-compose logs worker       # Celery worker logs
docker-compose logs beat         # Celery Beat logs
docker-compose logs db           # PostgreSQL logs

# Access database
docker-compose exec db psql -U postgres -d fare_hunter

# Query tables
docker-compose exec db psql -U postgres -d fare_hunter -c "SELECT * FROM airports;"
docker-compose exec db psql -U postgres -d fare_hunter -c "SELECT * FROM routes;"
docker-compose exec db psql -U postgres -d fare_hunter -c "SELECT * FROM price_alerts;"
```

---

## 🔐 Security

- **Passwords** - Hashed with bcrypt (via passlib)
- **JWT Tokens** - HS256 algorithm, 15-min expiry (access), 7-day expiry (refresh)
- **Database** - All models use SQLAlchemy ORM (SQL injection safe)
- **Validation** - Pydantic v2 models validate all input
- **CORS** - Can be enabled in `app/main.py` if needed

---

## 📊 Database Schema

### users
```sql
id (UUID, PK) | first_name | email (UNIQUE) | password_hash | is_active | created_at
```

### airports
```sql
id (INT, PK) | iata_code (UNIQUE) | name | city | country | country_code
```

### airlines
```sql
id (INT, PK) | iata_code (UNIQUE) | name
```

### routes
```sql
id (INT, PK) | user_id (FK→users) | origin_id (FK→airports) | destination_id (FK→airports) | 
departure_date | return_date | is_active | created_at
```

### flight_prices
```sql
id (INT, PK) | route_id (FK→routes) | airline_id (FK→airlines) | price | currency | 
departure_date | return_date | fetched_at
```

### price_alerts
```sql
id (INT, PK) | route_id (FK→routes, UNIQUE) | threshold_price | currency | is_active | last_notified_at
```

---

## 🚧 Roadmap

### Current (Sept 2026)
- [x] User authentication (JWT)
- [x] Route CRUD
- [x] Airport/airline reference data
- [x] Price alert system
- [x] Email notifications (SendGrid)
- [x] Celery background jobs
- [x] Docker containerization
- [x] Database initialization with seed data

### Next Phase
- [ ] Advanced analytics (price trends, best time to buy)
- [ ] Multiple alert types (price drop, availability, schedule changes)
- [ ] Deployment to Heroku/AWS

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit changes (`git commit -am 'Add my feature'`)
4. Push to branch (`git push origin feature/my-feature`)
5. Open a Pull Request


---

**Happy flight hunting! 🛫✈️**
