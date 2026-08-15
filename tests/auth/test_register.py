

def test_register_creates_user(client, user_data):
    """Successful registration and user data without password"""
    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@gmail.com"
    assert data["first_name"] == "test"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_register_missing_field_returns_422(client):
    """Verify with missing fields"""
    response = client.post(
        "/auth/register",
        json={
            "email": "kuba@example.com",
        },
    )
    assert response.status_code == 422


def test_register_with_existing_email(client, user_data):
    """Verify, when email is an already registered"""
    client.post("/auth/register", json=user_data)

    response_second_user = client.post("/auth/register", json=user_data)

    assert response_second_user.status_code == 409
    assert response_second_user.json()["detail"] == "Email already registered"


def test_register_with_not_appropriate_email(client):
    """Adress email without @ sign"""
    response = client.post(
        "/auth/register",
        json={
            "email": "user",
            "password": "user321",
            "first_name": "user",
        },
    )

    assert response.status_code == 422


def test_register_with_empty_values(client):
    """Verify validation error with empty fields"""
    response = client.post(
        "/auth/register",
        json={
            "email": "",
            "password": "",
            "first_name": "",
        },
    )

    assert response.status_code == 422


def test_register_with_additional_field(client):
    """Verify behavior when unexpected fields are passed in the request"""
    response = client.post(
        "/auth/register",
        json={
            "email": "user@gmail.com",
            "password": "user1234",
            "first_name": "user",
            "is_protected": True,
        },
    )

    assert response.status_code == 201 # 422
