from fastapi import Depends

from app.db.session import sessionmaker
from app.db.transaction_manager import TransactionManager
from app.services.report_service import ReportService


async def get_tr_manager() -> TransactionManager:
    return TransactionManager(sessionmaker)


async def get_report_service(
    tr_manager: TransactionManager = Depends(get_tr_manager),
) -> ReportService:
    return ReportService(tr_manager)
