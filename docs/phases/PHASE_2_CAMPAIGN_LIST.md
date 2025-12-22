# Fase 2: Campaign List - Página Principal

**Estado**: ✅ Completado (2025-12-21)
**Dependencias**: Fase 1 (Backend)
**Riesgo**: BAJO (código nuevo, no modifica existente)

---

## Objetivo

Crear la página principal del Campaign Manager que muestra un grid de todas las campañas con:
- Card por campaña con icono, nombre, conteo de audios
- Indicador de entrenamiento IA
- Modal para crear nueva campaña
- Navegación a detalle de campaña

---

## Diseño Visual de Referencia

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌─ HEADER ────────────────────────────────────────────────────────────────┐│
│  │  🎯 Campañas 2025                                        [+ Nueva]      ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ┌─ GRID DE CAMPAÑAS ──────────────────────────────────────────────────────┐│
│  │   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌─────────────┐ ││
│  │   │      🎄       │ │      🎆       │ │      🐰       │ │     👧      │ ││
│  │   │    Navidad    │ │   Año Nuevo   │ │    Pascua     │ │  Día Niño   │ ││
│  │   │   12 audios   │ │   8 audios    │ │   5 audios    │ │  0 audios   │ ││
│  │   │   🧠 ✓        │ │   🧠 ✓        │ │   🧠 ✗        │ │  🧠 ✗       │ ││
│  │   └───────────────┘ └───────────────┘ └───────────────┘ └─────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Tareas

### Tarea 2.1: Crear tipos TypeScript

**Archivo nuevo**: `frontend/src/types/campaign.ts`

```typescript
/**
 * Tipos para el módulo Campaign Manager
 */

export interface Campaign {
  id: string
  name: string
  icon: string | null
  color: string | null
  order: number
  active: boolean
  ai_instructions: string | null
  audio_count: number
  has_ai_training: boolean
  created_at: string | null
  updated_at: string | null
}

export interface CampaignCreate {
  id: string           // slug generado desde name
  name: string
  icon?: string
  color?: string
}

export interface CampaignAITrainingUpdate {
  ai_instructions: string
}

export interface CampaignListResponse {
  campaigns: Campaign[]
  total: number
}
```

---

### Tarea 2.2: Crear campaignStore

**Archivo nuevo**: `frontend/src/components/campaigns/stores/campaignStore.ts`

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Campaign, CampaignCreate, CampaignListResponse } from '@/types/campaign'
import { apiClient } from '@/api/client'

