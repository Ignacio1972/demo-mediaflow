"""
Operations API Router
Aggregates all operations-related endpoints
"""
from fastapi import APIRouter

from app.api.v1.endpoints.operations.vehicles import router as vehicles_router
from app.api.v1.endpoints.operations.schedules import router as schedules_router
from app.api.v1.endpoints.operations.employee_call import router as employee_call_router

router = APIRouter()

# Include sub-routers
router.include_router(vehicles_router)
router.include_router(schedules_router)
router.include_router(employee_call_router)

# Future operation templates will be added here:
# router.include_router(lost_child_router)
# router.include_router(promotions_router)
