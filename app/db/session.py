import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.db.uow import SaSessionUnitOfWork

logger = logging.getLogger("app")

engine = create_async_engine(
    url=settings.db.dsn,
    echo=settings.db.ECHO,
    connect_args={"timeout": settings.db.TIMEOUT},
    pool_pre_ping=True,
)

sessionmaker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session


async def get_uow(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[SaSessionUnitOfWork, None]:
    uow = SaSessionUnitOfWork(sessionmaker)

    async with uow:
        yield uow
