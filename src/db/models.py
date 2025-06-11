import uuid
from datetime import datetime

from fastapi import Depends
from sqlmodel import Field, ForeignKey, SQLModel
from src.schemes.transaction import TransactionBase
from src.schemes.user import UserBase


class User(UserBase, table=True):
    __tablename__ = 'users'  # type: ignore
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)
    hashed_password: str
    rank: int = 1020
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={'onupdate': datetime.now}
    )


class Token(SQLModel, table=True):
    __tablename__ = 'tokens'  # type: ignore
    cg_id: str = Field(primary_key=True)
    symbol: str
    name: str


class Transaction(TransactionBase, table=True):
    __tablename__ = 'transactions'  # type: ignore
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID | None = Field(default=None, index=True, foreign_key='users.uid')
