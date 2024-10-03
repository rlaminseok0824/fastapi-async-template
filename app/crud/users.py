from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import DatabaseError

from app.core.security import verify_password
from app.models.user import User as UserDBModel
from app.schemas.user import UserCreate, User
from sqlalchemy.future import select


async def authenticate_user(db_session: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db_session, email)
    if not user:
        return False
    # if not verify_password(password,user.hashed_password):
    #     return False
    return user


async def create_user(*, session: AsyncSession, user_create: UserCreate) -> User:
    user = UserDBModel(**user_create.dict())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user(db_session: AsyncSession, user_id: int):
    user = (await db_session.scalars(select(UserDBModel).where(UserDBModel.id == user_id))).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_user_by_email(db_session: AsyncSession, email: str):
    return (await db_session.scalars(select(UserDBModel).where(UserDBModel.email == email))).first()
