from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from app.api.auth import CurrentUser
from app.api.v1.schemas.token import AccessToken, RefreshRequest, TokenPair
from app.api.v1.schemas.user import UserCreate, UserRead
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
)
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])

db_dependency = Annotated[Session, Depends(get_db)]
form_data_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]


def _user_service(db: Session) -> UserService:
    return UserService(users=UserRepository(db))


def _auth_service(db: Session) -> AuthService:
    return AuthService(users=_user_service(db))


@router.post("/token", response_model=TokenPair)
def login(db: db_dependency, form: form_data_dependency):
    user = _auth_service(db).authenticate(form.username, form.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong login or password!")

    return TokenPair(
        access_token=create_access_token(email=user.email, user_id=user.id),
        refresh_token=create_refresh_token(email=user.email, user_id=user.id),
    )


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
def register(user_in: UserCreate, db: db_dependency):
    user = _user_service(db).register(user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    return user


@router.post("/refresh", response_model=AccessToken)
def refresh(db: db_dependency, body: RefreshRequest):
    access_token = _auth_service(db).refresh_access_token(body.refresh_token)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return AccessToken(access_token=access_token)


@router.get("/me", response_model=UserRead)
def read_me(user: CurrentUser):
    return user
