from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.api.auth import CurrentUser
from app.api.v1.dependencies import AuthServiceDep, UserServiceDep
from app.api.v1.schemas.token import AccessToken, RefreshRequest, TokenPair
from app.api.v1.schemas.user import UserCreate, UserRead
from app.core.security import (
    create_access_token,
    create_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])

form_data_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/token", response_model=TokenPair)
def login(service: AuthServiceDep, form: form_data_dependency):
    user = service.authenticate(form.username, form.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong login or password!")

    return TokenPair(
        access_token=create_access_token(email=user.email, user_id=user.id),
        refresh_token=create_refresh_token(email=user.email, user_id=user.id),
    )


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
def register(user_in: UserCreate, service: UserServiceDep):
    user = service.register(user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    return user


@router.post("/refresh", response_model=AccessToken)
def refresh(service: AuthServiceDep, body: RefreshRequest):
    access_token = service.refresh_access_token(body.refresh_token)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return AccessToken(access_token=access_token)


@router.get("/me", response_model=UserRead)
def read_me(user: CurrentUser):
    return user
