"""
API v1 Router
Aggregates all API v1 endpoints
"""
from fastapi import APIRouter
from app.api.v1.endpoints import audio, ai, library, categories, schedules, campaigns, shortcuts, radio
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

# Include campaigns endpoints (Campaign Manager module)
api_router.include_router(
    campaigns.router,
    prefix="/campaigns",
    tags=["campaigns"]
)

# Include shortcuts public endpoints (mobile page)
api_router.include_router(
    shortcuts.router,
    prefix="/shortcuts",
    tags=["shortcuts"]
)

# Include radio control endpoints (Azuracast)
api_router.include_router(
    radio.router,
    prefix="/radio",
    tags=["radio"]
)
