from typing import TypeVar, Any

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Base

TModel = TypeVar("TModel", bound=Base)


class BaseRepository[TModel]:
    def __init__(self, session: AsyncSession, model: type[TModel]) -> None:
        self._session = session
        self.model = model

    async def count(self) -> int:
        stmt = select(func.count(self.model.id))
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def bulk_insert(self, data: list[dict[str, Any]]) -> None:
        await self._session.execute(insert(self.model), data)
