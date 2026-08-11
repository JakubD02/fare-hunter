from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from app.database import get_db
from app.config import settings


oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identity cannot be verified",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise credentials_exception

        return {"username": username, "id": user_id}
    except JWTError:
        raise credentials_exception

CurrentUser = Annotated[dict, Depends(get_current_user)]

def create_access_token(username: str, user_id: int, expires_delta: timedelta | None = None) -> str:
    encode = {'sub': username, 'id': user_id}
    if expires_delta:
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    encode.update({'exp': expires})
    return jwt.encode(encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
