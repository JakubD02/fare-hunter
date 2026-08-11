
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from app.core.security import create_access_token
from app.database import get_db
from app.services.auth_service import authenticate_user


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/token")
async def login_for_access_token(
    db: db_dependency,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(db=db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong login or password!"
        )

    access_token = create_access_token(username=user.username, user_id=user.id)

    return {"access_token": access_token, "token_type": "bearer"}