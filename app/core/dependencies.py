from fastapi import Depends

from app.db.session import sessionmaker
from app.db.uow import SaSessionUnitOfWork
from app.services.report_service import ReportService


async def get_uow() -> SaSessionUnitOfWork:
    return SaSessionUnitOfWork(sessionmaker)


async def get_report_service(
    uow: SaSessionUnitOfWork = Depends(get_uow),
) -> ReportService:
    return ReportService(uow)
