import uuid
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)

pytestmark = pytest.mark.unit


def _decode(token: str) -> dict:
    """Decode a token without any extra checks, to inspect its claims"""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def test_password_hash_is_not_plaintext_and_verifies():
    hashed = hash_password("secret123")

    assert hashed != "secret123"
    assert verify_password("secret123", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_access_token_contains_access_type_and_user_id():
    user_id = str(uuid.uuid4())

    token = create_access_token(email="user@example.com", user_id=user_id)
    payload = _decode(token)

    assert payload["type"] == "access"
    assert payload["user_id"] == user_id


def test_refresh_token_lives_for_configured_days():
    token = create_refresh_token(email="user@example.com", user_id=str(uuid.uuid4()))
    payload = _decode(token)

    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    lifetime = expires_at - datetime.now(timezone.utc)

    assert lifetime > timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS - 1)


def test_decode_refresh_rejects_expired_token():
    expired_payload = {
        "sub": "user@example.com",
        "user_id": str(uuid.uuid4()),
        "type": "refresh",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    token = jwt.encode(expired_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_refresh_token(token)
