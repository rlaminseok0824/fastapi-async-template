from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.db import DBSessionDep
from app.core.security import create_access_token
from app.core.settings import settings
from app.crud.users import authenticate_user, get_user_by_email
from app.schemas.auth import Token

router = APIRouter()

@router.post("/login")
async def login_access_token(db_session: DBSessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await authenticate_user(db_session, form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(
            user.email, expires_delta=access_token_expires
        )
    )