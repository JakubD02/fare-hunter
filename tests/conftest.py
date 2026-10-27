from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app
from app.models import Base
from app.models.airline import Airline
from app.models.airport import Airport
from app.models.route import Route
from data import AIRLINES_DATA, AIRPORTS_DATA

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Test database session"""
    Base.metadata.create_all(engine)
    session = TestSessionLocal()
    try:
        session.add_all(Airport(**data) for data in AIRPORTS_DATA)
        session.add_all(Airline(**data) for data in AIRLINES_DATA)
        session.commit()

        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def client(db):
    """FastAPI test client"""

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def other_user_data():
    return {
        "first_name": "other",
        "email": "other@gmail.com",
        "password": "other1234",
    }


@pytest.fixture
def user_data():
    return {
        "first_name": "test",
        "email": "test@gmail.com",
        "password": "test1234",
    }


@pytest.fixture
def other_user_route(client, other_registered_user, db):
    """Create a route for the other user"""
    origin = db.execute(select(Airport).where(Airport.iata_code == "WAW")).scalar_one_or_none()
    destination = db.execute(select(Airport).where(Airport.iata_code == "JFK")).scalar_one_or_none()

    if not origin or not destination:
        pytest.skip("Test airports not found in database")

    route_data = {
        "origin_id": origin.id,
        "destination_id": destination.id,
        "departure_date": "2026-12-29",
    }
    response = client.post(
        "/routes/",
        json=route_data,
        headers={"Authorization": f"Bearer {other_registered_user['token']}"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def registered_user(client, user_data):
    """register user in DB and return login data"""
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201

    token_response = client.post(
        "/auth/token",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    assert token_response.status_code == 200
    user_data["token"] = token_response.json()["access_token"]

    return user_data


@pytest.fixture
def other_registered_user(client, other_user_data):
    """Register second user"""
    response = client.post("/auth/register", json=other_user_data)
    assert response.status_code == 201
    token_response = client.post(
        "/auth/token",
        data={"username": other_user_data["email"], "password": other_user_data["password"]},
    )
    other_user_data["token"] = token_response.json()["access_token"]
    return other_user_data


@pytest.fixture
def created_route_model(db, created_route):
    return db.get(Route, created_route["id"])


@pytest.fixture
def airline(db):
    """Airline used by the tests. Assumes IATA code 'LO' exists in AIRLINES_DATA."""
    return db.execute(select(Airline).where(Airline.iata_code == "LO")).scalar_one()


@pytest.fixture
def alert_data():
    return {
        "threshold_price": 150.0,
        "currency": "EUR",
        "is_active": True,
    }


@pytest.fixture
def created_alert(client, registered_user, created_route, alert_data, db):
    """Create an alert for testing"""
    response = client.put(
        f"/routes/{created_route['id']}/alert",
        json=alert_data,
        headers={"Authorization": f"Bearer {registered_user['token']}"},
    )
    assert response.status_code == 200, f"Status: {response.status_code}, response: {response.text}"
    return response.json()


@pytest.fixture
def created_route(client, registered_user, db):
    """Create a route for the registered user"""
    from app.models.airport import Airport

    origin = db.execute(select(Airport).where(Airport.iata_code == "WAW")).scalar_one_or_none()
    destination = db.execute(select(Airport).where(Airport.iata_code == "JFK")).scalar_one_or_none()

    if not origin or not destination:
        pytest.skip("Test airpots doesn't found in database")

    route_data = {
        "origin_id": origin.id,
        "destination_id": destination.id,
        "departure_date": "2026-11-15",
    }

    response = client.post(
        "/routes/",
        json=route_data,
        headers={"Authorization": f"Bearer {registered_user['token']}"},
    )

    assert response.status_code == 201
    return response.json()


@pytest.fixture
def route_data(db):
    """Route creation data with actual airport IDs"""
    origin = db.execute(select(Airport).where(Airport.iata_code == "WAW")).scalar_one_or_none()
    destination = db.execute(select(Airport).where(Airport.iata_code == "JFK")).scalar_one_or_none()

    if not origin or not destination:
        pytest.skip("Test airports not found in database")

    return {
        "origin_id": origin.id,
        "destination_id": destination.id,
        "departure_date": "2026-12-25",
    }


@pytest.fixture
def update_route_data(db):
    airport = db.execute(select(Airport).where(Airport.iata_code == "LHR")).scalar_one()

    return {
        "destination_id": airport.id,
    }


@pytest.fixture
def price_history(client, registered_user, created_route, db):
    """Create price history for route"""
    from app.models.airline import Airline
    from app.models.flight_price import FlightPrice

    airline = db.execute(select(Airline)).scalars().first()
    assert airline is not None, "No airlines seeded in test DB"

    departure = date.fromisoformat(created_route["departure_date"])

    for i in range(5):
        db.add(
            FlightPrice(
                route_id=created_route["id"],
                airline_id=airline.id,
                price=100.0 + i * 10,
                currency="EUR",
                departure_date=departure,
                fetched_at=datetime.now(timezone.utc),
            )
        )
    db.commit()
    return created_route


@pytest.fixture
def other_user_price_history(client, other_registered_user, other_user_route, db):
    """Create price history for other user's route"""
    from app.models.airline import Airline
    from app.models.flight_price import FlightPrice

    airline = db.execute(select(Airline)).scalars().first()
    assert airline is not None, "No airlines seeded in test DB"

    departure = date.fromisoformat(other_user_route["departure_date"])

    for i in range(5):
        db.add(
            FlightPrice(
                route_id=other_user_route["id"],
                airline_id=airline.id,
                price=100.0 + i * 10,
                currency="EUR",
                departure_date=departure,
                fetched_at=datetime.now(timezone.utc),
            )
        )
    db.commit()
    return other_user_route


# @pytest.fixture(autouse=True)
# def no_celery_delay(monkeypatch):
#     """Don't send Celery tasks to the broker during tests"""
#     for task in (
#         fetch_prices_for_route,
#         send_alert_confirmation_email_task,
#         send_price_drop_email_task,
#     ):
#         monkeypatch.setattr(task, "delay", lambda *args, **kwargs: None)
