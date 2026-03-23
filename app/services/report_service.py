from typing import Any

from app.core.enums import TransactionStatus
from app.db.uow import SaSessionUnitOfWork
from app.schemas.report import ReportQueryParams


class ReportService:
    def __init__(self, uow: SaSessionUnitOfWork) -> None:
        self.uow = uow

    async def get_report(self, params: ReportQueryParams) -> dict[str, Any]:
        if params.tr_status == TransactionStatus.FAILED:
            return {}
        async with self.uow:
            await self.uow.transaction_repo.set_params(params)
            base_metrics = await self.uow.transaction_repo.get_base_metrics()
        if not params.include_daily_shift:
            return base_metrics
        async with self.uow:
            daily_metrics = await self.uow.transaction_repo.get_daily_metrics()
        daily = []
        for metric in daily_metrics:
            daily.append(
                {
                    "date": metric["date"],
                    "amount_total": metric["amount_total_daily_shift"],
                    "amount_avg": metric.get("amount_avg_daily_shift"),
                    "amount_min": metric.get("amount_min_daily_shift"),
                    "amount_max": metric.get("amount_max_daily_shift"),
                }
            )
        base_metrics["daily"] = daily
        return base_metrics
