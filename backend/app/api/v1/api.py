"""
API v1 Router
Aggregates all API v1 endpoints
"""
from fastapi import APIRouter
from app.api.v1.endpoints import audio, ai

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

# Future routers will be added here:
# api_router.include_router(library.router, prefix="/library", tags=["library"])
# api_router.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
# api_router.include_router(player.router, prefix="/player", tags=["player"])
# api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
