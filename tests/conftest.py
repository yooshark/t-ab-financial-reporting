from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)

from app.core.app_factory import app
from app.core.config import Settings
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.user_repo import UserRepository
from app.services.report_service import ReportService

engine: AsyncEngine = create_async_engine("postgresql+asyncpg:///:memory:", echo=False, poolclass=StaticPool)


@pytest.fixture
def app_settings() -> Settings:
    return Settings(
        DEBUG=True,
    )


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.transaction_repo = AsyncMock()
    uow.user_repo = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


@pytest.fixture
def user_repo(mock_session):
    return UserRepository(mock_session)


@pytest.fixture
def transaction_repo(mock_session):
    return TransactionRepository(mock_session)


@pytest.fixture
def mock_report_service():
    return AsyncMock()


@pytest.fixture
def report_service(mock_uow):
    return ReportService(mock_uow)


@pytest.fixture()
def test_app() -> FastAPI:
    return app


@pytest.fixture
async def api_client(test_app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture()
def override_dependency(test_app: FastAPI):
    from contextlib import contextmanager

    @contextmanager
    def _override(dep, value):
        test_app.dependency_overrides[dep] = lambda: value
        try:
            yield
        finally:
            test_app.dependency_overrides.clear()

    return _override
