from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Base as ModelBase


class ReportRepository:
    def __init__(self, session: AsyncSession, model: ModelBase) -> None:
        self._session = session
        self.model = model
