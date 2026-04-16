from pathlib import Path
from typing import Any

from pandas import DataFrame, read_csv

from app.core.enums import MetricSortByCountry, TransactionStatus
from app.db.transaction_manager import TransactionManager
from app.schemas.report import ReportQueryParams


class ReportService:
    def __init__(self, tr_manager: TransactionManager) -> None:
        self.tr_manager = tr_manager

    @staticmethod
    async def get_user_countries() -> DataFrame:
        file_path = Path.cwd() / "external" / "user-country.csv"
        df = read_csv(file_path, delimiter=";")
        df.columns = ["id", "country"]
        return df

    async def get_report(self, params: ReportQueryParams) -> dict[str, Any]:
        if params.tr_status == TransactionStatus.FAILED:
            return {}
        async with self.tr_manager:
            await self.tr_manager.transaction_repo.set_params(params)
            base_metrics = await self.tr_manager.transaction_repo.get_base_metrics()
        if not params.include_daily_shift:
            return base_metrics
        async with self.tr_manager:
            await self.tr_manager.transaction_repo.set_params(params)
            daily_metrics = await self.tr_manager.transaction_repo.get_daily_metrics()
        daily = []
        for metric in daily_metrics:
            daily.append(
                {
                    "date": metric["date"],
                    "amount_total": metric["amount_total_daily_shift"],
                    "amount_avg": metric.get("amount_avg_daily_shift"),
                    "amount_min": metric.get("amount_min_daily_shift"),
                    "amount_max": metric.get("amount_max_daily_shift"),
                },
            )
        base_metrics["daily"] = daily
        return base_metrics

    async def get_report_by_countries(
        self,
        sort_by: MetricSortByCountry | None,
        top_n: int | None,
    ) -> list[dict[str, Any]]:
        dataframe = await self.get_user_countries()
        user_ids = dataframe["id"].tolist()
        if not user_ids:
            return []

        dataframe["count"] = 0
        dataframe["total"] = 0.0
        dataframe["avg"] = 0.0

        async with self.tr_manager:
            transactions = await self.tr_manager.user_repo.get_user_transactions_by_external_ids(user_ids)

        for row in transactions:
            dataframe.loc[dataframe["id"] == row["external_id"], ["count", "total", "avg"]] = [
                row["count"],
                float(row["total"]),
                float(row["avg"]),
            ]

        dataframe = dataframe.groupby("country", as_index=False).agg(
            count=("count", "sum"),
            total=("total", "sum"),
            avg=("avg", "mean"),
        )

        if sort_by is not None:
            dataframe = dataframe.sort_values(by=sort_by, ascending=False)

        if top_n is not None:
            dataframe = dataframe.head(top_n)

        return dataframe.to_dict(orient="records")
