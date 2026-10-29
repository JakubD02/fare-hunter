from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError as JWTError
from starlette import status

from app.api.v1.dependencies import AuthServiceDep, DbSession
from app.core.security import decode_access_token
from app.models.user import User

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: DbSession, auth: AuthServiceDep) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identity cannot be verified",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
    except JWTError:
        raise credentials_exception

    user_id = payload.get("user_id")
    if not user_id:
        raise credentials_exception

    user = auth.get_active_user(user_id)
    if user is None:
        raise credentials_exception

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
