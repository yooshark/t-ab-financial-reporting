import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from app.api.main import api_router
from app.core.config import settings
from app.core.logs import configure_logging
from app.db.session import engine

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("Application is starting...")
    yield
    logger.debug("Disposing async engine...")
    await engine.dispose()
    logger.debug("Engine is disposed.")
    logger.info("Application has stopped")


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        lifespan=lifespan,
        docs_url="/api/docs" if settings.DEBUG else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOW_ORIGINS,
        allow_origin_regex=settings.ALLOW_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    return app


app = create_app()


@app.exception_handler(HTTPException)
async def api_http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={"status": "error", "data": None, "detail": exc.detail},
    )
