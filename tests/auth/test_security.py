from app.services.auth_service import get_user_by_email, verify_password, refresh_access_token
from app.core.security import create_refresh_token

def test_password_is_properly_hashed_in_db(db, registered_user, user_data):
    """Check, if password isn't saved as plaintext and properly is verified"""
    user_in_db = get_user_by_email(db, email=registered_user["email"])

    assert user_in_db is not None
    assert user_in_db.password_hash != registered_user["password"]
    assert verify_password(registered_user["password"], user_in_db.password_hash) is True

def test_read_me_unauthorized_without_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_read_me_success(client, user_data, registered_user):
    login_res = client.post(
        "/auth/token",
        data={"username": user_data["email"], "password": user_data["password"]}
    )
    token = login_res.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]


def test_read_me_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token_123"}
    )
    assert response.status_code == 401

def test_refresh_token_for_inactive_user(db, registered_user):
    """An inacive user shouldn't be able to renew the access token"""
    user = get_user_by_email(db, registered_user["email"])
    user.is_active = False
    db.commit()

    refresh_token = create_refresh_token(email=user.email, user_id=user.id)
    
    new_token = refresh_access_token(db, refresh_token=refresh_token)
    assert new_token is None