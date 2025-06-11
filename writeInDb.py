import csv
from datetime import datetime

import requests
from pydantic import BaseModel, ConfigDict, field_validator
from sqlmodel import Session, SQLModel, create_engine, select
from src.db.models import Token, Transaction, User
from src.utils.security import hash_password

sqlite_url = 'sqlite:///./src/db/database.sqlite'

engine = create_engine(sqlite_url, echo=True)
# SQLModel.metadata.create_all(engine)


class TransactionCSVModel(BaseModel):
    date: datetime
    type: str
    actif_a: str
    qty_a: float
    actif_v: str | None = None
    price: float | None = None
    qty_v: float | None = None
    destination: str
    origin: str | None = None
    actif_f: str | None = None
    qty_f: float | None = None
    val_f: float | None = None
    val_a: float | None = None
    id: int | None = None

    @field_validator('date', mode='before')
    @classmethod
    def parse_date(cls, v):
        return datetime.strptime(v.strip(), '%d-%m-%y %H:%M:%S')

    @field_validator('*', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and v.strip() == '':
            return None
        return v

    model_config = ConfigDict(extra='ignore')


def resetUsers():
    user1 = User(
        username='fkaisin',
        email='floriankaisin@hotmail.com',
        hashed_password=hash_password('Jtmbmu6-'),
        rank=1337,
    )
    user2 = User(
        username='ariane',
        email='ariane@hotmail.com',
        hashed_password=hash_password('Jtmbmu6-'),
    )
    user3 = User(
        username='Laure',
        email='flammecup1992@hotmail.com',
        hashed_password=hash_password('Jtmbmu6-'),
    )
    user4 = User(
        username='test',
        email='test@hotmail.com',
        hashed_password=hash_password('Jtmbmu6-'),
    )

    with Session(engine) as session:
        for user in session.exec(select(User)):
            session.delete(user)
        session.commit()

        session.add(user1)
        session.add(user2)
        session.add(user3)
        session.add(user4)

        session.commit()


def resetTokens():
    response_list = requests.get('https://api.coingecko.com/api/v3/coins/list')
    coins = response_list.json()

    with Session(engine) as session:
        for token in session.exec(select(Token)):
            session.delete(token)
        session.commit()

        for coin in coins:
            session.add(
                Token(cg_id=coin['id'], symbol=coin['symbol'], name=coin['name'])
            )

        session.add(Token(cg_id='fiat_eur', symbol='EUR', name='Euro'))
        session.add(Token(cg_id='fiat_usd', symbol='USD', name='Dollar US'))
        session.add(Token(cg_id='fiat_cad', symbol='CAD', name='Dollar CA'))
        session.add(Token(cg_id='fiat_chf', symbol='CHF', name='Franc suisse'))
        session.commit()


def resetTransactions():
    with open('./src/transactions.csv', 'rt', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    transactions = [convert_transaction(dict(zip(headers, row))) for row in rows]

    with Session(engine) as session:
        fkaisin_uid = session.exec(
            select(User.uid).where(User.username == 'fkaisin')
        ).one()

        for t in session.exec(select(Transaction)):
            session.delete(t)
        session.commit()

        for t in transactions:
            t['user_id'] = fkaisin_uid
            session.add(Transaction(**t))
        session.commit()


def convert_transaction(tx_dict: dict) -> dict:
    validated = TransactionCSVModel(**tx_dict)
    return validated.model_dump(exclude={'id'})  # on enlève `id` s'il ne sert pas


if __name__ == '__main__':
    resetUsers()
    resetTokens()
    resetTransactions()
