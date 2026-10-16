from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.exceptions import AppError, app_error_handler
from app.api.router import router

settings = get_settings()
setup_logging("DEBUG" if settings.is_development else "INFO")

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

# CORS — restrict to frontend origin in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)

app.include_router(router)


@app.on_event("startup")
async def on_startup():
    import logging
    logging.getLogger(__name__).info(
        "Debug Dojo API starting | env=%s | provider=%s",
        settings.app_env,
        settings.llm_provider,
    )
