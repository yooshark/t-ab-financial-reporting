from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Transaction
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Transaction)
