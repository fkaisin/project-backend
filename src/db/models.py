import uuid
from datetime import datetime

from fastapi import Depends
from sqlmodel import Field, ForeignKey

from src.schemes.user import UserBase


class User(UserBase, table=True):
    __tablename__ = 'users'

    uid: uuid.UUID = Field(default_factory=uuid.uuid4)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={'onupdate': datetime.now}
    )