export const useCampaignStore = defineStore('campaigns', () => {
  // State
  const campaigns = ref<Campaign[]>([])
  const currentCampaign = ref<Campaign | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const activeCampaigns = computed(() =>
    campaigns.value.filter(c => c.active)
  )

  const campaignsWithTraining = computed(() =>
    campaigns.value.filter(c => c.has_ai_training)
  )

  const totalAudios = computed(() =>
    campaigns.value.reduce((sum, c) => sum + c.audio_count, 0)
  )

  // Actions
  async function fetchCampaigns() {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiClient.get<CampaignListResponse>('/campaigns')
      campaigns.value = response.data.campaigns
    } catch (err) {
      error.value = 'Error al cargar campañas'
      console.error('fetchCampaigns error:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCampaign(id: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiClient.get<Campaign>(`/campaigns/${id}`)
      currentCampaign.value = response.data
      return response.data
    } catch (err) {
      error.value = 'Campaña no encontrada'
      console.error('fetchCampaign error:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function createCampaign(data: CampaignCreate) {
    isLoading.value = true
    error.value = null
    try {
      // Usar endpoint existente de categories
      const response = await apiClient.post('/settings/categories', data)
      await fetchCampaigns() // Refresh list
      return response.data
    } catch (err) {
      error.value = 'Error al crear campaña'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateAITraining(id: string, instructions: string) {
    try {
      const response = await apiClient.patch<Campaign>(
        `/campaigns/${id}/ai-training`,
        { ai_instructions: instructions }
      )
      // Update local state
      if (currentCampaign.value?.id === id) {
        currentCampaign.value = response.data
      }
      const index = campaigns.value.findIndex(c => c.id === id)
      if (index !== -1) {
        campaigns.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = 'Error al guardar entrenamiento'
      throw err
    }
  }

  function clearCurrent() {
    currentCampaign.value = null
  }

  return {
    // State
    campaigns,
    currentCampaign,
    isLoading,
    error,
    // Getters
    activeCampaigns,
    campaignsWithTraining,
    totalAudios,
    // Actions
    fetchCampaigns,
    fetchCampaign,
    createCampaign,
    updateAITraining,
    clearCurrent
  }
})
```

**Tamaño**: ~100 líneas

---

### Tarea 2.3: Crear CampaignCard.vue

**Archivo nuevo**: `frontend/src/components/campaigns/components/CampaignCard.vue`

```vue
<script setup lang="ts">
import type { Campaign } from '@/types/campaign'

interface Props {
  campaign: Campaign
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: [campaign: Campaign]
}>()

function handleClick() {
  emit('click', props.campaign)
}
</script>

<template>
  <div
    class="card bg-base-200 cursor-pointer transition-all duration-200 hover:scale-105 hover:shadow-lg"
    :style="campaign.color ? { borderTopColor: campaign.color, borderTopWidth: '4px' } : {}"
    @click="handleClick"
  >
    <div class="card-body items-center text-center p-6">
      <!-- Icono grande -->
      <div class="text-5xl mb-2">
        {{ campaign.icon || '📁' }}
      </div>

      <!-- Nombre -->
      <h3 class="card-title text-lg">
        {{ campaign.name }}
      </h3>

      <!-- Conteo de audios -->
      <p class="text-sm opacity-70">
        {{ campaign.audio_count }} {{ campaign.audio_count === 1 ? 'audio' : 'audios' }}
      </p>

      <!-- Indicador de entrenamiento IA -->
      <div class="mt-2">
        <span
          v-if="campaign.has_ai_training"
          class="badge badge-success badge-sm gap-1"
        >
          🧠 ✓
        </span>
        <span
          v-else
          class="badge badge-ghost badge-sm gap-1 opacity-50"
        >
          🧠 ✗
        </span>
      </div>
    </div>
  </div>
</template>
```

**Tamaño**: ~60 líneas

---

### Tarea 2.4: Crear NewCampaignModal.vue

**Archivo nuevo**: `frontend/src/components/campaigns/modals/NewCampaignModal.vue`

```vue
<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { CampaignCreate } from '@/types/campaign'

interface Props {
  isOpen: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:isOpen': [value: boolean]
  'create': [data: CampaignCreate]
}>()

// Form state
const name = ref('')
const selectedIcon = ref('')
const selectedColor = ref('')

// Emojis disponibles
const icons = [
  '🎄', '🎆', '🐰', '👧', '💐', '👔', '🇨🇱', '📚',
  '💕', '🏷️', '🔥', '🛒', '🎁', '💰', '⭐', '🎉',
  '📦', '💝', '🦃', '☀️', '🎃', '❄️', '🌸', '🎓'
]

// Colores disponibles
const colors = [
  { name: 'Rojo', value: '#DC2626' },
  { name: 'Naranja', value: '#EA580C' },
  { name: 'Amarillo', value: '#CA8A04' },
  { name: 'Verde', value: '#16A34A' },
  { name: 'Azul', value: '#2563EB' },
  { name: 'Violeta', value: '#9333EA' },
  { name: 'Rosa', value: '#DB2777' },
  { name: 'Gris', value: '#6B7280' }
]

// Generar ID desde nombre
const generatedId = computed(() => {
  return name.value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remove accents
    .replace(/[^a-z0-9\s]/g, '')     // Remove special chars
    .replace(/\s+/g, '_')            // Spaces to underscore
    .slice(0, 30)
})

// Validación
const isValid = computed(() => {
  return name.value.trim().length >= 2
})

// Reset on close
watch(() => props.isOpen, (open) => {
  if (!open) {
    name.value = ''
    selectedIcon.value = ''
    selectedColor.value = ''
  }
})

function close() {
  emit('update:isOpen', false)
}

function handleCreate() {
  if (!isValid.value) return

  const data: CampaignCreate = {
    id: generatedId.value,
    name: name.value.trim(),
    icon: selectedIcon.value || undefined,
    color: selectedColor.value || undefined
  }

  emit('create', data)
  close()
}
</script>

<template>
  <dialog class="modal" :class="{ 'modal-open': isOpen }">
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-4">🎯 Nueva Campaña</h3>

      <!-- Nombre -->
      <div class="form-control mb-4">
        <label class="label">
          <span class="label-text">Nombre de la campaña</span>
        </label>
        <input
          v-model="name"
          type="text"
          class="input input-bordered"
          placeholder="Ej: Cyber Monday"
          maxlength="50"
        />
        <label v-if="generatedId" class="label">
          <span class="label-text-alt opacity-50">ID: {{ generatedId }}</span>
        </label>
      </div>

      <!-- Selector de iconos -->
      <div class="form-control mb-4">
        <label class="label">
          <span class="label-text">Icono</span>
        </label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="icon in icons"
            :key="icon"
            type="button"
            class="btn btn-square btn-sm text-xl"
            :class="{ 'btn-primary': selectedIcon === icon, 'btn-ghost': selectedIcon !== icon }"
            @click="selectedIcon = selectedIcon === icon ? '' : icon"
          >
            {{ icon }}
          </button>
        </div>
      </div>

      <!-- Selector de colores -->
      <div class="form-control mb-6">
        <label class="label">
          <span class="label-text">Color</span>
        </label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="color in colors"
            :key="color.value"
            type="button"
            class="btn btn-circle btn-sm"
            :class="{ 'ring ring-primary ring-offset-2': selectedColor === color.value }"
            :style="{ backgroundColor: color.value }"
            :title="color.name"
            @click="selectedColor = selectedColor === color.value ? '' : color.value"
          />
        </div>
      </div>

      <!-- Actions -->
      <div class="modal-action">
        <button class="btn btn-ghost" @click="close">Cancelar</button>
        <button
          class="btn btn-primary"
          :disabled="!isValid"
          @click="handleCreate"
        >
          ✓ Crear Campaña
        </button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop" @click="close">
      <button>close</button>
    </form>
  </dialog>
</template>
```

**Tamaño**: ~140 líneas

---

### Tarea 2.5: Crear CampaignList.vue (Página Principal)

**Archivo nuevo**: `frontend/src/components/campaigns/CampaignList.vue`

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCampaignStore } from './stores/campaignStore'
import CampaignCard from './components/CampaignCard.vue'
import NewCampaignModal from './modals/NewCampaignModal.vue'
import type { Campaign, CampaignCreate } from '@/types/campaign'

const router = useRouter()
const store = useCampaignStore()

// Modal state
const showNewModal = ref(false)

// Load campaigns on mount
onMounted(() => {
  store.fetchCampaigns()
})

// Handlers
function handleCampaignClick(campaign: Campaign) {
  router.push(`/campaigns/${campaign.id}`)
}

async function handleCreateCampaign(data: CampaignCreate) {
  try {
    await store.createCampaign(data)
  } catch (error) {
    // Error handled in store
    console.error('Create campaign failed:', error)
  }
}

// Current year for header
const currentYear = new Date().getFullYear()
</script>

<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-2xl font-bold">
        🎯 Campañas {{ currentYear }}
      </h1>
      <button
        class="btn btn-primary"
        @click="showNewModal = true"
      >
        + Nueva
      </button>
    </div>

    <!-- Loading -->
    <div v-if="store.isLoading" class="flex justify-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <!-- Error -->
    <div v-else-if="store.error" class="alert alert-error">
      {{ store.error }}
    </div>

    <!-- Empty state -->
    <div
      v-else-if="store.campaigns.length === 0"
      class="text-center py-12 opacity-70"
    >
      <div class="text-5xl mb-4">📭</div>
      <p>No hay campañas aún</p>
      <button
        class="btn btn-primary btn-sm mt-4"
        @click="showNewModal = true"
      >
        Crear primera campaña
      </button>
    </div>

    <!-- Grid de campañas -->
    <div
      v-else
      class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4"
    >
      <CampaignCard
        v-for="campaign in store.campaigns"
        :key="campaign.id"
        :campaign="campaign"
        @click="handleCampaignClick"
      />
    </div>

    <!-- Leyenda -->
    <div v-if="store.campaigns.length > 0" class="mt-8 text-sm opacity-50">
      <span class="mr-4">🧠 ✓ = IA entrenada para esta campaña</span>
      <span>🧠 ✗ = Sin entrenamiento de IA</span>
    </div>

    <!-- Modal -->
    <NewCampaignModal
      v-model:isOpen="showNewModal"
      @create="handleCreateCampaign"
    />
  </div>
</template>
```

**Tamaño**: ~100 líneas

---

### Tarea 2.6: Configurar Router

**Archivo a modificar**: `frontend/src/router/index.ts`

**Agregar rutas**:
```typescript
// Campaigns
{
  path: '/campaigns',
  name: 'campaigns',
  component: () => import('@/components/campaigns/CampaignList.vue'),
  meta: { title: 'Campañas' }
},
{
  path: '/campaigns/:id',
  name: 'campaign-detail',
  component: () => import('@/components/campaigns/CampaignDetail.vue'),
  meta: { title: 'Detalle de Campaña' }
}
```

---

### Tarea 2.7: Agregar enlace en Sidebar

**Ubicación**: Componente de navegación lateral (identificar archivo exacto)

**Agregar**:
```vue
<router-link
  to="/campaigns"
  class="..."
  active-class="..."
>
  🎯 Campañas
</router-link>
```

---

## Estructura de Archivos Resultante

```
frontend/src/
├── components/
│   └── campaigns/
│       ├── CampaignList.vue              # Página principal (~100 líneas)
│       ├── CampaignDetail.vue            # Placeholder (Fase 3)
│       ├── components/
│       │   └── CampaignCard.vue          # Card individual (~60 líneas)
│       ├── modals/
│       │   └── NewCampaignModal.vue      # Modal crear (~140 líneas)
│       └── stores/
│           └── campaignStore.ts          # Store Pinia (~100 líneas)
│
├── types/
│   └── campaign.ts                       # Tipos TS (~40 líneas)
│
└── router/
    └── index.ts                          # +2 rutas
```

**Total Fase 2**: ~440 líneas nuevas

---

## Verificación Final

### Checklist Funcional

```
□ /campaigns carga sin errores
□ Grid muestra todas las categorías como campañas
□ Cada card muestra: icono, nombre, audio_count, indicador IA
□ Click en card navega a /campaigns/:id
□ Botón "+ Nueva" abre modal
□ Modal valida nombre mínimo 2 caracteres
□ Crear campaña agrega a la lista
□ Sidebar tiene enlace a Campañas
```

### Checklist de NO-REGRESIÓN

```
□ Dashboard sigue funcionando
□ Library sigue funcionando
□ Settings/Categories sigue funcionando
□ No hay errores en consola
□ npm run build pasa
```

---

## Notas de Implementación

### CampaignDetail.vue Placeholder

Crear archivo mínimo para que la ruta funcione:

```vue
<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<template>
  <div class="p-6">
    <h1>Campaña: {{ route.params.id }}</h1>
    <p class="opacity-50">Implementación en Fase 3</p>
  </div>
</template>
```

### Uso del endpoint de Campaigns

`createCampaign()` en el store usa `POST /api/v1/campaigns` (endpoint creado en Fase 1).

---

## Implementación Completada (2025-12-21)

### Archivos Creados

| Archivo | Descripción | Líneas |
|---------|-------------|--------|
| `types/campaign.ts` | Tipos TypeScript | ~60 |
| `campaigns/stores/campaignStore.ts` | Store Pinia | ~100 |
| `campaigns/components/CampaignCard.vue` | Card individual | ~60 |
| `campaigns/modals/NewCampaignModal.vue` | Modal crear | ~130 |
| `campaigns/CampaignList.vue` | Página principal | ~90 |
| `campaigns/CampaignDetail.vue` | Placeholder Fase 3 | ~60 |

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `router/index.ts` | +2 rutas (`/campaigns`, `/campaigns/:id`) |
| `common/NavigationHeader.vue` | +enlace "Campañas" con RocketLaunchIcon |

### Notas de Implementación

1. **El endpoint POST usa `/api/v1/campaigns`** - Diferente a lo planificado originalmente que sugería usar `/settings/categories`
2. **Fase 0 ya estaba implementada** - Los componentes `shared/` existían previamente
3. **apiClient devuelve `data` directamente** - No `response.data`, ajustado en el store

### Verificación

```bash
# Build exitoso
npm run build

# Chunks generados
campaignStore-DUpUrMqV.js (1.43 kB)
CampaignList-CH7E1uXK.js (5.67 kB)
CampaignDetail-DikCADzg.js (2.04 kB)
```

---

**Siguiente fase**: `PHASE_3_CAMPAIGN_DETAIL.md` - Layout y paneles del detalle
