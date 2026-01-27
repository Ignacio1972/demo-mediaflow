"""
Config API endpoints
Exposes tenant configuration to frontend
"""
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()


class TenantConfigResponse(BaseModel):
    """Tenant configuration response"""
    tenant_id: str
    tenant_name: str
    tenant_logo: str
    tenant_primary_color: str
    tenant_secondary_color: str
    tenant_domain: str
    tenant_favicon: str
    app_version: str


@router.get("/tenant", response_model=TenantConfigResponse)
async def get_tenant_config():
    """
    Get tenant configuration for frontend branding.

    Returns tenant-specific settings like name, logo, and colors
    that the frontend uses to customize the UI.
    """
    return TenantConfigResponse(
        tenant_id=settings.TENANT_ID,
        tenant_name=settings.TENANT_NAME,
        tenant_logo=settings.TENANT_LOGO,
        tenant_primary_color=settings.TENANT_PRIMARY_COLOR,
        tenant_secondary_color=settings.TENANT_SECONDARY_COLOR,
        tenant_domain=settings.TENANT_DOMAIN,
        tenant_favicon=settings.TENANT_FAVICON,
        app_version=settings.APP_VERSION
    )
