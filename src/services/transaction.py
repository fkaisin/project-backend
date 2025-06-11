from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import Transaction, User


class TransactionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_transactions(self, currentUser: User):
        statement = select(Transaction).where(Transaction.user_id == currentUser.uid)
        result = await self.session.exec(statement)
        return result.all()
