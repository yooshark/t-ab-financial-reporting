from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_all_ids(self) -> list[int]:
        stmt = select(User.id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
