from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.core.dependencies import get_report_service
from app.core.enums import MetricSortByCountry
from app.schemas.report import ReportByCountryItem, ReportQueryParams, ReportResponse
from app.services.report_service import ReportService

router = APIRouter(
    prefix="/report",
    tags=["Report"],
)


@router.get("/", response_model=ReportResponse)
async def get_report(
    params: Annotated[ReportQueryParams, Depends()],
    service: Annotated[ReportService, Depends(get_report_service)],
) -> dict[str, Any]:
    return await service.get_report(params)


@router.get("/by-country", response_model=list[ReportByCountryItem])
async def get_report_by_country(
    service: Annotated[ReportService, Depends(get_report_service)],
    sort_by: MetricSortByCountry | None = None,
    top_n: int | None = None,
) -> list[dict[str, Any]]:
    return await service.get_report_by_countries(sort_by, top_n)
