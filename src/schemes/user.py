import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(primary_key=True)
    email: str = Field(index=True)


class UserCreate(UserBase):
    password: str


class UserPublic(UserBase):
    uid: uuid.UUID
    created_at: datetime
    updated_at: datetime
    hashed_password: str


class UserUpdate(SQLModel):
    username: str | None = None
    email: str | None = None
    old_password: str | None = None
    new_password: str | None = None


class UserLogin(UserBase):
    email: None = None
    password: str
