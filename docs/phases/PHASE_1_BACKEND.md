# Fase 1: Backend - Migración y Endpoints

**Estado**: ✅ Completado (2025-12-21)
**Dependencia**: Ninguna (puede ejecutarse en paralelo con Fase 0)
**Principio**: Cambios ADITIVOS, no modificar comportamiento existente

---

## Objetivo

Preparar el backend para soportar el Campaign Manager:
1. Agregar campo `ai_instructions` a Category
2. Crear endpoint para campañas con conteo de audios
3. Modificar ClaudeService para aceptar instrucciones de campaña

---

## Regla de Oro

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Todos los cambios son ADITIVOS:                               │
│   • Nuevo campo nullable (no rompe registros existentes)        │
│   • Nuevo endpoint (no modifica existentes)                     │
│   • Nuevo parámetro OPCIONAL (backward compatible)              │
│                                                                 │
│   ANTES de cada cambio:                                         │
│   $ python -c "from app.main import app; print('OK')"           │
│                                                                 │
│   DESPUÉS de cada cambio:                                       │
│   $ python -c "from app.main import app; print('OK')"           │
│   $ pytest tests/ -v (si hay tests)                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tareas

### Tarea 1.1: Migración - Agregar ai_instructions a Category

**Archivo a modificar**: `backend/app/models/category.py`

**Cambio**:
```python
# Agregar DESPUÉS de los campos existentes
ai_instructions = Column(Text, nullable=True)  # NUEVO
```

**Comando de migración**:
```bash
cd /var/www/mediaflow-v2/backend
source venv/bin/activate
alembic revision --autogenerate -m "add ai_instructions to category"
alembic upgrade head
```

**Verificación**:
```bash
sqlite3 mediaflow.db ".schema categories"
# Debe mostrar: ai_instructions TEXT
```

**Impacto en sistema existente**: NINGUNO
- Campo nullable, no afecta registros existentes
- Settings/Categories sigue funcionando
- Library sigue funcionando

---

### Tarea 1.2: Schema - CampaignResponse

**Archivo nuevo**: `backend/app/schemas/campaign.py`

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CampaignResponse(BaseModel):
    """Campaña = Category + audio_count + has_ai_training"""
    id: str
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    order: int
    active: bool
    ai_instructions: Optional[str] = None

    # Campos calculados
    audio_count: int
    has_ai_training: bool

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CampaignAITrainingUpdate(BaseModel):
    """Para PATCH /campaigns/:id/ai-training"""
    ai_instructions: str


class CampaignListResponse(BaseModel):
    """Lista de campañas"""
    campaigns: list[CampaignResponse]
    total: int
```

---

### Tarea 1.3: Endpoint - GET /api/v1/campaigns

**Archivo nuevo**: `backend/app/api/v1/endpoints/campaigns.py`

**Funcionalidad**:
- Listar todas las categorías activas
- Incluir conteo de audios por categoría
- Incluir indicador de entrenamiento IA

```python
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.category import Category
from app.models.audio import AudioMessage
from app.schemas.campaign import CampaignResponse, CampaignListResponse

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=CampaignListResponse)
async def get_campaigns(
    db: AsyncSession = Depends(get_db),
    active_only: bool = True
):
    """
    Lista todas las campañas (categorías) con conteo de audios.

    Cada campaña incluye:
    - audio_count: número de audios asociados
    - has_ai_training: si tiene ai_instructions definido
    """
    # Query base
    query = select(Category)
    if active_only:
        query = query.filter(Category.active == True)
    query = query.order_by(Category.order.asc())

    result = await db.execute(query)
    categories = result.scalars().all()

    # Contar audios por categoría
    campaigns = []
    for cat in categories:
        # Subquery para contar audios
        count_query = select(func.count(AudioMessage.id)).filter(
            AudioMessage.category_id == cat.id
        )
        count_result = await db.execute(count_query)
        audio_count = count_result.scalar() or 0

        campaigns.append(CampaignResponse(
            id=cat.id,
            name=cat.name,
            icon=cat.icon,
            color=cat.color,
            order=cat.order,
            active=cat.active,
            ai_instructions=cat.ai_instructions,
            audio_count=audio_count,
            has_ai_training=bool(cat.ai_instructions),
            created_at=cat.created_at,
            updated_at=cat.updated_at,
        ))

    return CampaignListResponse(campaigns=campaigns, total=len(campaigns))
