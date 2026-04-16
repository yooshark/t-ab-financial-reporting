from collections.abc import Sequence

from sqlalchemy import RowMapping, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Transaction, User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_all_ids(self) -> list[int]:
        stmt = select(User.id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_transactions_by_external_ids(self, user_ids: list[int]) -> Sequence[RowMapping]:
        stmt = (
            select(
                self.model.external_id,
                func.count(Transaction.id).label("count"),
                func.sum(Transaction.amount).label("total"),
                func.avg(Transaction.amount).label("avg"),
            )
            .join(self.model.transactions)
            .where(self.model.external_id.in_(user_ids))
            .group_by(self.model.id)
        )
        result = await self._session.execute(stmt)
        return result.mappings().all()
