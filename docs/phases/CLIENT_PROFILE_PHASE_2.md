# Fase 2: Backend - Modificar Generación AI

**Plan Maestro**: `CLIENT_PROFILE_SYSTEM.md`
**Dependencia**: Fase 1 completada
**Estado**: Pendiente

---

## Objetivo

Modificar el endpoint de generación de IA para que lea las instrucciones de campaña desde `AIClient.custom_prompts` en lugar de `Category.ai_instructions`.

---

## Tareas

### 2.1 Modificar Endpoint de Generación

**Archivo**: `backend/app/api/v1/endpoints/ai.py`

```python
# ANTES (código actual):
@router.post("/generate")
async def generate_announcements(
    request: GenerateAnnouncementsRequest,
    db: AsyncSession = Depends(get_db)
):
    # ...
    campaign_instructions = None
    if request.campaign_id:
        result = await db.execute(
            select(Category).filter(Category.id == request.campaign_id)
        )
        category = result.scalar_one_or_none()
        if category and category.ai_instructions:
            campaign_instructions = category.ai_instructions
            logger.info(f"📋 Loaded AI instructions from campaign: {request.campaign_id}")
    # ...


# DESPUÉS (nuevo código):
@router.post("/generate")
async def generate_announcements(
    request: GenerateAnnouncementsRequest,
    db: AsyncSession = Depends(get_db)
):
    # ...

    # Obtener cliente activo
    active_client = await ai_client_manager.get_active_client(db)
    active_client_id = active_client.id if active_client else None

    # NUEVO: Leer instrucciones de campaña desde AIClient.custom_prompts
    campaign_instructions = None
    if active_client and request.campaign_id:
        prompts = active_client.custom_prompts or {}
        campaign_instructions = prompts.get(request.campaign_id, "")

        if campaign_instructions:
            logger.info(
                f"📋 Loaded campaign instructions from client: "
                f"{active_client.id} -> campaign: {request.campaign_id}"
            )
        else:
            logger.info(
                f"ℹ️ No campaign instructions found for: "
                f"{active_client.id} -> campaign: {request.campaign_id}"
            )

    # DEPRECADO: Ya no leemos de Category.ai_instructions
    # (mantener comentado por si necesitamos rollback)
    # if request.campaign_id:
    #     result = await db.execute(
    #         select(Category).filter(Category.id == request.campaign_id)
    #     )
    #     category = result.scalar_one_or_none()
    #     if category and category.ai_instructions:
    #         campaign_instructions = category.ai_instructions

    # Resto del código igual...
    suggestions = await claude_service.generate_announcements(
        context=request.context,
        category=request.category,
        tone=request.tone,
        duration=request.duration,
        keywords=request.keywords,
        client_context=active_client.context if active_client else None,
        campaign_instructions=campaign_instructions,  # ← Ahora viene de AIClient
    )

    return GenerateAnnouncementsResponse(
        suggestions=suggestions,
        model=claude_service.model,
        active_client_id=active_client_id
    )
```

### 2.2 Agregar Import del Manager

```python
# En la parte superior de ai.py, verificar que existe:
from app.services.ai.client_manager import ai_client_manager
```

### 2.3 Crear Script de Migración de Datos

**Archivo**: `backend/scripts/migrate_campaign_instructions.py`

