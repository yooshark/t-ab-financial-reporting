from app.schemas.report import ReportQueryParams
from app.db.uow import SaSessionUnitOfWork


class ReportService:
    def __init__(self, uow: SaSessionUnitOfWork) -> None:
        self.uow = uow

    async def get_report(self, params: ReportQueryParams):
        async with self.uow:
            await self.uow.transaction_repo.set_params(params)
            analytics = await self.uow.transaction_repo.get_analytics()
        return analytics
