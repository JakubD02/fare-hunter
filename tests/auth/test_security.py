from app.core.security import create_refresh_token, verify_password
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService


def _user_service(db):
    return UserService(users=UserRepository(db))


def _auth_service(db):
    return AuthService(users=_user_service(db))


def test_password_is_properly_hashed_in_db(db, registered_user):
    """Check, if password isn't saved as plaintext and properly is verified"""
    user_in_db = _user_service(db).get_by_email(registered_user["email"])

    assert user_in_db is not None
    assert user_in_db.password_hash != registered_user["password"]
    assert verify_password(registered_user["password"], user_in_db.password_hash) is True


def test_refresh_token_for_inactive_user(db, registered_user):
    """An inactive user shouldn't be able to renew the access token"""
    user = _user_service(db).get_by_email(registered_user["email"])
    user.is_active = False
    db.commit()

    refresh_token = create_refresh_token(email=user.email, user_id=str(user.id))

    assert _auth_service(db).refresh_access_token(refresh_token) is None
