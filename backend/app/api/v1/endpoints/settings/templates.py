"""
Message Template Settings API Endpoints
Handles template management for the Template Manager - v2.1 Playground
"""
import logging
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.db.session import get_db
from app.models.message_template import MessageTemplate
from app.schemas.templates import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateReorderRequest,
    TemplatePreviewRequest,
    TemplatePreviewResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def serialize_template(template: MessageTemplate) -> dict:
    """Serialize a MessageTemplate model to dict"""
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "template_text": template.template_text,
        "variables": template.variables or [],
        "module": template.module,
        "order": template.order,
        "active": template.active,
        "is_default": template.is_default,
        "use_announcement_sound": template.use_announcement_sound,
        "default_voice_id": template.default_voice_id,
        "created_at": template.created_at,
        "updated_at": template.updated_at,
    }


@router.get(
    "/templates",
    response_model=List[TemplateResponse],
    summary="Get All Templates",
    description="Get all message templates (optionally filtered by module)",
)
async def get_all_templates(
    module: Optional[str] = Query(None, description="Filter by module"),
    include_inactive: bool = Query(True, description="Include inactive templates"),
    db: AsyncSession = Depends(get_db),
):
    """Get all templates for settings management"""
    try:
        logger.info(f"📝 Fetching templates (module={module}, include_inactive={include_inactive})")

        query = select(MessageTemplate).order_by(
            MessageTemplate.module.asc(),
            MessageTemplate.order.asc()
        )

        if module:
            query = query.filter(MessageTemplate.module == module.lower())

        if not include_inactive:
            query = query.filter(MessageTemplate.active == True)

        result = await db.execute(query)
        templates = result.scalars().all()

        logger.info(f"✅ Retrieved {len(templates)} templates")
        return [serialize_template(t) for t in templates]

    except Exception as e:
        logger.error(f"❌ Failed to fetch templates: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch templates: {str(e)}",
        )


@router.get(
    "/templates/{template_id}",
    response_model=TemplateResponse,
    summary="Get Single Template",
)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single template by ID"""
    try:
        result = await db.execute(
            select(MessageTemplate).filter(MessageTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template '{template_id}' not found",
            )

        return serialize_template(template)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch template: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch template: {str(e)}",
        )


@router.post(
    "/templates",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Template",
    description="Create a new message template",
)
async def create_template(
    template_data: TemplateCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new template"""
    try:
        logger.info(f"➕ Creating template: {template_data.id}")

        # Check if ID already exists
        result = await db.execute(
            select(MessageTemplate).filter(MessageTemplate.id == template_data.id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Template with ID '{template_data.id}' already exists",
            )

        # Extract variables from template text if not provided
        variables = template_data.variables
        if not variables:
            variables = extract_variables(template_data.template_text)

        # Get next order number if not provided
        order = template_data.order
        if order is None:
            result = await db.execute(
                select(MessageTemplate).filter(
                    MessageTemplate.module == template_data.module
                )
            )
            module_templates = result.scalars().all()
            order = max([t.order for t in module_templates], default=-1) + 1

        # If this is set as default, unset other defaults in the module
        if template_data.is_default:
            await db.execute(
                update(MessageTemplate)
                .where(MessageTemplate.module == template_data.module)
                .values(is_default=False)
            )

        # Create template
        template = MessageTemplate(
            id=template_data.id,
            name=template_data.name,
            description=template_data.description,
            template_text=template_data.template_text,
            variables=variables,
            module=template_data.module,
            order=order,
            active=template_data.active,
            is_default=template_data.is_default,
            use_announcement_sound=template_data.use_announcement_sound,
            default_voice_id=template_data.default_voice_id,
        )

        db.add(template)
        await db.commit()
        await db.refresh(template)

        logger.info(f"✅ Template created: {template.id}")

        return serialize_template(template)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create template: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}",
        )


