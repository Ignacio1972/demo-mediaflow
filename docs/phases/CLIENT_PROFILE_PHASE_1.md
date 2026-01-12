# Fase 1: Backend - Nuevos Endpoints

**Plan Maestro**: `CLIENT_PROFILE_SYSTEM.md`
**Estado**: Pendiente

---

## Objetivo

Crear los endpoints necesarios para gestionar instrucciones de campaña vinculadas al cliente activo.

---

## Tareas

### 1.1 Crear Schemas

**Archivo**: `backend/app/schemas/ai_client.py`

```python
# Agregar al final del archivo existente

class CampaignPromptUpdate(BaseModel):
    """Request para actualizar instrucciones de campaña"""
    instructions: str = Field(
        ...,
        min_length=0,
        max_length=5000,
        description="Instrucciones de IA para esta campaña"
    )

class CampaignPromptResponse(BaseModel):
    """Response con instrucciones de una campaña específica"""
    client_id: str
    client_name: str
    campaign_id: str
    instructions: str

    class Config:
        from_attributes = True

class AllCampaignPromptsResponse(BaseModel):
    """Response con todas las instrucciones del cliente"""
    client_id: str
    client_name: str
    prompts: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapa de campaign_id -> instrucciones"
    )

    class Config:
        from_attributes = True
```

### 1.2 Implementar Endpoints

**Archivo**: `backend/app/api/v1/endpoints/settings/ai_clients.py`

```python
# Agregar después de los endpoints existentes

# ============================================================
# CAMPAIGN PROMPTS - Instrucciones por campaña del cliente activo
# ============================================================

@router.get(
    "/active/campaign-prompts",
    response_model=AllCampaignPromptsResponse,
    summary="Listar instrucciones de todas las campañas",
    description="Obtiene todas las instrucciones de campaña del cliente activo"
)
async def get_active_client_all_prompts(
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna un mapa con todas las instrucciones de campaña
    del cliente actualmente activo.
    """
    active_client = await ai_client_manager.get_active_client(db)
    if not active_client:
        raise HTTPException(
            status_code=404,
            detail="No hay cliente activo configurado"
        )

    prompts = active_client.custom_prompts or {}

    return AllCampaignPromptsResponse(
        client_id=active_client.id,
        client_name=active_client.name,
        prompts=prompts
    )


@router.get(
    "/active/campaign-prompts/{campaign_id}",
    response_model=CampaignPromptResponse,
    summary="Obtener instrucciones de una campaña",
    description="Obtiene las instrucciones de una campaña específica del cliente activo"
)
async def get_active_client_campaign_prompt(
    campaign_id: str = Path(..., description="ID de la campaña"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna las instrucciones de una campaña específica
    del cliente actualmente activo.

    Si no existen instrucciones para esa campaña, retorna string vacío.
    """
    active_client = await ai_client_manager.get_active_client(db)
    if not active_client:
        raise HTTPException(
            status_code=404,
            detail="No hay cliente activo configurado"
        )

    prompts = active_client.custom_prompts or {}
    instructions = prompts.get(campaign_id, "")

    return CampaignPromptResponse(
        client_id=active_client.id,
        client_name=active_client.name,
        campaign_id=campaign_id,
        instructions=instructions
    )


@router.patch(
    "/active/campaign-prompts/{campaign_id}",
    response_model=CampaignPromptResponse,
    summary="Actualizar instrucciones de una campaña",
    description="Actualiza las instrucciones de una campaña en el cliente activo"
)
async def update_active_client_campaign_prompt(
    campaign_id: str = Path(..., description="ID de la campaña"),
    request: CampaignPromptUpdate = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza las instrucciones de una campaña específica
    en el cliente actualmente activo.

    Si las instrucciones están vacías, se elimina la entrada.
    """
    active_client = await ai_client_manager.get_active_client(db)
    if not active_client:
        raise HTTPException(
            status_code=404,
            detail="No hay cliente activo configurado"
        )

    # Obtener prompts actuales o inicializar
    prompts = active_client.custom_prompts or {}

    # Actualizar o eliminar
    if request.instructions.strip():
        prompts[campaign_id] = request.instructions.strip()
        logger.info(f"📝 Updated campaign prompt: {active_client.id}/{campaign_id}")
    else:
        # Si está vacío, eliminar la entrada
        prompts.pop(campaign_id, None)
        logger.info(f"🗑️ Removed campaign prompt: {active_client.id}/{campaign_id}")

    # Guardar
    active_client.custom_prompts = prompts
    await db.commit()
    await db.refresh(active_client)

    return CampaignPromptResponse(
        client_id=active_client.id,
        client_name=active_client.name,
        campaign_id=campaign_id,
        instructions=prompts.get(campaign_id, "")
    )


@router.delete(
    "/active/campaign-prompts/{campaign_id}",
    status_code=204,
    summary="Eliminar instrucciones de una campaña",
    description="Elimina las instrucciones de una campaña del cliente activo"
)
async def delete_active_client_campaign_prompt(
    campaign_id: str = Path(..., description="ID de la campaña"),
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina las instrucciones de una campaña específica
    del cliente actualmente activo.
    """
    active_client = await ai_client_manager.get_active_client(db)
    if not active_client:
        raise HTTPException(
            status_code=404,
            detail="No hay cliente activo configurado"
        )

    prompts = active_client.custom_prompts or {}

    if campaign_id in prompts:
        del prompts[campaign_id]
        active_client.custom_prompts = prompts
        await db.commit()
        logger.info(f"🗑️ Deleted campaign prompt: {active_client.id}/{campaign_id}")

    return Response(status_code=204)
```

