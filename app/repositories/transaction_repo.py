from collections.abc import Callable
from functools import cached_property
from typing import Any

from sqlalchemy import ColumnElement, RowMapping, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

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
            col = await method()
            if col is not None:
                columns.append(col)
        return columns

    async def set_params(self, report_params: ReportQueryParams) -> None:
        self.params = report_params

    def _base_stmt(self) -> Select:
        stmt = select(Transaction).where(
            Transaction.payment_date >= self.params.start_date,
            Transaction.payment_date <= self.params.end_date,
        )

        if self.params.tr_type != "all":
            stmt = stmt.where(Transaction.type == self.params.tr_type)

        return stmt

    @cached_property
    def base_transactions(self):
        return self._base_stmt().where(Transaction.status == TransactionStatus.SUCCESSFUL).subquery()

    @cached_property
    def filtered_transactions(self):
        stmt = self._base_stmt()

        if self.params.tr_status != "all":
            stmt = stmt.where(Transaction.status == self.params.tr_status)

        return stmt.subquery()

    async def _stmt_metrics(self, methods: list[Callable]) -> Select[Any]:
        return select(*await self.build_columns(methods)).select_from(self.base_transactions)

    async def column_total(self):
        return func.sum(self.base_transactions.c.amount).label("amount_total")

    async def column_avg(self):
        if not self.params.include_avg:
            return None
        return func.avg(self.base_transactions.c.amount).label("amount_avg")

    async def column_min(self):
        if not self.params.include_min:
            return None
        return func.min(self.base_transactions.c.amount).label("amount_min")

    async def column_max(self):
        if not self.params.include_max:
            return None
        return func.max(self.base_transactions.c.amount).label("amount_max")

    async def get_base_metrics(self) -> dict[str, Any]:
        stmt = await self._stmt_metrics([self.column_total, self.column_avg, self.column_min, self.column_max])
        result = await self._session.execute(stmt)
        return dict(result.mappings().one())

    def _daily_aggregated_subquery(self):
        return (
            select(
                func.date(self.filtered_transactions.c.payment_date).label("date"),
                func.sum(self.filtered_transactions.c.amount).label("daily_total"),
            )
            .group_by(func.date(self.filtered_transactions.c.payment_date))
            .subquery()
        )

    def _daily_stmt(self) -> Select:
        subq = self._daily_aggregated_subquery()

        return select(
            subq.c.date,
            subq.c.daily_total,
            (
                100
                * (subq.c.daily_total - func.lag(subq.c.daily_total).over(order_by=subq.c.date))
                / func.lag(subq.c.daily_total).over(order_by=subq.c.date)
            ).label("change_daily_shift"),
        ).order_by(subq.c.date)

    async def get_daily_metrics(self) -> list[RowMapping]:
        if not self.params.include_daily_shift:
            return []

        stmt = self._daily_stmt()
        result = await self._session.execute(stmt)
        return list(result.mappings().all())
