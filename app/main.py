"""FastAPI application entrypoint."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config.logger import configure_logging, get_logger
from app.config.settings import get_settings
from app.utils.exceptions import AppError

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize and tear down app-level resources."""
    logger.info("application.startup", extra={"model": settings.model_name})
    yield
    logger.info("application.shutdown")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready LangChain/Groq agentic assistant API.",
    lifespan=lifespan,
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log request metadata and latency for every HTTP request."""
    start = perf_counter()
    response = await call_next(request)
    elapsed_ms = round((perf_counter() - start) * 1000, 2)
    logger.info(
        "http.request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "elapsed_ms": elapsed_ms,
        },
    )
    response.headers["X-Process-Time-Ms"] = str(elapsed_ms)
    return response


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    """Convert domain errors to consistent API responses."""
    logger.warning("application.error", extra={"code": exc.code, "detail": exc.detail})
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.detail}},
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    """Avoid leaking implementation details for unexpected failures."""
    logger.exception("application.unhandled_error", extra={"error": str(exc)})
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "Unexpected server error."}},
    )


app.include_router(router)
