import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

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