@router.patch(
    "/templates/{template_id}",
    response_model=TemplateResponse,
    summary="Update Template",
    description="Update an existing template",
)
async def update_template(
    template_id: str,
    template_data: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update existing template"""
    try:
        logger.info(f"📝 Updating template: {template_id}")

        result = await db.execute(
            select(MessageTemplate).filter(MessageTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template '{template_id}' not found",
            )

        # Update fields
        update_data = template_data.model_dump(exclude_unset=True)

        # If template_text changed and variables not provided, extract them
        if "template_text" in update_data and "variables" not in update_data:
            update_data["variables"] = extract_variables(update_data["template_text"])

        # If setting as default, unset other defaults in the module
        if update_data.get("is_default"):
            module = update_data.get("module", template.module)
            await db.execute(
                update(MessageTemplate)
                .where(MessageTemplate.module == module)
                .where(MessageTemplate.id != template_id)
                .values(is_default=False)
            )

        for field, value in update_data.items():
            setattr(template, field, value)

        await db.commit()
        await db.refresh(template)

        logger.info(f"✅ Template updated: {template.id}")

        return serialize_template(template)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update template: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update template: {str(e)}",
        )


@router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Template",
    description="Delete a template",
)
async def delete_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a template"""
    try:
        logger.info(f"🗑️ Deleting template: {template_id}")

        result = await db.execute(
            select(MessageTemplate).filter(MessageTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template '{template_id}' not found",
            )

        # If deleting the default, set another as default
        if template.is_default:
            result = await db.execute(
                select(MessageTemplate)
                .filter(MessageTemplate.module == template.module)
                .filter(MessageTemplate.id != template_id)
                .filter(MessageTemplate.active == True)
                .order_by(MessageTemplate.order.asc())
                .limit(1)
            )
            next_default = result.scalar_one_or_none()
            if next_default:
                next_default.is_default = True

        await db.delete(template)
        await db.commit()

        logger.info(f"✅ Template deleted: {template_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete template: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete template: {str(e)}",
        )


@router.put(
    "/templates/reorder",
    summary="Reorder Templates",
    description="Update the display order of templates",
)
async def reorder_templates(
    request: TemplateReorderRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reorder templates"""
    try:
        logger.info(f"🔄 Reordering templates: {request.template_ids}")

        for index, template_id in enumerate(request.template_ids):
            await db.execute(
                update(MessageTemplate)
                .where(MessageTemplate.id == template_id)
                .values(order=index)
            )

        await db.commit()

        logger.info("✅ Templates reordered")

        return {"success": True, "message": "Templates reordered successfully"}

    except Exception as e:
        logger.error(f"❌ Failed to reorder templates: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reorder templates: {str(e)}",
        )


@router.post(
    "/templates/preview",
    response_model=TemplatePreviewResponse,
    summary="Preview Template",
    description="Preview a template with variable substitution",
)
async def preview_template(
    request: TemplatePreviewRequest,
):
    """Preview a template with variables replaced"""
    try:
        template_text = request.template_text
        variables = request.variables

        # Find all variables in template
        template_vars = extract_variables(template_text)

        # Find missing variables
        missing = [v for v in template_vars if v not in variables]

        # Replace variables
        rendered = template_text
        for var_name, var_value in variables.items():
            rendered = rendered.replace(f"{{{var_name}}}", str(var_value))

        return TemplatePreviewResponse(
            original=template_text,
            rendered=rendered,
            missing_variables=missing,
        )

    except Exception as e:
        logger.error(f"❌ Failed to preview template: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview template: {str(e)}",
        )


@router.get(
    "/templates/modules/list",
    summary="Get Available Modules",
    description="Get list of available template modules",
)
async def get_modules(
    db: AsyncSession = Depends(get_db),
):
    """Get list of modules that have templates"""
    try:
        result = await db.execute(
            select(MessageTemplate.module).distinct()
        )
        modules = [row[0] for row in result.fetchall()]

        # Define module info
        module_info = {
            "vehicles": {
                "id": "vehicles",
                "name": "Vehiculos Mal Estacionados",
                "icon": "🚗",
                "variables": ["marca", "color", "patente"],
            },
            "schedules": {
                "id": "schedules",
                "name": "Anuncios de Cierre",
                "icon": "🕐",
                "variables": ["minutes"],
            },
            "employee_call": {
                "id": "employee_call",
                "name": "Llamado a Empleado o Cliente",
                "icon": "📞",
                "variables": ["nombre", "ubicacion"],
            },
            "lost_child": {
                "id": "lost_child",
                "name": "Nino Perdido",
                "icon": "👶",
                "variables": ["nombre", "edad", "descripcion"],
            },
            "promotions": {
                "id": "promotions",
                "name": "Promociones",
                "icon": "🎉",
                "variables": ["producto", "precio", "descuento"],
            },
        }

        return {
            "modules": [
                module_info.get(m, {"id": m, "name": m.replace("_", " ").title(), "icon": "📝", "variables": []})
                for m in modules
            ],
            "available_modules": list(module_info.values()),
        }

    except Exception as e:
        logger.error(f"❌ Failed to fetch modules: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch modules: {str(e)}",
        )


def extract_variables(template_text: str) -> List[str]:
    """Extract variable names from a template string"""
    # Find all {variable_name} patterns
    pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}'
    matches = re.findall(pattern, template_text)
    # Return unique variables preserving order
    seen = set()
    return [v for v in matches if not (v in seen or seen.add(v))]