### 1.3 Agregar Imports Necesarios

```python
# En la parte superior de ai_clients.py, agregar:
from fastapi import Path, Body
from typing import Dict

# Asegurarse que los nuevos schemas estén importados:
from app.schemas.ai_client import (
    # ... imports existentes ...
    CampaignPromptUpdate,
    CampaignPromptResponse,
    AllCampaignPromptsResponse,
)
```

---

## Tests

**Archivo**: `backend/tests/test_campaign_prompts.py`

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_all_campaign_prompts(client: AsyncClient, active_client):
    """Test obtener todas las instrucciones"""
    response = await client.get("/api/v1/settings/ai-clients/active/campaign-prompts")
    assert response.status_code == 200
    data = response.json()
    assert "client_id" in data
    assert "prompts" in data

@pytest.mark.asyncio
async def test_get_campaign_prompt(client: AsyncClient, active_client):
    """Test obtener instrucciones de una campaña"""
    response = await client.get(
        "/api/v1/settings/ai-clients/active/campaign-prompts/navidad"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["campaign_id"] == "navidad"

@pytest.mark.asyncio
async def test_update_campaign_prompt(client: AsyncClient, active_client):
    """Test actualizar instrucciones"""
    response = await client.patch(
        "/api/v1/settings/ai-clients/active/campaign-prompts/navidad",
        json={"instructions": "Tono festivo y navideño"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["instructions"] == "Tono festivo y navideño"

@pytest.mark.asyncio
async def test_delete_campaign_prompt(client: AsyncClient, active_client):
    """Test eliminar instrucciones"""
    # Primero crear
    await client.patch(
        "/api/v1/settings/ai-clients/active/campaign-prompts/test",
        json={"instructions": "Test instructions"}
    )

    # Luego eliminar
    response = await client.delete(
        "/api/v1/settings/ai-clients/active/campaign-prompts/test"
    )
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_no_active_client(client: AsyncClient):
    """Test error cuando no hay cliente activo"""
    # Asumiendo que no hay cliente activo
    response = await client.get(
        "/api/v1/settings/ai-clients/active/campaign-prompts/navidad"
    )
    # Debería retornar 404 si no hay cliente activo
```

---

## Verificación

```bash
# 1. Ejecutar tests
cd /var/www/mediaflow-v2/backend
source venv/bin/activate
pytest tests/test_campaign_prompts.py -v

# 2. Verificar endpoints en Swagger
# Abrir: http://localhost:3001/api/docs
# Buscar: /settings/ai-clients/active/campaign-prompts

# 3. Test manual con curl
curl -X GET http://localhost:3001/api/v1/settings/ai-clients/active/campaign-prompts

curl -X PATCH http://localhost:3001/api/v1/settings/ai-clients/active/campaign-prompts/navidad \
  -H "Content-Type: application/json" \
  -d '{"instructions": "Tono festivo y navideño"}'
```

---

## Checklist

- [ ] Schemas creados en `ai_client.py`
- [ ] Endpoint GET /active/campaign-prompts implementado
- [ ] Endpoint GET /active/campaign-prompts/{campaign_id} implementado
- [ ] Endpoint PATCH /active/campaign-prompts/{campaign_id} implementado
- [ ] Endpoint DELETE /active/campaign-prompts/{campaign_id} implementado
- [ ] Imports agregados
- [ ] Tests escritos
- [ ] Tests pasando
- [ ] Endpoints visibles en Swagger
- [ ] Test manual exitoso

---

## Siguiente Fase

Una vez completada esta fase, continuar con **Fase 2: Modificar Generación AI**.
