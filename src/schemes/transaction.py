from datetime import datetime

from pydantic import computed_field
from sqlmodel import Field, SQLModel


class TransactionBase(SQLModel):
    date: datetime
    type: str
    actif_a: str = Field(default=None, foreign_key='tokens.cg_id')
    qty_a: float
    actif_v: str | None = Field(default=None, foreign_key='tokens.cg_id')
    price: float | None = None
    destination: str
    origin: str | None = None
    actif_f: str | None = Field(default=None, foreign_key='tokens.cg_id')
    qty_f: float | None = None
    value_f: float | None = None
    value_a: float | None = None


class TransactionPublic(TransactionBase):
    @computed_field
    @property
    def qty_v(self) -> float | None:
        if self.qty_a is not None and self.price is not None:
            return round(self.qty_a * self.price, 10)
        return None
