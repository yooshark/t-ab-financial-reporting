from fastapi import APIRouter

from app.api.routes.report import router as report_router
from app.api.routes.utils import router as utils_router

api_router = APIRouter(prefix="/api")
api_router.include_router(utils_router)
api_router.include_router(report_router)
