"""
API v1 Router
Aggregates all API v1 endpoints
"""
from fastapi import APIRouter
from app.api.v1.endpoints import audio, ai, library, categories, schedules
from app.api.v1.endpoints.settings import router as settings_router
from app.api.v1.endpoints.operations import router as operations_router

api_router = APIRouter()

# Include audio endpoints
api_router.include_router(
    audio.router,
    prefix="/audio",
    tags=["audio"]
)

# Include AI endpoints
api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["ai"]
)

# Include library endpoints
api_router.include_router(
    library.router,
    prefix="/library",
    tags=["library"]
)

# Include categories endpoints
api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["categories"]
)

# Include schedules endpoints
api_router.include_router(
    schedules.router,
    prefix="/schedules",
    tags=["schedules"]
)

# Include settings endpoints (Playground - refactored)
api_router.include_router(
    settings_router,
    prefix="/settings",
    tags=["settings"]
)

# Include operations endpoints (Vehicle announcements, etc.)
api_router.include_router(
    operations_router,
    prefix="/operations",
    tags=["operations"]
)

# Future routers will be added here:
# api_router.include_router(player.router, prefix="/player", tags=["player"])
