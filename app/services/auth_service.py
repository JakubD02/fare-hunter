from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.name == username).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False

    return user
