from datetime import date, timedelta
from decimal import Decimal
from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator

from app.core.enums import TransactionStatus, TransactionType

ReportTransactionStatus = Literal["all", TransactionStatus.SUCCESSFUL, TransactionStatus.FAILED]
ReportTransactionType = Literal["all", TransactionType.PAYMENT, TransactionType.INVOICE]


class ReportQueryParams(BaseModel):
    start_date: date = Field(default_factory=lambda: date.today() - timedelta(days=30))
    end_date: date = Field(default_factory=date.today)
    tr_status: ReportTransactionStatus = "all"
    tr_type: ReportTransactionType = "all"
    include_avg: bool = False
    include_min: bool = False
    include_max: bool = False
    include_daily_shift: bool = False

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.start_date > self.end_date:
            raise ValueError("start_date must be <= end_date")
        return self


class DailyData(BaseModel):
    date: date
    change_daily_shift: Decimal | None = None


class ReportResponse(BaseModel):
    amount_total: Decimal | None = None
    amount_avg: Decimal | None = None
    amount_min: Decimal | None = None
    amount_max: Decimal | None = None
    daily: list[DailyData] | None = None


class ReportByCountryItem(BaseModel):
    country: str
    count: int
    total: Decimal
    avg: Decimal | None = None
