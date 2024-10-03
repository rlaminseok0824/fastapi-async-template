from typing import Annotated
from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import ValidationError

from app.api.dependencies.db import DBSessionDep
from app.core.security import decode_jwt
from app.crud.users import get_user_by_email
from app.models.user import User
from app.schemas.auth import TokenPayload


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/login")


TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(db_session: DBSessionDep,token : TokenDep) -> User:
    try:
        payload = decode_jwt(token)
        
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await get_user_by_email(db_session, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]

def get_current_active_superuser(current_user: CurrentUserDep) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