```python
#!/usr/bin/env python3
"""
Script de migración: Category.ai_instructions → AIClient.custom_prompts

Este script copia las instrucciones de campaña existentes desde
Category.ai_instructions al campo custom_prompts del cliente activo.

USO:
    cd /var/www/mediaflow-v2/backend
    source venv/bin/activate
    python scripts/migrate_campaign_instructions.py

IMPORTANTE:
    - Hacer backup de la base de datos ANTES de ejecutar
    - Ejecutar UNA SOLA VEZ antes de desplegar la nueva versión
    - El script es idempotente (puede ejecutarse múltiples veces sin problema)
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.category import Category
from app.models.ai_client import AIClient


async def migrate_campaign_instructions():
    """Migra instrucciones de Category a AIClient activo."""

    print("=" * 60)
    print("MIGRACIÓN: Category.ai_instructions → AIClient.custom_prompts")
    print("=" * 60)

    # Crear conexión
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # 1. Obtener cliente activo
        result = await db.execute(
            select(AIClient).where(AIClient.is_default == True)
        )
        active_client = result.scalar_one_or_none()

        if not active_client:
            print("\n❌ ERROR: No hay cliente activo (is_default=True)")
            print("   Por favor, configure un cliente activo primero.")
            return False

        print(f"\n✅ Cliente activo encontrado: {active_client.name} ({active_client.id})")

        # 2. Obtener categorías con instrucciones
        result = await db.execute(
            select(Category).where(
                Category.ai_instructions.isnot(None),
                Category.ai_instructions != ""
            )
        )
        categories = result.scalars().all()

        if not categories:
            print("\nℹ️ No hay categorías con ai_instructions para migrar.")
            return True

        print(f"\n📋 Encontradas {len(categories)} categorías con instrucciones:")

        # 3. Preparar custom_prompts
        prompts = active_client.custom_prompts or {}
        migrated = 0
        skipped = 0

        for cat in categories:
            instructions = cat.ai_instructions.strip()
            if not instructions:
                continue

            # Verificar si ya existe
            if cat.id in prompts:
                print(f"   ⏭️  {cat.id}: Ya existe en custom_prompts (saltado)")
                skipped += 1
                continue

            # Migrar
            prompts[cat.id] = instructions
            migrated += 1
            preview = instructions[:50] + "..." if len(instructions) > 50 else instructions
            print(f"   ✅ {cat.id}: \"{preview}\"")

        # 4. Guardar
        if migrated > 0:
            active_client.custom_prompts = prompts
            await db.commit()
            print(f"\n💾 Guardado en: {active_client.id}.custom_prompts")

        # 5. Resumen
        print("\n" + "=" * 60)
        print("RESUMEN DE MIGRACIÓN")
        print("=" * 60)
        print(f"   Cliente destino: {active_client.name} ({active_client.id})")
        print(f"   Instrucciones migradas: {migrated}")
        print(f"   Instrucciones saltadas (ya existían): {skipped}")
        print(f"   Total en custom_prompts: {len(prompts)}")

        if migrated > 0:
            print("\n✅ Migración completada exitosamente")
        else:
            print("\nℹ️ No se realizaron cambios")

        return True

    await engine.dispose()


async def show_current_state():
    """Muestra el estado actual de las instrucciones."""

    print("\n" + "=" * 60)
    print("ESTADO ACTUAL")
    print("=" * 60)

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # Categorías con instrucciones
        result = await db.execute(
            select(Category).where(
                Category.ai_instructions.isnot(None),
                Category.ai_instructions != ""
            )
        )
        categories = result.scalars().all()

        print(f"\n📁 Category.ai_instructions ({len(categories)} con datos):")
        for cat in categories:
            preview = cat.ai_instructions[:40] + "..." if len(cat.ai_instructions) > 40 else cat.ai_instructions
            print(f"   - {cat.id}: \"{preview}\"")

        # Clientes con custom_prompts
        result = await db.execute(select(AIClient))
        clients = result.scalars().all()

        print(f"\n👤 AIClient.custom_prompts:")
        for client in clients:
            prompts = client.custom_prompts or {}
            status = "⭐ ACTIVO" if client.is_default else ""
            print(f"   - {client.id} ({len(prompts)} prompts) {status}")
            for campaign_id, instructions in prompts.items():
                preview = instructions[:30] + "..." if len(instructions) > 30 else instructions
                print(f"      └─ {campaign_id}: \"{preview}\"")

    await engine.dispose()


async def main():
    """Punto de entrada principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrar instrucciones de Category a AIClient"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo mostrar qué se haría, sin ejecutar"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Mostrar estado actual sin migrar"
    )

    args = parser.parse_args()

    if args.status:
        await show_current_state()
        return

    if args.dry_run:
        print("🔍 MODO DRY-RUN: Solo mostrando estado actual")
        await show_current_state()
        print("\n💡 Para ejecutar la migración, quitar --dry-run")
        return

    # Confirmar antes de migrar
    print("\n⚠️  ADVERTENCIA: Este script modificará la base de datos.")
    print("   Asegúrese de tener un backup antes de continuar.")
    response = input("\n¿Desea continuar? (yes/no): ")

    if response.lower() != "yes":
        print("Operación cancelada.")
        return

    success = await migrate_campaign_instructions()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
```

### 2.4 Agregar Logging Mejorado

**Archivo**: `backend/app/services/ai/claude.py`

```python
# En el método generate_announcements, agregar logging detallado:

async def generate_announcements(
    self,
    context: str,
    # ... otros params ...
    campaign_instructions: Optional[str] = None,
) -> List[Suggestion]:
    # Log de contexto
    logger.info("=" * 50)
    logger.info("🤖 GENERACIÓN DE ANUNCIOS")
    logger.info("=" * 50)
    logger.info(f"   Contexto usuario: {context[:100]}...")
    logger.info(f"   Tono: {tone}")
    logger.info(f"   Duración: {duration}s")

    if client_context:
        logger.info(f"   ✅ Cliente activo: contexto de {len(client_context)} chars")
    else:
        logger.info("   ⚠️ Sin contexto de cliente activo")

    if campaign_instructions:
        logger.info(f"   ✅ Instrucciones campaña: {len(campaign_instructions)} chars")
        logger.info(f"      Preview: {campaign_instructions[:80]}...")
    else:
        logger.info("   ℹ️ Sin instrucciones de campaña")

    # Resto del código...
```

