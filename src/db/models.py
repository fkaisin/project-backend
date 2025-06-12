import uuid
from datetime import datetime
from typing import Optional

from fastapi import Depends
from sqlmodel import Field, ForeignKey, Relationship, SQLModel
from src.schemes.transaction import TransactionBase
from src.schemes.user import UserBase


class User(UserBase, table=True):
    __tablename__ = 'users'  # type: ignore
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    rank: int = 1020
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={'onupdate': datetime.now})

    transactions: list['Transaction'] = Relationship(back_populates='user', cascade_delete=True)


class Token(SQLModel, table=True):
    __tablename__ = 'tokens'  # type: ignore
    cg_id: str = Field(primary_key=True)
    symbol: str
    name: str


class Transaction(TransactionBase, table=True):
    __tablename__ = 'transactions'  # type: ignore
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID | None = Field(default=None, index=True, foreign_key='users.uid', ondelete='CASCADE')

    user: User = Relationship(back_populates='transactions')
    actif_a: Optional['Token'] = Relationship(
        sa_relationship_kwargs={'foreign_keys': lambda: [Transaction.__table__.c.actif_a_id]}
    )
    actif_v: Optional['Token'] = Relationship(
        sa_relationship_kwargs={'foreign_keys': lambda: [Transaction.__table__.c.actif_v_id]}
    )
    actif_f: Optional['Token'] = Relationship(
        sa_relationship_kwargs={'foreign_keys': lambda: [Transaction.__table__.c.actif_f_id]}
    )
