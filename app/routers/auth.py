from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from app.core.security import (
    CurrentUser,
    create_access_token,
    create_refresh_token,
)
from app.database import get_db
from app.schemas.token import TokenPair
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["auth"])

db_dependency = Annotated[Session, Depends(get_db)]
form_data_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/token", response_model=TokenPair)
async def login(db: db_dependency, form_data: form_data_dependency):
    user = authenticate_user(
        db=db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong login or password!"
        )

    return TokenPair(
        access_token=create_access_token(email=user.email, user_id=user.id),
        refresh_token=create_refresh_token(email=user.email, user_id=user.id),
    )


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def register(user_in: UserCreate, db: db_dependency):
    user = create_user(db=db, user_in=user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    return user


@router.get("/me", response_model=UserRead)
async def read_me(current_user: CurrentUser):
    return current_user
