from fastapi import APIRouter
from app.api.routes import health, challenges, submissions, hints, learners
from app.core.config import get_settings

settings = get_settings()

router = APIRouter()

# Health outside /api prefix
router.include_router(health.router)

# Domain routes under /api prefix
api_router = APIRouter(prefix=settings.api_prefix)
api_router.include_router(challenges.router)
api_router.include_router(submissions.router)
api_router.include_router(hints.router)
api_router.include_router(learners.router)

router.include_router(api_router)
