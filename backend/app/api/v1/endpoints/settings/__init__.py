"""
Settings API Router
Aggregates all settings-related endpoints (Playground)
"""
from fastapi import APIRouter

from app.api.v1.endpoints.settings.voices import router as voices_router
from app.api.v1.endpoints.settings.music import router as music_router
from app.api.v1.endpoints.settings.categories import router as categories_router
from app.api.v1.endpoints.settings.automatic import router as automatic_router
from app.api.v1.endpoints.settings.playroom import router as playroom_router
from app.api.v1.endpoints.settings.ai_clients import router as ai_clients_router

router = APIRouter()

# Include all settings sub-routers
router.include_router(voices_router)
router.include_router(music_router)
router.include_router(categories_router)
router.include_router(automatic_router)
router.include_router(playroom_router)
router.include_router(ai_clients_router)
