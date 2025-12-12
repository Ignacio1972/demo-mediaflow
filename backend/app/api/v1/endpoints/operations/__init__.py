"""
Operations API Router
Aggregates all operations-related endpoints
"""
from fastapi import APIRouter

from app.api.v1.endpoints.operations.vehicles import router as vehicles_router

router = APIRouter()

# Include vehicles sub-router
router.include_router(vehicles_router)

# Future operation templates will be added here:
# router.include_router(lost_child_router)
# router.include_router(promotions_router)