---

## Tests

**Archivo**: `backend/tests/test_ai_generate_with_client.py`

```python
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_generate_uses_client_custom_prompts(
    client: AsyncClient,
    active_client_with_prompts
):
    """
    Test que la generación usa custom_prompts del cliente activo
    en lugar de Category.ai_instructions
    """
    # Setup: cliente activo tiene custom_prompts["navidad"]
    # active_client_with_prompts fixture debe configurar esto

    with patch('app.services.ai.claude.claude_service') as mock_claude:
        mock_claude.generate_announcements = AsyncMock(return_value=[
            {"text": "Test suggestion", "word_count": 10, "char_count": 50}
        ])

        response = await client.post(
            "/api/v1/ai/generate",
            json={
                "context": "ofertas navideñas",
                "campaign_id": "navidad",
                "tone": "entusiasta"
            }
        )

        assert response.status_code == 200

        # Verificar que se llamó con las instrucciones del cliente
        call_args = mock_claude.generate_announcements.call_args
        assert call_args.kwargs.get("campaign_instructions") is not None


@pytest.mark.asyncio
async def test_generate_without_campaign_id(client: AsyncClient, active_client):
    """Test generación sin campaign_id (sin instrucciones de campaña)"""
    with patch('app.services.ai.claude.claude_service') as mock_claude:
        mock_claude.generate_announcements = AsyncMock(return_value=[])

        response = await client.post(
            "/api/v1/ai/generate",
            json={
                "context": "mensaje genérico",
                "tone": "profesional"
            }
        )

        assert response.status_code == 200

        # Sin campaign_id, no debe haber instrucciones de campaña
        call_args = mock_claude.generate_announcements.call_args
        campaign_instructions = call_args.kwargs.get("campaign_instructions")
        assert campaign_instructions is None or campaign_instructions == ""


@pytest.mark.asyncio
async def test_generate_with_empty_custom_prompts(
    client: AsyncClient,
    active_client_no_prompts
):
    """Test cuando el cliente no tiene instrucciones para esa campaña"""
    with patch('app.services.ai.claude.claude_service') as mock_claude:
        mock_claude.generate_announcements = AsyncMock(return_value=[])

        response = await client.post(
            "/api/v1/ai/generate",
            json={
                "context": "test",
                "campaign_id": "campaña_sin_instrucciones",
                "tone": "profesional"
            }
        )

        assert response.status_code == 200
```

---

## Verificación

```bash
# 1. Ver estado actual
cd /var/www/mediaflow-v2/backend
source venv/bin/activate
python scripts/migrate_campaign_instructions.py --status

# 2. Dry run de migración
python scripts/migrate_campaign_instructions.py --dry-run

# 3. Ejecutar migración (con backup previo!)
python scripts/migrate_campaign_instructions.py

# 4. Ejecutar tests
pytest tests/test_ai_generate_with_client.py -v

# 5. Test manual de generación
curl -X POST http://localhost:3001/api/v1/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "context": "ofertas de navidad",
    "campaign_id": "navidad",
    "tone": "entusiasta",
    "duration": 10
  }'

# 6. Verificar logs
tail -f logs/mediaflow.log | grep -E "(📋|🤖|GENERACIÓN)"
```

---

## Checklist

- [ ] Endpoint `/api/v1/ai/generate` modificado
- [ ] Código legacy comentado (no eliminado)
- [ ] Import de `ai_client_manager` verificado
- [ ] Script de migración creado
- [ ] Script probado con `--dry-run`
- [ ] Script probado con `--status`
- [ ] Migración ejecutada en desarrollo
- [ ] Logging mejorado agregado
- [ ] Tests escritos
- [ ] Tests pasando
- [ ] Generación funciona correctamente

---

## Rollback Plan

Si algo sale mal:

```python
# En ai.py, descomentar el código legacy:

# ROLLBACK: Volver a leer de Category.ai_instructions
if request.campaign_id:
    result = await db.execute(
        select(Category).filter(Category.id == request.campaign_id)
    )
    category = result.scalar_one_or_none()
    if category and category.ai_instructions:
        campaign_instructions = category.ai_instructions

# Y comentar el código nuevo que lee de AIClient.custom_prompts
```

---

## Siguiente Fase

Una vez completada esta fase, continuar con **Fase 3: Frontend - Composable y AITrainingPanel**.