```

---

### Tarea 1.4: Endpoint - GET /api/v1/campaigns/:id

```python
@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene una campaña por ID con su conteo de audios."""
    result = await db.execute(
        select(Category).filter(Category.id == campaign_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Contar audios
    count_result = await db.execute(
        select(func.count(AudioMessage.id)).filter(
            AudioMessage.category_id == campaign_id
        )
    )
    audio_count = count_result.scalar() or 0

    return CampaignResponse(
        id=category.id,
        name=category.name,
        icon=category.icon,
        color=category.color,
        order=category.order,
        active=category.active,
        ai_instructions=category.ai_instructions,
        audio_count=audio_count,
        has_ai_training=bool(category.ai_instructions),
        created_at=category.created_at,
        updated_at=category.updated_at,
    )
```

---

### Tarea 1.5: Endpoint - PATCH /api/v1/campaigns/:id/ai-training

```python
@router.patch("/{campaign_id}/ai-training", response_model=CampaignResponse)
async def update_ai_training(
    campaign_id: str,
    data: CampaignAITrainingUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza las instrucciones de IA para una campaña.

    Estas instrucciones se agregan al prompt cuando se generan
    sugerencias para esta campaña específica.
    """
    result = await db.execute(
        select(Category).filter(Category.id == campaign_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Campaign not found")

    category.ai_instructions = data.ai_instructions
    await db.commit()
    await db.refresh(category)

    # Retornar con audio_count
    count_result = await db.execute(
        select(func.count(AudioMessage.id)).filter(
            AudioMessage.category_id == campaign_id
        )
    )
    audio_count = count_result.scalar() or 0

    return CampaignResponse(
        id=category.id,
        name=category.name,
        icon=category.icon,
        color=category.color,
        order=category.order,
        active=category.active,
        ai_instructions=category.ai_instructions,
        audio_count=audio_count,
        has_ai_training=bool(category.ai_instructions),
        created_at=category.created_at,
        updated_at=category.updated_at,
    )
```

---

### Tarea 1.6: Endpoint - GET /api/v1/campaigns/:id/audios

```python
@router.get("/{campaign_id}/audios")
async def get_campaign_audios(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Lista los audios de una campaña específica."""
    # Verificar que la campaña existe
    result = await db.execute(
        select(Category).filter(Category.id == campaign_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Obtener audios
    query = (
        select(AudioMessage)
        .filter(AudioMessage.category_id == campaign_id)
        .order_by(AudioMessage.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(query)
    audios = result.scalars().all()

    # Contar total
    count_result = await db.execute(
        select(func.count(AudioMessage.id)).filter(
            AudioMessage.category_id == campaign_id
        )
    )
    total = count_result.scalar() or 0

    return {
        "audios": [serialize_audio(a) for a in audios],
        "total": total,
        "limit": limit,
        "offset": offset
    }
```

---

### Tarea 1.7: Registrar router en API

**Archivo a modificar**: `backend/app/api/v1/api.py`

**Agregar**:
```python
from app.api.v1.endpoints import campaigns

# En la sección de includes
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
```

---

### Tarea 1.8: Modificar ClaudeService (CUIDADOSAMENTE)

**Archivo a modificar**: `backend/app/services/ai/claude.py`

**Cambio**: Agregar parámetro OPCIONAL `campaign_instructions`

**ANTES** (ejemplo simplificado):
```python
async def generate_suggestions(
    self,
    context: str,
    tone: str = "profesional",
    ...
) -> list[str]:
    system_prompt = self._build_system_prompt(tone)
    # ...
```

**DESPUÉS**:
```python
async def generate_suggestions(
    self,
    context: str,
    tone: str = "profesional",
    campaign_instructions: str | None = None,  # NUEVO - OPCIONAL
    ...
) -> list[str]:
    system_prompt = self._build_system_prompt(tone)

    # NUEVO: Agregar instrucciones de campaña si existen
    if campaign_instructions:
        system_prompt += f"\n\n## Instrucciones específicas de la campaña:\n{campaign_instructions}"

    # ... resto sin cambios
```

**Verificación de backward compatibility**:
```python
# Llamada existente (Dashboard) - SIGUE FUNCIONANDO
await claude_service.generate_suggestions(context="oferta", tone="profesional")

# Llamada nueva (Campaigns)
await claude_service.generate_suggestions(
    context="oferta",
    tone="profesional",
    campaign_instructions="Usa vocabulario patriota para Fiestas Patrias"
)
```

---

### Tarea 1.9: Modificar endpoint /api/v1/ai/generate (OPCIONAL)

Si el frontend de Campaigns usará el mismo endpoint de AI:

**Archivo**: `backend/app/api/v1/endpoints/ai.py`

**Agregar parámetro opcional**:
```python
@router.post("/generate")
async def generate_suggestions(
    request: AISuggestRequest,
    campaign_id: str | None = None,  # NUEVO - OPCIONAL
    db: AsyncSession = Depends(get_db)
):
    campaign_instructions = None

    # NUEVO: Obtener instrucciones si hay campaign_id
    if campaign_id:
        result = await db.execute(
            select(Category).filter(Category.id == campaign_id)
        )
        category = result.scalar_one_or_none()
        if category:
            campaign_instructions = category.ai_instructions

    # Llamar a ClaudeService con instrucciones
    suggestions = await claude_service.generate_suggestions(
        context=request.context,
        tone=request.tone,
        campaign_instructions=campaign_instructions,  # NUEVO
        ...
    )

    return {"suggestions": suggestions}
```

---

## Verificación Final

### Checklist de Migración

```
□ Migración creada sin errores
□ Migración aplicada (alembic upgrade head)
□ Campo ai_instructions visible en DB
□ Registros existentes no afectados
```

### Checklist de Endpoints

```
□ GET /api/v1/campaigns → 200 + lista de campañas
□ GET /api/v1/campaigns/:id → 200 + campaña con audio_count
□ PATCH /api/v1/campaigns/:id/ai-training → 200 + actualizado
□ GET /api/v1/campaigns/:id/audios → 200 + lista de audios
```

### Checklist de NO-REGRESIÓN

```
□ GET /api/v1/categories → Sigue funcionando
□ GET /api/v1/settings/categories → Sigue funcionando
□ POST /api/v1/ai/generate (sin campaign_id) → Sigue funcionando
□ Dashboard → Genera sugerencias correctamente
□ Library → Muestra categorías correctamente
```

### Test Manual

```bash
# Probar nuevo endpoint
curl http://localhost:3001/api/v1/campaigns

# Probar actualizar ai_training
curl -X PATCH http://localhost:3001/api/v1/campaigns/navidad/ai-training \
  -H "Content-Type: application/json" \
  -d '{"ai_instructions": "Usa vocabulario festivo y navideño"}'

# Probar generar con campaign_id
curl -X POST http://localhost:3001/api/v1/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"context": "ofertas de regalos", "campaign_id": "navidad"}'
```

---

## Estructura de Archivos Resultante

```
backend/app/
├── api/v1/
│   ├── api.py                   # MODIFICADO: +campaigns router
│   └── endpoints/
│       ├── campaigns.py         # NUEVO (~150 líneas)
│       └── ai.py                # MODIFICADO: +campaign_id param
│
├── models/
│   └── category.py              # MODIFICADO: +ai_instructions
│
├── schemas/
│   └── campaign.py              # NUEVO (~50 líneas)
│
├── services/ai/
│   └── claude.py                # MODIFICADO: +campaign_instructions param
│
└── alembic/versions/
    └── xxx_add_ai_instructions_to_category.py  # NUEVO
```

---

## Rollback Plan

Si algo sale mal:

```bash
# Revertir migración
alembic downgrade -1

# Revertir cambios en código
git checkout backend/app/models/category.py
git checkout backend/app/services/ai/claude.py
# etc.
```

---

## Implementación Completada (2025-12-21)

### Archivos Creados
- `backend/app/schemas/campaign.py` - Schemas Pydantic para Campaign Manager
- `backend/app/api/v1/endpoints/campaigns.py` - Endpoints REST para campañas

### Archivos Modificados
- `backend/app/models/category.py` - Ya tenía `ai_instructions` (migración previa)
- `backend/app/api/v1/endpoints/ai.py` - Añadido `campaign_id` opcional a `GenerateAnnouncementsRequest`
- `backend/app/services/ai/claude.py` - Añadido parámetro `campaign_instructions` a `generate_announcements()`
- `backend/app/api/v1/api.py` - Incluido router de campaigns

### Endpoints Disponibles
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/campaigns` | GET | Lista campañas con audio_count |
| `/api/v1/campaigns/{id}` | GET | Detalle de campaña |
| `/api/v1/campaigns` | POST | Crear nueva campaña |
| `/api/v1/campaigns/{id}` | PATCH | Actualizar (incluye ai_instructions) |
| `/api/v1/campaigns/{id}/audios` | GET | Audios de la campaña |

### Verificación
```bash
# Todos los endpoints funcionan
curl http://localhost:3001/api/v1/campaigns
curl http://localhost:3001/api/v1/campaigns/musica
curl -X PATCH http://localhost:3001/api/v1/campaigns/musica -H "Content-Type: application/json" -d '{"ai_instructions": "..."}'
curl http://localhost:3001/api/v1/campaigns/pedidos/audios

# Endpoints existentes no afectados
curl http://localhost:3001/api/v1/categories  # OK
curl http://localhost:3001/api/v1/settings/categories  # OK
```

---

**Siguiente fase**: `PHASE_2_CAMPAIGN_LIST.md` - Página 1 del Campaign Manager
