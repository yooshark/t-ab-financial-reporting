from typing import Self, TypeVar, Any

from sqlalchemy.ext.asyncio import (
    AsyncSessionTransaction,
    async_sessionmaker,
    AsyncSession,
)

from app.repositories.transaction_repo import TransactionRepository
from app.repositories.user_repo import UserRepository

TExc = TypeVar("TExc", bound=BaseException)


class SaSessionUnitOfWork:
    session: AsyncSession
    session_factory: async_sessionmaker[AsyncSession]
    transaction: AsyncSessionTransaction
    user_repo: UserRepository
    transaction_repo: TransactionRepository

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def __aenter__(self) -> Self:
        self.session = self.session_factory()
        self.user_repo = UserRepository(self.session)
        self.transaction_repo = TransactionRepository(self.session)
        self.transaction: AsyncSessionTransaction = await self.session.begin()
        return self

    async def __aexit__(
        self, exc_type: type[TExc] | None, exc: TExc | None, traceback: Any | None
    ) -> None:
        if exc_type is None:
            await self.commit()
        else:
            await self.transaction.rollback()
        await self.session.close()

    async def commit(self) -> None:
        await self.transaction.commit()
