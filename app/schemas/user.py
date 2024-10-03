from typing import Optional
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    username: str
    slug: str
    email: str
    first_name: str
    last_name: str
    is_superuser: bool = False

class UserCreate(User):
    hashed_password: str

class UserUpdateMe(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]


class UserRegister(BaseModel):
    email: str
    slug: str
    username: str
    hashed_password: str
    first_name: str
    last_name: str

class UserList(BaseModel):
    users: list[User]
    count: int