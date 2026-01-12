# Sistema de Perfiles de Cliente - Plan Maestro de Implementación

**Versión**: 1.0
**Fecha**: 2025-01-09
**Estado**: Planificación

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Problema Actual](#2-problema-actual)
3. [Solución Propuesta](#3-solución-propuesta)
4. [Decisiones de Arquitectura](#4-decisiones-de-arquitectura)
5. [Modelo de Datos](#5-modelo-de-datos)
6. [Cambios en Backend](#6-cambios-en-backend)
7. [Cambios en Frontend](#7-cambios-en-frontend)
8. [Fases de Desarrollo](#8-fases-de-desarrollo)
9. [Casos de Uso](#9-casos-de-uso)
10. [Riesgos y Mitigaciones](#10-riesgos-y-mitigaciones)

---

## 1. Resumen Ejecutivo

### Objetivo
Implementar un sistema donde las **instrucciones de IA por campaña estén vinculadas al cliente activo**, evitando mezclas de contexto y permitiendo que usuarios sin acceso a Settings puedan editar instrucciones de campaña.

### Problema Principal
Actualmente, el contexto del cliente (AIClient) y las instrucciones de campaña (Category.ai_instructions) están **desconectados**. Esto causa que al cambiar de cliente activo, las campañas mantengan instrucciones de otro cliente.

### Solución
Mover las instrucciones de campaña **desde Category hacia AIClient.custom_prompts**, creando un paquete coherente donde todo el contexto de un cliente (general + por campaña) vive en un solo lugar.

### Niveles de Acceso

| Rol | Settings | Campaigns |
|-----|----------|-----------|
| **Admin** | ✅ Cambiar cliente activo, configurar todo | ✅ Acceso completo |
| **Marketing** | ❌ Sin acceso | ✅ Editar instrucciones de campaña (del cliente activo) |

---

## 2. Problema Actual

### 2.1 Arquitectura Actual (Problemática)

```
┌─────────────────────────────────────────────────────────────────┐
│                    ESTADO ACTUAL                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   AIClient (Settings)              Category (Campaigns)          │
│   ┌──────────────────┐             ┌──────────────────┐         │
│   │ id: supermercado │             │ id: navidad      │         │
│   │ context: "..."   │      ❌     │ ai_instructions: │         │
│   │ is_default: true │─── SIN ────│ "Instrucciones   │         │
│   └──────────────────┘    LINK    │  de farmacia!"   │ ← ERROR │
│                                    └──────────────────┘         │
│   ┌──────────────────┐                                          │
│   │ id: farmacia     │             Las instrucciones de la      │
│   │ context: "..."   │             campaña pueden pertenecer    │
│   │ is_default: false│             a CUALQUIER cliente          │
│   └──────────────────┘                                          │
│                                                                  │
│   RESULTADO: Mezcla de contextos no deseada                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Flujo Actual (Con Problemas)

1. Admin activa cliente "Supermercado" en Settings
2. Usuario entra a campaña "Navidad"
3. Campaña tiene `ai_instructions` de "Farmacia" (de una sesión anterior)
4. Al generar audio: contexto de Supermercado + instrucciones de Farmacia = **MEZCLA**

### 2.3 Campos Involucrados

| Modelo | Campo | Ubicación Actual | Problema |
|--------|-------|------------------|----------|
| AIClient | context | Settings | ✅ OK |
| AIClient | custom_prompts | Settings | ⚠️ Subutilizado |
| Category | ai_instructions | Campaign | ❌ Desvinculado de cliente |

---

## 3. Solución Propuesta

### 3.1 Nueva Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                    ESTADO PROPUESTO                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   AIClient (TODO el contexto del cliente)                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ id: supermercado                                        │   │
│   │ name: "Supermercado Líder"                              │   │
│   │ context: "Somos Supermercado Líder, la cadena..."       │   │
│   │ is_default: true                                        │   │
│   │                                                          │   │
│   │ custom_prompts: {  ← AQUÍ van las instrucciones         │   │
│   │   "navidad": "Tono festivo, ofertas navideñas...",      │   │
│   │   "fiestas_patrias": "Tono patriota, asados...",        │   │
│   │   "pedidos": "Mencionar nombre del cliente...",         │   │
│   │   "ofertas": "Destacar precios y descuentos..."         │   │
│   │ }                                                        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│   AIClient                                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ id: farmacia                                            │   │
│   │ name: "Farmacias Cruz Verde"                            │   │
│   │ context: "Somos Farmacias Cruz Verde..."                │   │
│   │ is_default: false                                       │   │
│   │                                                          │   │
│   │ custom_prompts: {                                        │   │
│   │   "navidad": "Regalos saludables, vitaminas...",        │   │
│   │   "ofertas": "Medicamentos con descuento...",           │   │
│   │   "pedidos": "Retiro en mostrador..."                   │   │
│   │ }                                                        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│   Category (Solo metadatos de la campaña)                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ id: navidad                                             │   │
│   │ name: "Navidad"                                         │   │
│   │ icon: "🎄"                                              │   │
│   │ color: "#FF0000"                                        │   │
│   │ ai_instructions: NULL  ← YA NO SE USA                   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Beneficios

| Beneficio | Descripción |
|-----------|-------------|
| **Coherencia garantizada** | Todo el contexto de un cliente está en UN objeto |
| **Cambio automático** | Al activar cliente, todas las instrucciones cambian |
| **Sin mezclas** | Imposible tener contexto de un cliente con instrucciones de otro |
| **Backup simple** | Exportar AIClient = exportar toda la configuración |
| **Multiempresa** | Perfecto para conglomerados con múltiples marcas |

### 3.3 Nuevo Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│                       NUEVO FLUJO                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Admin en Settings:                                          │
│     ┌─────────────────────────────────────────────────────┐     │
│     │ Clientes:                                           │     │
│     │ ● Supermercado Líder  [ACTIVO]                     │     │
│     │ ○ Farmacias Cruz Verde                              │     │
│     │ ○ Jumbo                                             │     │
│     │                                                     │     │
│     │ [Configurar cliente seleccionado]                   │     │
│     └─────────────────────────────────────────────────────┘     │
│                                                                  │
│  2. Marketing en Campaigns (sin acceso a Settings):             │
│     ┌─────────────────────────────────────────────────────┐     │
│     │ 🏪 Cliente: Supermercado Líder     (solo lectura)  │     │
│     │                                                     │     │
│     │ Campaña: Navidad                                    │     │
│     │                                                     │     │
│     │ Instrucciones IA:                                   │     │
│     │ ┌─────────────────────────────────────────────┐    │     │
│     │ │ Tono festivo, ofertas navideñas...          │    │     │
│     │ └─────────────────────────────────────────────┘    │     │
│     │                                       [Guardar]    │     │
│     └─────────────────────────────────────────────────────┘     │
│                                                                  │
│  3. Al Guardar:                                                  │
│     → Se guarda en: AIClient["supermercado"].custom_prompts[    │
│                       "navidad"                                  │
│                     ]                                            │
│     → El cliente activo se determina automáticamente            │
│                                                                  │
│  4. Al Generar Audio:                                           │
│     → Contexto: AIClient["supermercado"].context                │
│     → Instrucciones: AIClient["supermercado"].custom_prompts[   │
│                        campaign_id                               │
│                      ]                                           │
│     → 100% coherente, sin mezclas                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Decisiones de Arquitectura

### 4.1 Usar custom_prompts Existente

```
┌─────────────────────────────────────────────────────────────────┐
│        DECISIÓN: Reutilizar AIClient.custom_prompts             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  El campo custom_prompts YA EXISTE en el modelo AIClient        │
│  pero está subutilizado.                                        │
│                                                                  │
│  Estructura actual (poco usada):                                │
│  custom_prompts: {                                              │
│    "ofertas": "...",     ← Categoría genérica                   │
│    "eventos": "..."      ← Categoría genérica                   │
│  }                                                               │
│                                                                  │
│  Nueva estructura (por campaign_id):                            │
│  custom_prompts: {                                              │
│    "navidad": "...",           ← ID de campaña                  │
│    "fiestas_patrias": "...",   ← ID de campaña                  │
│    "pedidos": "...",           ← ID de campaña                  │
│    "ofertas": "..."            ← ID de campaña                  │
│  }                                                               │
│                                                                  │
│  BENEFICIO: No requiere migración de BD, solo cambio de uso     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Deprecar Category.ai_instructions

```
┌─────────────────────────────────────────────────────────────────┐
│        DECISIÓN: Deprecar (no eliminar) ai_instructions         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Category.ai_instructions seguirá existiendo pero:              │
│                                                                  │
│  Fase 1: Ignorar                                                │
│  - El sistema lee de AIClient.custom_prompts[campaign_id]       │
│  - Category.ai_instructions se ignora                           │
│  - Migración: copiar valores existentes a cliente activo        │
│                                                                  │
│  Fase 2 (opcional futura): Eliminar                             │
│  - Crear migración para eliminar columna                        │
│  - Limpiar código legacy                                        │
│                                                                  │
│  BENEFICIO: Rollback fácil si hay problemas                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Permisos por Ubicación

```
┌─────────────────────────────────────────────────────────────────┐
│        DECISIÓN: Control de acceso por ruta, no por rol         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  En lugar de implementar sistema de roles complejo:             │
│                                                                  │
│  /settings/*     → Solo admins tienen acceso (futuro)           │
│                    Pueden cambiar cliente activo                 │
│                    Pueden editar contexto global                 │
│                                                                  │
│  /campaigns/*    → Todos con acceso                             │
│                    NO pueden cambiar cliente activo              │
│                    SÍ pueden editar instrucciones de campaña    │
│                                                                  │
│  El cliente activo se muestra en Campaigns pero es READ-ONLY    │
│                                                                  │
│  BENEFICIO: Simple de implementar, sin sistema de permisos      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.4 Edición Híbrida (Settings + Campaigns)

```
┌─────────────────────────────────────────────────────────────────┐
│        DECISIÓN: Permitir edición desde ambos lugares           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SETTINGS (vista global):                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Cliente: Supermercado                                    │   │
│  │                                                          │   │
│  │ Contexto General: [textarea]                             │   │
│  │                                                          │   │
│  │ Instrucciones por Campaña:                               │   │
│  │ ├─ 🎄 Navidad: "Tono festivo..."           [Editar]     │   │
│  │ ├─ 🇨🇱 Fiestas: "Tono patriota..."         [Editar]     │   │
│  │ └─ 📦 Pedidos: "Mencionar nombre..."       [Editar]     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  CAMPAIGNS (vista individual):                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 🏪 Cliente: Supermercado              (solo lectura)    │   │
│  │                                                          │   │
│  │ Campaña: Navidad                                         │   │
│  │                                                          │   │
│  │ Instrucciones IA:                                        │   │
│  │ ┌─────────────────────────────────────────────────┐     │   │
│  │ │ Tono festivo, ofertas navideñas...              │     │   │
│  │ └─────────────────────────────────────────────────┘     │   │
│  │                                          [Guardar]      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Ambos editan el MISMO dato:                                    │
│  AIClient.custom_prompts[campaign_id]                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Modelo de Datos

### 5.1 AIClient (Existente - Sin cambios de schema)

```python
# backend/app/models/ai_client.py
class AIClient(Base, TimestampMixin):
    __tablename__ = "ai_clients"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    context = Column(Text, nullable=False)           # Contexto global
    category = Column(String(50), default="general")
    active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)      # Cliente activo
    order = Column(Integer, default=0)
    settings = Column(JSON, nullable=True)
    custom_prompts = Column(JSON, nullable=True)     # ← AQUÍ van las instrucciones

    # custom_prompts estructura:
    # {
    #   "navidad": "Instrucciones para Navidad...",
    #   "fiestas_patrias": "Instrucciones para Fiestas...",
    #   "pedidos": "Instrucciones para Pedidos...",
    #   ...
    # }
```

### 5.2 Category (Existente - Campo deprecado)

```python
# backend/app/models/category.py
class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(10), nullable=True)
    color = Column(String(7), nullable=True)
    order = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    ai_instructions = Column(Text, nullable=True)    # ← DEPRECADO (no eliminar aún)
```

### 5.3 Flujo de Datos

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO DE DATOS                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  GUARDAR INSTRUCCIONES (desde Campaigns):                       │
│  ───────────────────────────────────────                        │
│                                                                  │
│  1. Frontend: PATCH /api/v1/ai-clients/active/campaign-prompts  │
│     Body: { campaign_id: "navidad", instructions: "..." }       │
│                                                                  │
│  2. Backend:                                                     │
│     a. Obtener cliente activo (is_default=true)                 │
│     b. Actualizar custom_prompts[campaign_id] = instructions    │
│     c. Guardar AIClient                                         │
│                                                                  │
│  LEER INSTRUCCIONES (al generar audio):                         │
│  ─────────────────────────────────────                          │
│                                                                  │
│  1. Frontend: POST /api/v1/ai/generate                          │
│     Body: { context: "...", campaign_id: "navidad", ... }       │
│                                                                  │
│  2. Backend:                                                     │
│     a. Obtener cliente activo                                   │
│     b. Leer client.custom_prompts.get("navidad", "")            │
│     c. Combinar: client.context + campaign_instructions         │
│     d. Enviar a Claude                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Cambios en Backend

### 6.1 Nuevos Endpoints

```python
# backend/app/api/v1/endpoints/settings/ai_clients.py

# NUEVO: Obtener instrucciones de campaña del cliente activo
@router.get("/active/campaign-prompts/{campaign_id}")
async def get_active_client_campaign_prompt(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Obtiene las instrucciones de una campaña específica
    del cliente actualmente activo.

    Returns:
        {
            "client_id": "supermercado",
            "client_name": "Supermercado Líder",
            "campaign_id": "navidad",
            "instructions": "Tono festivo..."
        }
    """

# NUEVO: Actualizar instrucciones de campaña del cliente activo
@router.patch("/active/campaign-prompts/{campaign_id}")
async def update_active_client_campaign_prompt(
    campaign_id: str,
    request: CampaignPromptUpdate,  # { instructions: str }
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Actualiza las instrucciones de una campaña específica
    en el cliente actualmente activo.

    Solo requiere el campaign_id y las nuevas instrucciones.
    El cliente activo se determina automáticamente.
    """

# NUEVO: Listar todas las instrucciones del cliente activo
@router.get("/active/campaign-prompts")
async def get_active_client_all_prompts(
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Obtiene todas las instrucciones de campaña del cliente activo.

    Returns:
        {
            "client_id": "supermercado",
            "client_name": "Supermercado Líder",
            "prompts": {
                "navidad": "Tono festivo...",
                "fiestas_patrias": "Tono patriota...",
                ...
            }
        }
    """
```

### 6.2 Modificar Endpoint de Generación AI

```python
# backend/app/api/v1/endpoints/ai.py

@router.post("/generate")
async def generate_announcements(
    request: GenerateAnnouncementsRequest,
    db: AsyncSession = Depends(get_db)
):
    # ANTES: Leía de Category.ai_instructions
    # campaign_instructions = category.ai_instructions

    # DESPUÉS: Lee de AIClient.custom_prompts
    active_client = await ai_client_manager.get_active_client(db)
    campaign_instructions = None

    if active_client and request.campaign_id:
        prompts = active_client.custom_prompts or {}
        campaign_instructions = prompts.get(request.campaign_id, "")

        if campaign_instructions:
            logger.info(f"📋 Loaded campaign instructions from client: "
                       f"{active_client.id} -> {request.campaign_id}")

    # Resto del código igual...
```

### 6.3 Nuevos Schemas

```python
# backend/app/schemas/ai_client.py

class CampaignPromptUpdate(BaseModel):
    """Request para actualizar instrucciones de campaña"""
    instructions: str = Field(..., min_length=0, max_length=5000)

class CampaignPromptResponse(BaseModel):
    """Response con instrucciones de una campaña"""
    client_id: str
    client_name: str
    campaign_id: str
    instructions: str

class AllCampaignPromptsResponse(BaseModel):
    """Response con todas las instrucciones del cliente"""
    client_id: str
    client_name: str
    prompts: Dict[str, str]
```

### 6.4 Script de Migración de Datos

```python
# backend/scripts/migrate_campaign_instructions.py
"""
Script para migrar instrucciones existentes de Category.ai_instructions
al cliente activo AIClient.custom_prompts.

Ejecutar UNA VEZ antes de desplegar la nueva versión.
"""

async def migrate_campaign_instructions():
    async with get_db_session() as db:
        # 1. Obtener cliente activo
        active_client = await ai_client_manager.get_active_client(db)
        if not active_client:
            print("❌ No hay cliente activo. Crear uno primero.")
            return

        # 2. Obtener todas las categorías con ai_instructions
        result = await db.execute(
            select(Category).where(Category.ai_instructions.isnot(None))
        )
        categories = result.scalars().all()

        # 3. Migrar a custom_prompts del cliente activo
        prompts = active_client.custom_prompts or {}
        migrated = 0

        for cat in categories:
            if cat.ai_instructions and cat.ai_instructions.strip():
                prompts[cat.id] = cat.ai_instructions
                migrated += 1
                print(f"✅ Migrado: {cat.id} -> {active_client.id}")

        # 4. Guardar
        active_client.custom_prompts = prompts
        await db.commit()

        print(f"\n📊 Migración completada: {migrated} instrucciones")
        print(f"   Cliente destino: {active_client.name} ({active_client.id})")
```

---

## 7. Cambios en Frontend

### 7.1 Nuevo Composable

```typescript
// frontend/src/composables/useClientCampaignPrompts.ts

import { ref, computed } from 'vue'
import apiClient from '@/api/client'

interface ActiveClientInfo {
  client_id: string
  client_name: string
}

export function useClientCampaignPrompts() {
  const activeClient = ref<ActiveClientInfo | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  /**
   * Obtiene info del cliente activo
   */
  async function loadActiveClient() {
    try {
      const response = await apiClient.get('/api/v1/settings/ai-clients/active')
      activeClient.value = {
        client_id: response.id,
        client_name: response.name
      }
    } catch (e) {
      console.error('Error loading active client:', e)
      activeClient.value = null
    }
  }

  /**
   * Obtiene instrucciones de una campaña del cliente activo
   */
  async function getCampaignInstructions(campaignId: string): Promise<string> {
    try {
      const response = await apiClient.get(
        `/api/v1/settings/ai-clients/active/campaign-prompts/${campaignId}`
      )
      return response.instructions || ''
    } catch (e) {
      console.error('Error loading campaign instructions:', e)
      return ''
    }
  }

  /**
   * Guarda instrucciones de una campaña en el cliente activo
   */
  async function saveCampaignInstructions(
    campaignId: string,
    instructions: string
  ): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      await apiClient.patch(
        `/api/v1/settings/ai-clients/active/campaign-prompts/${campaignId}`,
        { instructions }
      )
      return true
    } catch (e: any) {
      error.value = e.message || 'Error al guardar'
      return false
    } finally {
      isLoading.value = false
    }
  }

  return {
    activeClient,
    isLoading,
    error,
    loadActiveClient,
    getCampaignInstructions,
    saveCampaignInstructions
  }
}
```

### 7.2 Modificar AITrainingPanel

```vue
<!-- frontend/src/components/campaigns/components/AITrainingPanel.vue -->
<template>
  <CollapsiblePanel title="Entrenamiento IA" :default-open="!hasInstructions">
    <!-- Indicador de cliente activo (READ-ONLY) -->
    <div class="mb-4 p-3 bg-base-200 rounded-lg">
      <div class="flex items-center gap-2">
        <span class="text-lg">🏪</span>
        <div>
          <div class="text-sm text-base-content/60">Cliente activo:</div>
          <div class="font-medium">{{ activeClientName }}</div>
        </div>
      </div>
      <p class="text-xs text-base-content/50 mt-2">
        Las instrucciones se guardarán para este cliente.
        Para cambiar de cliente, contacte al administrador.
      </p>
    </div>

    <!-- Textarea de instrucciones -->
    <textarea
      v-model="localInstructions"
      class="textarea textarea-bordered w-full h-32"
      placeholder="Ej: Usa un tono festivo y navideño..."
      @input="markDirty"
    />

    <!-- Botón guardar -->
    <div class="flex justify-end mt-3">
      <button
        class="btn btn-primary btn-sm"
        :disabled="!isDirty || isSaving"
        @click="handleSave"
      >
        <span v-if="isSaving" class="loading loading-spinner loading-xs" />
        {{ isSaving ? 'Guardando...' : 'Guardar' }}
      </button>
    </div>
  </CollapsiblePanel>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useClientCampaignPrompts } from '@/composables/useClientCampaignPrompts'
import CollapsiblePanel from '@/components/shared/ui/CollapsiblePanel.vue'

const props = defineProps<{
  campaignId: string
}>()

const emit = defineEmits<{
  saved: []
}>()

const {
  activeClient,
  isLoading,
  loadActiveClient,
  getCampaignInstructions,
  saveCampaignInstructions
} = useClientCampaignPrompts()

const localInstructions = ref('')
const originalInstructions = ref('')
const isDirty = ref(false)
const isSaving = ref(false)

const activeClientName = computed(() =>
  activeClient.value?.client_name || 'Cargando...'
)

const hasInstructions = computed(() =>
  localInstructions.value.trim().length > 0
)

function markDirty() {
  isDirty.value = localInstructions.value !== originalInstructions.value
}

async function handleSave() {
  isSaving.value = true
  const success = await saveCampaignInstructions(
    props.campaignId,
    localInstructions.value
  )
  isSaving.value = false

  if (success) {
    originalInstructions.value = localInstructions.value
    isDirty.value = false
    emit('saved')
  }
}

onMounted(async () => {
  await loadActiveClient()
  const instructions = await getCampaignInstructions(props.campaignId)
  localInstructions.value = instructions
  originalInstructions.value = instructions
})
</script>
```

### 7.3 Nuevo Panel en Settings (AIClientManager)

```vue
<!-- Agregar sección de instrucciones por campaña en AIClientEditor.vue -->
<template>
  <!-- ... campos existentes ... -->

  <!-- Nueva sección: Instrucciones por Campaña -->
  <CollapsiblePanel
    title="Instrucciones por Campaña"
    :default-open="false"
    class="mt-6"
  >
    <p class="text-sm text-base-content/60 mb-4">
      Configure instrucciones específicas para cada campaña.
      Estas instrucciones se añaden al contexto general cuando se genera audio.
    </p>

    <div class="space-y-4">
      <div
        v-for="campaign in campaigns"
        :key="campaign.id"
        class="border border-base-300 rounded-lg p-4"
      >
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xl">{{ campaign.icon }}</span>
          <span class="font-medium">{{ campaign.name }}</span>
        </div>

        <textarea
          v-model="campaignPrompts[campaign.id]"
          class="textarea textarea-bordered textarea-sm w-full h-20"
          :placeholder="`Instrucciones específicas para ${campaign.name}...`"
        />
      </div>
    </div>

    <div class="text-xs text-base-content/50 mt-4">
      💡 Tip: Deje vacío para usar solo el contexto general.
    </div>
  </CollapsiblePanel>
</template>
```

### 7.4 Estructura de Archivos Nueva/Modificada

```
frontend/src/
├── composables/
│   └── useClientCampaignPrompts.ts          # NUEVO
│
├── components/
│   ├── campaigns/
│   │   └── components/
│   │       └── AITrainingPanel.vue          # MODIFICADO
│   │
│   └── settings/
│       └── ai-clients/
│           └── components/
│               └── AIClientEditor.vue       # MODIFICADO (agregar sección)
│
└── types/
    └── ai-client.ts                         # MODIFICADO (agregar tipos)
```

---

## 8. Fases de Desarrollo

### Fase 1: Backend - Nuevos Endpoints
**Duración estimada**: 1 sesión
**Archivo**: `docs/phases/CLIENT_PROFILE_PHASE_1.md`

```
Tareas:
□ Crear schemas para campaign prompts
□ Implementar GET /active/campaign-prompts/{campaign_id}
□ Implementar PATCH /active/campaign-prompts/{campaign_id}
□ Implementar GET /active/campaign-prompts (listar todas)
□ Tests de endpoints
□ Documentación OpenAPI
```

### Fase 2: Backend - Modificar Generación AI
**Duración estimada**: 1 sesión
**Archivo**: `docs/phases/CLIENT_PROFILE_PHASE_2.md`

```
Tareas:
□ Modificar /api/v1/ai/generate para leer de AIClient.custom_prompts
□ Crear script de migración de datos existentes
□ Ejecutar migración en ambiente de desarrollo
□ Tests de generación con nueva lógica
□ Logging mejorado para debugging
```

### Fase 3: Frontend - Composable y AITrainingPanel
**Duración estimada**: 1 sesión
**Archivo**: `docs/phases/CLIENT_PROFILE_PHASE_3.md`

```
Tareas:
□ Crear useClientCampaignPrompts composable
□ Modificar AITrainingPanel para usar nuevo composable
□ Agregar indicador de cliente activo (read-only)
□ Tests de flujo de guardado
□ Verificar que cambios se reflejan correctamente
```

### Fase 4: Frontend - Settings Integration
**Duración estimada**: 1 sesión
**Archivo**: `docs/phases/CLIENT_PROFILE_PHASE_4.md`

```
Tareas:
□ Agregar sección "Instrucciones por Campaña" en AIClientEditor
□ Cargar lista de campañas disponibles
□ Implementar edición de prompts desde Settings
□ Sincronización bidireccional (Settings ↔ Campaigns)
□ UI/UX polish
```

### Fase 5: Testing y Documentación
**Duración estimada**: 1 sesión
**Archivo**: `docs/phases/CLIENT_PROFILE_PHASE_5.md`

```
Tareas:
□ Test E2E: crear cliente → configurar campañas → generar audio
□ Test E2E: cambiar cliente activo → verificar cambio de instrucciones
□ Test E2E: editar desde Campaigns → verificar en Settings
□ Actualizar CLAUDE.md con nueva arquitectura
□ Documentación de usuario final
```

### Diagrama de Fases

```
Fase 1          Fase 2          Fase 3          Fase 4          Fase 5
────────────────────────────────────────────────────────────────────────►

[Endpoints]     [AI Generate]   [Campaigns UI]  [Settings UI]   [Testing]
    ⏳              ⏳              ⏳              ⏳              ⏳

GET/PATCH       Modificar       Composable      Sección nueva   E2E tests
campaign-       ai.py           AITraining      en AIClient     Documentación
prompts         Script          Panel           Editor
                migración

    │               │               │               │               │
    ▼               ▼               ▼               ▼               ▼
[API Ready]     [Gen Works]     [Campaigns OK]  [Settings OK]   [Complete]
```

---

## 9. Casos de Uso

### 9.1 Caso: Conglomerado con Múltiples Marcas

```
ESCENARIO:
Cencosud tiene: Jumbo, Santa Isabel, Paris, Easy

CONFIGURACIÓN EN SETTINGS:
┌─────────────────────────────────────────────────────────────────┐
│ Clientes AI:                                                    │
│ ● Jumbo (ACTIVO)                                                │
│ ○ Santa Isabel                                                  │
│ ○ Paris                                                         │
│ ○ Easy                                                          │
└─────────────────────────────────────────────────────────────────┘

CADA CLIENTE TIENE SUS PROPIAS INSTRUCCIONES:
┌─────────────────────────────────────────────────────────────────┐
│ Jumbo:                                                          │
│ - Navidad: "Ofertas de canastas navideñas premium..."           │
│ - Pedidos: "Jumbo te informa que tu pedido está listo..."       │
│                                                                  │
│ Santa Isabel:                                                    │
│ - Navidad: "Precios bajos para tu cena navideña..."             │
│ - Pedidos: "Santa Isabel: retira tu compra en caja rápida..."   │
└─────────────────────────────────────────────────────────────────┘

USO:
1. Admin activa "Jumbo" en Settings
2. Marketing de Jumbo entra a Campaigns
3. Ve "Cliente: Jumbo" (no puede cambiar)
4. Edita instrucciones de "Navidad"
5. Todo coherente: contexto Jumbo + instrucciones Jumbo
```

### 9.2 Caso: Usuario de Marketing sin Acceso a Settings

```
ESCENARIO:
María trabaja en Marketing de Cruz Verde
No tiene acceso a Settings (área de IT)
Necesita ajustar instrucciones para campaña de analgésicos

FLUJO:
┌─────────────────────────────────────────────────────────────────┐
│ María entra a /campaigns                                        │
│                                                                  │
│ Ve: 🏪 Cliente: Cruz Verde (solo lectura)                       │
│                                                                  │
│ Abre campaña "Ofertas"                                          │
│                                                                  │
│ Panel de Entrenamiento IA:                                      │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ Esta semana tenemos oferta especial de analgésicos:         ││
│ │ - Paracetamol 500mg con 30% de descuento                    ││
│ │ - Ibuprofeno 400mg 2x1                                      ││
│ │ - Mencionar que la oferta es válida hasta el domingo        ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                  [Guardar] ✓    │
│                                                                  │
│ María guarda → Se guarda en Cruz Verde.custom_prompts["ofertas"]│
│                                                                  │
│ Genera audio → Contexto Cruz Verde + instrucciones de ofertas  │
│ = 100% coherente                                                │
└─────────────────────────────────────────────────────────────────┘
```

### 9.3 Caso: Cambio de Cliente Activo

```
ESCENARIO:
Sistema estaba configurado para "Supermercado"
Ahora se necesita usar para "Farmacia"

ANTES (problema actual):
- Admin cambia a "Farmacia" en Settings
- Campañas siguen con instrucciones de "Supermercado"
- Mezcla de contextos

DESPUÉS (solución):
┌─────────────────────────────────────────────────────────────────┐
│ 1. Admin va a Settings > AI Clients                             │
│                                                                  │
│ 2. Activa "Farmacia"                                            │
│    ○ Supermercado                                               │
│    ● Farmacia (ACTIVO) ← click                                  │
│                                                                  │
│ 3. AUTOMÁTICAMENTE:                                             │
│    - Contexto global: "Somos Farmacia..."                       │
│    - Instrucciones Navidad: "Regalos saludables..."             │
│    - Instrucciones Ofertas: "Medicamentos con dto..."           │
│                                                                  │
│ 4. Usuario en Campaigns:                                        │
│    - Ve: 🏪 Cliente: Farmacia                                   │
│    - Instrucciones ya son las de Farmacia                       │
│    - Puede editar (se guarda en Farmacia)                       │
│                                                                  │
│ 5. Al generar: TODO es de Farmacia, sin mezclas                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Riesgos y Mitigaciones

### 10.1 Riesgos Técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Pérdida de datos en migración | Media | Alto | Script de migración con backup previo |
| custom_prompts muy grande | Baja | Medio | Límite de 5000 chars por instrucción |
| Conflictos de edición simultánea | Baja | Bajo | Last-write-wins (aceptable para este caso) |
| Performance con muchas campañas | Baja | Bajo | JSON en BD es eficiente |

### 10.2 Riesgos de UX

| Riesgo | Mitigación |
|--------|------------|
| Usuario no entiende qué cliente está activo | Indicador prominente y permanente |
| Confusión sobre dónde editar | Mensaje claro: "se guarda para cliente X" |
| Marketing quiere cambiar cliente | Mensaje: "contacte administrador" |

### 10.3 Checklist Pre-Deploy

```
□ Backup de base de datos
□ Script de migración probado en staging
□ Rollback plan documentado
□ Usuarios notificados del cambio
□ Documentación actualizada
```

### 10.4 Plan de Rollback

```
SI ALGO SALE MAL:

1. Category.ai_instructions NO se elimina
   → Los datos originales siguen ahí

2. Revertir cambio en ai.py
   → Volver a leer de Category.ai_instructions

3. Revertir frontend
   → AITrainingPanel vuelve a guardar en Category

4. Tiempo estimado de rollback: 15 minutos
```

---

## Apéndice: Resumen de Cambios

### Backend

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `endpoints/settings/ai_clients.py` | MODIFICAR | Agregar 3 endpoints nuevos |
| `endpoints/ai.py` | MODIFICAR | Leer de AIClient.custom_prompts |
| `schemas/ai_client.py` | MODIFICAR | Agregar schemas de campaign prompts |
| `scripts/migrate_campaign_instructions.py` | CREAR | Script de migración |

### Frontend

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `composables/useClientCampaignPrompts.ts` | CREAR | Nuevo composable |
| `campaigns/components/AITrainingPanel.vue` | MODIFICAR | Usar nuevo composable |
| `settings/ai-clients/components/AIClientEditor.vue` | MODIFICAR | Agregar sección campañas |

### Sin Cambios

- `models/ai_client.py` - Schema ya tiene custom_prompts
- `models/category.py` - ai_instructions queda (deprecado)
- Rutas de router
- Otros componentes

---

**Documento creado**: 2025-01-09
**Autor**: Claude AI Assistant
**Estado**: Listo para revisión
