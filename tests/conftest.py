import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base
from app.models.airline import Airline
from app.models.airport import Airport
from scripts.data import AIRLINES_DATA, AIRPORTS_DATA

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
    origin = db.execute(select(Airport).where(Airport.iata_code == "WAW") ).scalar_one_or_none()
    destination = db.execute( select(Airport).where(Airport.iata_code == "JFK") ).scalar_one_or_none()

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
    assert response.status_code == 200, (
        f"Status: {response.status_code}, response: {response.text}"
)
    return response.json()


@pytest.fixture
def created_route(client, registered_user, db):
    """Create a route for the registered user"""
    from app.models.airport import Airport


    origin = db.execute(select(Airport).where(Airport.iata_code=="WAW")).scalar_one_or_none()
    destination = db.execute(select(Airport).where(Airport.iata_code=="JFK")).scalar_one_or_none()

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
