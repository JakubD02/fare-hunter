import pytest

def test_register_creates_user(client):
    '''Successfull registration and user data without password'''
    response = client.post(
        "/auth/register",
        json={
            "email": "test@gmail.com",
            "password": "test1234",
            "first_name": "test",
        }
    )

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
    """Missing fields"""
    response = client.post(
        "/auth/register",
        json={
            "email": "kuba@example.com",
        },
    )
    assert response.status_code == 422


