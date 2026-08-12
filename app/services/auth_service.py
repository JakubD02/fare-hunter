from uuid import UUID

from jose import JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    decode_refresh_token,
)
from app.models.user import User
from app.schemas.user import UserCreate

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)


def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    stmt = select(User).where(User.id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_email(db, email=username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_user(db: Session, user_in: UserCreate) -> User | None:
    user = get_user_by_email(db, email=user_in.email)
    if user:
        return None

    user = User(
        first_name=user_in.first_name,
        email=user_in.email,
        password=get_password_hash(user_in.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def refresh_access_token(db: Session, refresh_token: str) -> str | None:
    try:
        decoded_token = decode_refresh_token(refresh_token)
    except JWTError:
        return None

    user_id = decoded_token.get("user_id")
    if not user_id:
        return None

    user = get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        return None

    new_access_token = create_access_token(user.email, user.id)

    return new_access_token
