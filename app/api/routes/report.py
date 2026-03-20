from fastapi import APIRouter, Depends

from app.core.dependencies import get_report_service
from app.schemas.report import ReportQueryParams, ReportResponse
from app.services.report_service import ReportService

router = APIRouter(
    prefix="/report",
    tags=["Report"],
)


@router.get("/", response_model=ReportResponse)
async def get_report(
    params: ReportQueryParams = Depends(),
    service: ReportService = Depends(get_report_service),
):
    return await service.get_report(params)
