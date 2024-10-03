from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.future import select


from app.api.dependencies.auth import CurrentUserDep, get_current_active_superuser
from app.api.dependencies.db import DBSessionDep
from app.core.security import get_password_hash
from app.crud.users import create_user, get_user_by_email
from app.schemas.user import *
from app.models.user import User as UserDBModel

router = APIRouter()

@router.get(
        "/",
        dependencies=[Depends(get_current_active_superuser)],
        response_model=UserList
)
async def read_users(session: DBSessionDep,skip: int = 0, limit: int = 100) -> Any:
    count_statement = select(func.count()).select_from(UserDBModel)
    count = await session.scalar(count_statement)

    statement = select(UserDBModel).offset(skip).limit(limit)
    users = (await session.scalars(statement)).all()

    return UserList(users=users, count=count)

@router.post("/",dependencies=[Depends(get_current_active_superuser)],response_model=User)
async def create_user(*,session: DBSessionDep, user_in: UserCreate) -> Any:
    user = get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user_create = UserCreate.validate(user_in)
    user_create.hashed_password = get_password_hash(user_in.hashed_password)
    user = create_user(session=session, user_create=user_in)


@router.patch("/me",response_model=User)
async def update_user_me(*,db_session: DBSessionDep, user_in : UserUpdateMe, curr_user: CurrentUserDep) -> Any:
    """
    Update current User
    """
    if user_in.email:
        existing_user = await get_user_by_email(db_session=db_session, email=user_in.email)
        if existing_user and existing_user.id != curr_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    
    user_data = user_in.dict(exclude_unset=True)
    for field in user_data:
        setattr(curr_user, field, user_data[field])
    db_session.add(curr_user)
    await db_session.commit()
    await db_session.refresh(curr_user)
    return curr_user


@router.get("/me",response_model=User)
async def read_user_me(curr_user: CurrentUserDep) -> Any:
    """
    Get current user
    """
    return curr_user


@router.post("/signup",response_model=User)
async def register_user(session: DBSessionDep, user_in: UserRegister) -> Any: 
    """
    Register a new user without admin privileges
    """

    user_create = UserCreate.validate(user_in)
    user_create.hashed_password = get_password_hash(user_in.hashed_password)
    user = await create_user(session=session, user_create=user_create)
    return user


