from datetime import date
from decimal import Decimal
from functools import cached_property
from typing import Callable, Any

from sqlalchemy import select, func, ColumnElement, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.core.enums import TransactionStatus
from app.db.models import Transaction
from app.repositories.base import BaseRepository
from app.schemas.report import ReportQueryParams


class TransactionRepository(BaseRepository):
    params: ReportQueryParams

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Transaction)

    @staticmethod
    async def build_columns(methods: list[Callable]) -> list[ColumnElement[Any]]:
        columns = []
        for method in methods:
            column = await method()
            if column is None:
                continue
            columns.append(column)
        return columns

    async def set_params(self, report_params: ReportQueryParams) -> None:
        self.params = report_params

    async def _stmt_metrics(self, methods: list[Callable]) -> Select[Any]:
        return select(*await self.build_columns(methods)).select_from(
            self.cte_filtered_transactions
        )

    @cached_property
    def cte_filtered_transactions(self) -> type[Transaction]:
        stmt = select(Transaction).where(
            Transaction.payment_date >= self.params.start_date,
            Transaction.payment_date <= self.params.end_date,
        )
        if self.params.tr_status != "all":
            stmt = stmt.where(Transaction.status == self.params.tr_status)
        if self.params.tr_type != "all":
            stmt = stmt.where(Transaction.type == self.params.tr_type)
        cte = stmt.cte("filtered_transactions").prefix_with("MATERIALIZED")
        return aliased(Transaction, cte)

    def daily_shift(self, agg_func: Callable[[Any], Any]) -> ColumnElement[Decimal]:
        return (
            100
            * (
                agg_func(self.cte_filtered_transactions.amount)
                - func.lag(agg_func(self.cte_filtered_transactions.amount)).over(
                    order_by=func.date(self.cte_filtered_transactions.payment_date)
                )
            )
            / func.lag(agg_func(self.cte_filtered_transactions.amount)).over(
                order_by=func.date(self.cte_filtered_transactions.payment_date)
            )
        )

    async def column_avg(self) -> ColumnElement[Decimal] | None:
        if not self.params.include_avg:
            return None

        return func.avg(self.cte_filtered_transactions.amount).label("amount_avg")

    async def column_avg_daily_shift(self) -> ColumnElement[Decimal] | None:
        if not self.params.include_avg:
            return None

        return self.daily_shift(func.avg).label("amount_avg_daily_shift")

    async def column_min(self) -> ColumnElement[Decimal] | None:
        if not self.params.include_min:
            return None

        return func.min(self.cte_filtered_transactions.amount).label("amount_min")

    async def column_min_daily_shift(self) -> ColumnElement[Decimal] | None:
        if not self.params.include_min:
            return None

        return self.daily_shift(func.min).label("amount_min_daily_shift")

    async def column_max(self) -> ColumnElement[Decimal] | None:
        if not self.params.include_max:
            return None

        return func.max(self.cte_filtered_transactions.amount).label("amount_max")

    async def column_max_daily_shift(self) -> ColumnElement[Decimal] | None:
        if not self.params.include_max:
            return None

        return self.daily_shift(func.max).label("amount_max_daily_shift")

    async def column_total(self) -> ColumnElement[Decimal]:
        return (
            func.sum(self.cte_filtered_transactions.amount)
            .filter(
                self.cte_filtered_transactions.status == TransactionStatus.SUCCESSFUL
            )
            .label("amount_total")
        )

    async def column_total_daily_shift(self) -> ColumnElement[Decimal]:
        return self.daily_shift(func.sum).label("amount_total_daily_shift")

    async def column_date(self) -> ColumnElement[date]:
        return func.date(self.cte_filtered_transactions.payment_date).label("date")

    async def get_base_metrics(self) -> dict[str, Any]:
        stmt = await self._stmt_metrics(
            [self.column_total, self.column_avg, self.column_min, self.column_max]
        )

        result = await self._session.execute(stmt)
        return dict(result.mappings().all()[0])

    async def get_daily_metrics(self) -> list[dict[str, Any]]:
        stmt = await self._stmt_metrics(
            [
                self.column_date,
                self.column_total_daily_shift,
                self.column_avg_daily_shift,
                self.column_min_daily_shift,
                self.column_max_daily_shift,
            ]
        )
        date_c = func.date(self.cte_filtered_transactions.payment_date)
        stmt = stmt.group_by(date_c).order_by(date_c)
        result = await self._session.execute(stmt)
        return result.mappings().all()
