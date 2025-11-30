# 📚 MediaFlowDemo - Library Module Technical Specification

**Proyecto:** MediaFlowDemo v2.1
**Documento:** 06-LIBRARY-TECHNICAL-SPEC
**Fecha:** 2025-11-29
**Versión:** 1.0

---

## 📋 Resumen Ejecutivo

El módulo **Library** (Biblioteca) es el centro de gestión de mensajes guardados. A diferencia del Dashboard que prioriza la generación rápida, Library se enfoca en **organización, categorización y acciones sobre mensajes existentes**.

### Diferencias Clave vs Sistema Legacy (v1)

| Aspecto | v1 (Legacy) | v2.1 (Nuevo) |
|---------|-------------|--------------|
| **Categorías** | Hardcoded (7 fijas) | Dinámicas (desde Settings) |
| **Favoritos** | No existe | Cross-category con filtro especial |
| **Vista** | Solo Grid | Grid + Lista (toggle) |
| **Editar** | Modifica original | "Editar en Dashboard" (copia) |
| **Arquitectura** | 1 archivo monolítico (1236 líneas) | Componentes modulares (~100 líneas c/u) |
| **Framework** | Vanilla JS + Event Bus | Vue 3 + Pinia + TypeScript |

---

## 🏗️ Arquitectura de Archivos

### Estructura Propuesta (Modular y Limpia)

```
frontend/src/components/library/
├── Library.vue                    # Container principal (~100 líneas)
│
├── components/
│   ├── LibraryHeader.vue          # Título + controles (~80 líneas)
│   ├── LibraryFilters.vue         # Búsqueda + filtros (~100 líneas)
│   ├── LibraryGrid.vue            # Vista grid de cards (~60 líneas)
│   ├── LibraryList.vue            # Vista lista/tabla (~80 líneas)
│   ├── ViewToggle.vue             # Switch Grid/Lista (~40 líneas)
│   ├── MessageCard.vue            # Card individual grid (~120 líneas)
│   ├── MessageRow.vue             # Fila individual lista (~80 líneas)
│   ├── EmptyState.vue             # Estado vacío (~40 líneas)
│   └── SelectionBar.vue           # Barra selección múltiple (~60 líneas)
│
├── modals/
│   ├── ScheduleModal.vue          # Modal programación (~200 líneas)
│   ├── UploadModal.vue            # Modal subir audio (~150 líneas)
│   └── DeleteConfirmModal.vue     # Confirmación eliminar (~60 líneas)
│
├── composables/
│   ├── useLibrary.ts              # Lógica principal lista
│   ├── useAudioPlayer.ts          # Reproducción inline
│   ├── useFileUpload.ts           # Carga de archivos
│   ├── useScheduling.ts           # Programación calendario
│   ├── useSelection.ts            # Selección múltiple
│   └── useFilters.ts              # Filtrado y búsqueda
│
├── stores/
│   └── libraryStore.ts            # Estado Pinia
│
├── services/
│   └── libraryApi.ts              # Llamadas API
│
├── types/
│   └── library.types.ts           # TypeScript interfaces
│
└── utils/
    └── formatters.ts              # Utilidades de formato
```

### Principios de Diseño

1. **Archivos pequeños** - Máximo ~200 líneas por componente
2. **Composables separados** - Lógica reutilizable fuera de componentes
3. **Store centralizado** - Pinia para estado global de library
4. **TypeScript 100%** - Type safety completo
5. **Categorías dinámicas** - Vienen del backend/settings, no hardcoded

---

## 🎯 Funciones a Implementar

### Prioridad Alta (Core)

| # | Función | Descripción | Componente |
|---|---------|-------------|------------|
| 1 | **Listado mensajes** | Grid + Lista con paginación | LibraryGrid, LibraryList |
| 2 | **Preview/Player** | Reproducir audio inline | useAudioPlayer |
| 3 | **Categorías dinámicas** | Dropdown con categorías de Settings | CategoryBadge |
| 4 | **Favoritos** | Toggle estrella cross-category | FavoriteButton |
| 5 | **Eliminar** | Individual + batch con confirmación | DeleteConfirmModal |
| 6 | **Búsqueda** | Full-text en nombre y contenido | LibraryFilters |

### Prioridad Media

| # | Función | Descripción | Componente |
|---|---------|-------------|------------|
| 7 | **Programar calendario** | Modal con 3 tipos de schedule | ScheduleModal |
| 8 | **Enviar a radio** | Reproducción inmediata en vivo | MessageCard actions |
| 9 | **Editar en Dashboard** | Copiar texto y navegar | useLibrary |
| 10 | **Subir audios externos** | Upload MP3/WAV con validación | UploadModal |
| 11 | **Selección múltiple** | Batch delete/categorize | useSelection |

### Prioridad Baja

| # | Función | Descripción | Componente |
|---|---------|-------------|------------|
| 12 | **Ordenamiento** | Por fecha, nombre, categoría | LibraryFilters |
| 13 | **Estadísticas** | Play count, radio count | MessageCard |
| 14 | **Drag & drop reorder** | Reordenar en grid | futuro |

---

## 📊 Modelo de Datos

### AudioMessage (TypeScript)

```typescript
// frontend/src/types/library.types.ts

export interface AudioMessage {
  id: number
  filename: string
  display_name: string
  original_text: string
  description?: string

  // Clasificación
  voice_id: string
  category_id: string | null      // Nullable - se asigna después
  is_favorite: boolean            // NEW v2.1

  // Audio
  duration: number                // Segundos
  file_size: number               // Bytes
  has_jingle: boolean

  // Metadatos
  priority: number
  play_count: number
  radio_count: number

  // Fechas
  created_at: string              // ISO 8601
  updated_at: string

  // Estado
  is_deleted: boolean             // Soft delete
}

export interface Category {
  id: string
  name: string                    // Editable desde Settings
  icon: string                    // Emoji
  color: string                   // Hex color
  order: number
  active: boolean
}

export interface LibraryFilters {
  search: string
  category_id: string | null      // null = todas
  is_favorite: boolean | null     // null = todas, true = solo favoritos
  sort_by: 'created_at' | 'display_name' | 'duration'
  sort_order: 'asc' | 'desc'
  page: number
  per_page: number
}

export interface LibraryState {
  messages: AudioMessage[]
  categories: Category[]
  filters: LibraryFilters
  selectedIds: Set<number>
  viewMode: 'grid' | 'list'
  isLoading: boolean
  total: number
  currentPage: number
}
```

### Schedule (para programación)

```typescript
export interface Schedule {
  id: number
  audio_message_id: number

  schedule_type: 'interval' | 'specific' | 'once'

  // Para interval
  interval_hours?: number
  interval_minutes?: number

  // Para specific/interval
  schedule_days?: number[]        // 0=Dom, 1=Lun, ..., 6=Sab
  schedule_times?: string[]       // ["09:00", "12:00", "18:00"]

  // Para once
  once_datetime?: string          // ISO 8601

  // Común
  start_date: string
  end_date?: string               // Opcional
  notes?: string
  is_active: boolean

  created_at: string
}
```

---

## 🔌 API Endpoints

### GET /api/v1/library

Lista mensajes con filtros y paginación.

```typescript
// Request
GET /api/v1/library?category_id=pedidos&is_favorite=true&search=oferta&sort_by=created_at&sort_order=desc&page=1&per_page=20

// Response
{
  "success": true,
  "data": {
    "messages": AudioMessage[],
    "total": 150,
    "page": 1,
    "per_page": 20,
    "total_pages": 8
  }
}
```

### GET /api/v1/library/{id}

Obtiene un mensaje específico.

```typescript
// Response
{
  "success": true,
  "data": AudioMessage
}
```

### PATCH /api/v1/library/{id}

Actualiza campos de un mensaje.

```typescript
// Request
{
  "display_name": "Nuevo nombre",      // Opcional
  "category_id": "ofertas",            // Opcional
  "is_favorite": true                  // Opcional
}

// Response
{
  "success": true,
  "data": AudioMessage
}
```

### DELETE /api/v1/library/{id}

Elimina un mensaje (soft delete).

```typescript
// Response
{
  "success": true,
  "message": "Mensaje eliminado"
}
```

### DELETE /api/v1/library/batch

Elimina múltiples mensajes.

```typescript
// Request
{
  "ids": [1, 2, 3, 4, 5]
}

// Response
{
  "success": true,
  "deleted_count": 5
}
```

### POST /api/v1/library/upload

Sube audio externo.

```typescript
// Request (multipart/form-data)
FormData {
  audio: File,                         // MP3, WAV, FLAC, AAC, OGG, M4A
  display_name?: string
}

// Validaciones
// - Tamaño máximo: 50 MB
// - Formatos: MP3, WAV, FLAC, AAC, OGG, M4A, Opus

// Response
{
  "success": true,
  "data": AudioMessage
}
```

### GET /api/v1/categories

Lista categorías activas.

```typescript
// Response
{
  "success": true,
  "data": Category[]
}
```

### POST /api/v1/schedules

Crea programación.

```typescript
// Request
{
  "audio_message_id": 123,
  "schedule_type": "interval",
  "interval_hours": 4,
  "schedule_days": [1, 2, 3, 4, 5],
  "schedule_times": ["09:00", "18:00"],
  "start_date": "2025-12-01",
  "end_date": "2025-12-31",
  "notes": "Campaña navideña"
}

// Response
{
  "success": true,
  "data": Schedule
}
```

### POST /api/v1/library/{id}/send-to-radio

Envía audio a reproducción inmediata.

```typescript
// Response
{
  "success": true,
  "message": "Audio enviado a la radio"
}
```

---

## 🎨 Componentes Vue

### Library.vue (Container Principal)

```vue
<template>
  <div class="library-container">
    <LibraryHeader
      @upload="showUploadModal = true"
      @toggle-selection="toggleSelectionMode"
    />

    <LibraryFilters
      v-model:filters="filters"
      :categories="categories"
    />

    <SelectionBar
      v-if="selectionMode"
      :selected-count="selectedIds.size"
      @delete="deleteSelected"
      @categorize="categorizeSelected"
      @cancel="cancelSelection"
    />

    <ViewToggle v-model="viewMode" />

    <LibraryGrid
      v-if="viewMode === 'grid'"
      :messages="messages"
      :selection-mode="selectionMode"
      :selected-ids="selectedIds"
      @play="playMessage"
      @toggle-favorite="toggleFavorite"
      @toggle-select="toggleSelect"
      @action="handleAction"
    />

    <LibraryList
      v-else
      :messages="messages"
      :selection-mode="selectionMode"
      :selected-ids="selectedIds"
      @play="playMessage"
      @toggle-favorite="toggleFavorite"
      @toggle-select="toggleSelect"
      @action="handleAction"
    />

    <EmptyState v-if="messages.length === 0 && !isLoading" />

    <!-- Modals -->
    <UploadModal
      v-model:open="showUploadModal"
      @uploaded="onUploaded"
    />

    <ScheduleModal
      v-model:open="showScheduleModal"
      :message="selectedMessage"
      @scheduled="onScheduled"
    />

    <DeleteConfirmModal
      v-model:open="showDeleteModal"
      :count="deleteCount"
      @confirm="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useLibraryStore } from '@/stores/libraryStore'
import { useAudioPlayer } from './composables/useAudioPlayer'
import { useSelection } from './composables/useSelection'

// Components
import LibraryHeader from './components/LibraryHeader.vue'
import LibraryFilters from './components/LibraryFilters.vue'
import LibraryGrid from './components/LibraryGrid.vue'
import LibraryList from './components/LibraryList.vue'
import ViewToggle from './components/ViewToggle.vue'
import SelectionBar from './components/SelectionBar.vue'
import EmptyState from './components/EmptyState.vue'
import UploadModal from './modals/UploadModal.vue'
import ScheduleModal from './modals/ScheduleModal.vue'
import DeleteConfirmModal from './modals/DeleteConfirmModal.vue'

const store = useLibraryStore()
const { playMessage, stopPlayback } = useAudioPlayer()
const { selectionMode, selectedIds, toggleSelect, clearSelection } = useSelection()

// State
const viewMode = ref<'grid' | 'list'>('grid')
const showUploadModal = ref(false)
const showScheduleModal = ref(false)
const showDeleteModal = ref(false)
const selectedMessage = ref<AudioMessage | null>(null)

// Computed
const messages = computed(() => store.messages)
const categories = computed(() => store.categories)
const filters = computed(() => store.filters)
const isLoading = computed(() => store.isLoading)

// Methods
const handleAction = (action: string, message: AudioMessage) => {
  switch (action) {
    case 'schedule':
      selectedMessage.value = message
      showScheduleModal.value = true
      break
    case 'edit-in-dashboard':
      editInDashboard(message)
      break
    case 'send-to-radio':
      sendToRadio(message)
      break
    case 'delete':
      selectedMessage.value = message
      showDeleteModal.value = true
      break
  }
}

// Load data on mount
onMounted(() => {
  store.fetchMessages()
  store.fetchCategories()
})
</script>
```

### MessageCard.vue (Card Grid)

```vue
<template>
  <div
    class="message-card"
    :class="{ 'selected': isSelected }"
    @click="selectionMode && emit('toggle-select', message.id)"
  >
    <!-- Checkbox (selection mode) -->
    <div v-if="selectionMode" class="selection-checkbox">
      <input
        type="checkbox"
        :checked="isSelected"
        @change="emit('toggle-select', message.id)"
      />
    </div>

    <!-- Header -->
    <div class="card-header">
      <h3 class="title">{{ message.display_name }}</h3>

      <!-- Favorite Button -->
      <button
        class="favorite-btn"
        :class="{ 'active': message.is_favorite }"
        @click.stop="emit('toggle-favorite', message.id)"
      >
        {{ message.is_favorite ? '★' : '☆' }}
      </button>
    </div>

    <!-- Category Badge -->
    <CategoryBadge
      :category-id="message.category_id"
      :categories="categories"
      @change="updateCategory"
    />

    <!-- Content Preview -->
    <p class="content-preview">
      {{ truncate(message.original_text, 100) }}
    </p>

    <!-- Audio Player -->
    <div class="player-row">
      <button
        class="play-btn"
        @click.stop="emit('play', message)"
      >
        {{ isPlaying ? '⏸' : '▶' }}
      </button>
      <span class="duration">{{ formatDuration(message.duration) }}</span>
    </div>

    <!-- Actions -->
    <div class="actions">
      <button @click.stop="emit('action', 'schedule', message)" title="Programar">
        📅
      </button>
      <button @click.stop="emit('action', 'send-to-radio', message)" title="Enviar a radio">
        📻
      </button>
      <button @click.stop="emit('action', 'edit-in-dashboard', message)" title="Editar copia">
        ✏️
      </button>
      <button @click.stop="emit('action', 'delete', message)" title="Eliminar">
        🗑️
      </button>
    </div>

    <!-- Meta -->
    <div class="meta">
      <span class="date">{{ formatDate(message.created_at) }}</span>
      <span class="voice">{{ getVoiceName(message.voice_id) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AudioMessage, Category } from '../types/library.types'
import CategoryBadge from './CategoryBadge.vue'
import { formatDuration, formatDate, truncate } from '../utils/formatters'

const props = defineProps<{
  message: AudioMessage
  categories: Category[]
  selectionMode: boolean
  isSelected: boolean
  isPlaying: boolean
}>()

const emit = defineEmits<{
  'play': [message: AudioMessage]
  'toggle-favorite': [id: number]
  'toggle-select': [id: number]
  'action': [action: string, message: AudioMessage]
}>()
</script>
```

### CategoryBadge.vue (Dropdown Categorías)

```vue
<template>
  <div class="category-badge-container" ref="containerRef">
    <button
      class="badge"
      :style="{ backgroundColor: category?.color || '#gray' }"
      @click="toggleDropdown"
    >
      {{ category?.icon || '📁' }} {{ category?.name || 'Sin categoría' }}
    </button>

    <div v-if="isOpen" class="dropdown">
      <button
        v-for="cat in categories"
        :key="cat.id"
        class="dropdown-item"
        :class="{ 'active': cat.id === categoryId }"
        @click="selectCategory(cat.id)"
      >
        <span :style="{ color: cat.color }">{{ cat.icon }}</span>
        {{ cat.name }}
        <span v-if="cat.id === categoryId">✓</span>
      </button>

      <button
        class="dropdown-item"
        :class="{ 'active': !categoryId }"
        @click="selectCategory(null)"
      >
        📁 Sin categoría
        <span v-if="!categoryId">✓</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onClickOutside } from '@vueuse/core'
import type { Category } from '../types/library.types'

const props = defineProps<{
  categoryId: string | null
  categories: Category[]
}>()

const emit = defineEmits<{
  'change': [categoryId: string | null]
}>()

const containerRef = ref<HTMLElement | null>(null)
const isOpen = ref(false)

const category = computed(() =>
  props.categories.find(c => c.id === props.categoryId)
)

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const selectCategory = (id: string | null) => {
  emit('change', id)
  isOpen.value = false
}

onClickOutside(containerRef, () => {
  isOpen.value = false
})
</script>
```

### ScheduleModal.vue (Programación)

```vue
<template>
  <dialog :open="open" class="modal">
    <div class="modal-content">
      <h2>Programar: {{ message?.display_name }}</h2>

      <!-- Tabs: Tipo de programación -->
      <div class="tabs">
        <button
          v-for="type in scheduleTypes"
          :key="type.id"
          :class="{ 'active': scheduleType === type.id }"
          @click="scheduleType = type.id"
        >
          {{ type.icon }} {{ type.label }}
        </button>
      </div>

      <!-- Interval Config -->
      <div v-if="scheduleType === 'interval'" class="config-section">
        <h3>Repetir cada:</h3>
        <div class="interval-inputs">
          <input v-model.number="intervalHours" type="number" min="0" max="23" />
          <span>horas</span>
          <input v-model.number="intervalMinutes" type="number" min="0" max="59" />
          <span>minutos</span>
        </div>

        <h3>En horario:</h3>
        <div class="time-range">
          <input v-model="startTime" type="time" />
          <span>a</span>
          <input v-model="endTime" type="time" />
        </div>

        <DaySelector v-model="selectedDays" />
      </div>

      <!-- Specific Config -->
      <div v-if="scheduleType === 'specific'" class="config-section">
        <h3>Días:</h3>
        <DaySelector v-model="selectedDays" />

        <h3>Horarios:</h3>
        <div v-for="(time, index) in specificTimes" :key="index" class="time-slot">
          <input v-model="specificTimes[index]" type="time" />
          <button @click="removeTime(index)">✕</button>
        </div>
        <button @click="addTime" class="btn-add">+ Agregar horario</button>
      </div>

      <!-- Once Config -->
      <div v-if="scheduleType === 'once'" class="config-section">
        <h3>Fecha y hora:</h3>
        <input v-model="onceDatetime" type="datetime-local" />
      </div>

      <!-- Common: Date Range -->
      <div class="date-range">
        <div>
          <label>Fecha inicio:</label>
          <input v-model="startDate" type="date" required />
        </div>
        <div>
          <label>Fecha fin (opcional):</label>
          <input v-model="endDate" type="date" />
        </div>
      </div>

      <!-- Notes -->
      <div class="notes">
        <label>Notas:</label>
        <textarea v-model="notes" rows="2"></textarea>
      </div>

      <!-- Actions -->
      <div class="modal-actions">
        <button @click="emit('update:open', false)" class="btn-cancel">
          Cancelar
        </button>
        <button @click="save" class="btn-save" :disabled="!isValid">
          Guardar Programación
        </button>
      </div>
    </div>
  </dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { AudioMessage, Schedule } from '../types/library.types'
import DaySelector from './DaySelector.vue'
import { libraryApi } from '../services/libraryApi'

const props = defineProps<{
  open: boolean
  message: AudioMessage | null
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'scheduled': [schedule: Schedule]
}>()

const scheduleTypes = [
  { id: 'interval', icon: '🔄', label: 'Intervalo' },
  { id: 'specific', icon: '🕐', label: 'Específico' },
  { id: 'once', icon: '📅', label: 'Una vez' }
]

const scheduleType = ref<'interval' | 'specific' | 'once'>('interval')
const intervalHours = ref(4)
const intervalMinutes = ref(0)
const startTime = ref('09:00')
const endTime = ref('18:00')
const selectedDays = ref([1, 2, 3, 4, 5]) // Lun-Vie
const specificTimes = ref(['09:00', '12:00', '18:00'])
const onceDatetime = ref('')
const startDate = ref('')
const endDate = ref('')
const notes = ref('')

const isValid = computed(() => {
  if (!startDate.value) return false
  if (scheduleType.value === 'interval') {
    return intervalHours.value > 0 || intervalMinutes.value > 0
  }
  if (scheduleType.value === 'specific') {
    return selectedDays.value.length > 0 && specificTimes.value.length > 0
  }
  if (scheduleType.value === 'once') {
    return !!onceDatetime.value
  }
  return false
})

const save = async () => {
  if (!props.message || !isValid.value) return

  const data: Partial<Schedule> = {
    audio_message_id: props.message.id,
    schedule_type: scheduleType.value,
    start_date: startDate.value,
    end_date: endDate.value || undefined,
    notes: notes.value || undefined,
    is_active: true
  }

  if (scheduleType.value === 'interval') {
    data.interval_hours = intervalHours.value
    data.interval_minutes = intervalMinutes.value
    data.schedule_days = selectedDays.value
    data.schedule_times = [startTime.value, endTime.value]
  } else if (scheduleType.value === 'specific') {
    data.schedule_days = selectedDays.value
    data.schedule_times = specificTimes.value
  } else if (scheduleType.value === 'once') {
    data.once_datetime = onceDatetime.value
  }

  const schedule = await libraryApi.createSchedule(data)
  emit('scheduled', schedule)
  emit('update:open', false)
}
</script>
```

---

## 🗄️ Pinia Store

### libraryStore.ts

```typescript
// frontend/src/stores/libraryStore.ts

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AudioMessage, Category, LibraryFilters } from '@/types/library.types'
import { libraryApi } from '@/services/libraryApi'

export const useLibraryStore = defineStore('library', () => {
  // State
  const messages = ref<AudioMessage[]>([])
  const categories = ref<Category[]>([])
  const isLoading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const perPage = ref(20)

  const filters = ref<LibraryFilters>({
    search: '',
    category_id: null,
    is_favorite: null,
    sort_by: 'created_at',
    sort_order: 'desc',
    page: 1,
    per_page: 20
  })

  // Computed
  const totalPages = computed(() => Math.ceil(total.value / perPage.value))

  const hasNextPage = computed(() => currentPage.value < totalPages.value)

  const hasPrevPage = computed(() => currentPage.value > 1)

  // Actions
  const fetchMessages = async () => {
    isLoading.value = true
    try {
      const response = await libraryApi.getMessages(filters.value)
      messages.value = response.messages
      total.value = response.total
      currentPage.value = response.page
    } finally {
      isLoading.value = false
    }
  }

  const fetchCategories = async () => {
    const response = await libraryApi.getCategories()
    categories.value = response
  }

  const updateMessage = async (id: number, data: Partial<AudioMessage>) => {
    const updated = await libraryApi.updateMessage(id, data)
    const index = messages.value.findIndex(m => m.id === id)
    if (index !== -1) {
      messages.value[index] = updated
    }
  }

  const deleteMessage = async (id: number) => {
    await libraryApi.deleteMessage(id)
    messages.value = messages.value.filter(m => m.id !== id)
    total.value--
  }

  const deleteMessages = async (ids: number[]) => {
    await libraryApi.deleteMessages(ids)
    messages.value = messages.value.filter(m => !ids.includes(m.id))
    total.value -= ids.length
  }

  const toggleFavorite = async (id: number) => {
    const message = messages.value.find(m => m.id === id)
    if (message) {
      await updateMessage(id, { is_favorite: !message.is_favorite })
    }
  }

  const updateCategory = async (id: number, categoryId: string | null) => {
    await updateMessage(id, { category_id: categoryId })
  }

  const setFilter = (key: keyof LibraryFilters, value: any) => {
    filters.value[key] = value
    filters.value.page = 1 // Reset page on filter change
    fetchMessages()
  }

  const nextPage = () => {
    if (hasNextPage.value) {
      filters.value.page++
      fetchMessages()
    }
  }

  const prevPage = () => {
    if (hasPrevPage.value) {
      filters.value.page--
      fetchMessages()
    }
  }

  const uploadAudio = async (file: File, displayName?: string) => {
    const newMessage = await libraryApi.uploadAudio(file, displayName)
    messages.value.unshift(newMessage)
    total.value++
    return newMessage
  }

  return {
    // State
    messages,
    categories,
    isLoading,
    total,
    currentPage,
    filters,

    // Computed
    totalPages,
    hasNextPage,
    hasPrevPage,

    // Actions
    fetchMessages,
    fetchCategories,
    updateMessage,
    deleteMessage,
    deleteMessages,
    toggleFavorite,
    updateCategory,
    setFilter,
    nextPage,
    prevPage,
    uploadAudio
  }
})
```

---

## 🔧 Composables

### useAudioPlayer.ts

```typescript
// frontend/src/components/library/composables/useAudioPlayer.ts

import { ref, onUnmounted } from 'vue'
import type { AudioMessage } from '../types/library.types'

export function useAudioPlayer() {
  const currentMessage = ref<AudioMessage | null>(null)
  const isPlaying = ref(false)
  const audioElement = ref<HTMLAudioElement | null>(null)

  const playMessage = (message: AudioMessage) => {
    // Stop current if different
    if (currentMessage.value?.id !== message.id) {
      stopPlayback()
    }

    // Create audio element if needed
    if (!audioElement.value) {
      audioElement.value = new Audio()
      audioElement.value.addEventListener('ended', () => {
        isPlaying.value = false
      })
    }

    // Toggle play/pause for same message
    if (currentMessage.value?.id === message.id) {
      if (isPlaying.value) {
        audioElement.value.pause()
        isPlaying.value = false
      } else {
        audioElement.value.play()
        isPlaying.value = true
      }
      return
    }

    // Play new message
    currentMessage.value = message
    audioElement.value.src = `/api/v1/audio/stream/${message.filename}`
    audioElement.value.play()
    isPlaying.value = true
  }

  const stopPlayback = () => {
    if (audioElement.value) {
      audioElement.value.pause()
      audioElement.value.currentTime = 0
    }
    isPlaying.value = false
    currentMessage.value = null
  }

  const isMessagePlaying = (messageId: number) => {
    return currentMessage.value?.id === messageId && isPlaying.value
  }

  onUnmounted(() => {
    stopPlayback()
  })

  return {
    currentMessage,
    isPlaying,
    playMessage,
    stopPlayback,
    isMessagePlaying
  }
}
```

### useFileUpload.ts

```typescript
// frontend/src/components/library/composables/useFileUpload.ts

import { ref } from 'vue'
import { useLibraryStore } from '@/stores/libraryStore'

const ALLOWED_TYPES = [
  'audio/mpeg',
  'audio/wav',
  'audio/x-wav',
  'audio/flac',
  'audio/aac',
  'audio/ogg',
  'audio/mp4',
  'audio/x-m4a'
]

const MAX_SIZE = 50 * 1024 * 1024 // 50 MB

export function useFileUpload() {
  const store = useLibraryStore()

  const isUploading = ref(false)
  const uploadProgress = ref(0)
  const uploadError = ref<string | null>(null)

  const validateFile = (file: File): string | null => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return 'Formato no permitido. Use: MP3, WAV, FLAC, AAC, OGG, M4A'
    }

    if (file.size > MAX_SIZE) {
      return 'Archivo excede el límite de 50MB'
    }

    return null
  }

  const uploadFile = async (file: File, displayName?: string) => {
    uploadError.value = null

    const error = validateFile(file)
    if (error) {
      uploadError.value = error
      return null
    }

    isUploading.value = true
    uploadProgress.value = 0

    try {
      const message = await store.uploadAudio(file, displayName)
      uploadProgress.value = 100
      return message
    } catch (err: any) {
      uploadError.value = err.message || 'Error al subir archivo'
      return null
    } finally {
      isUploading.value = false
    }
  }

  const resetUpload = () => {
    isUploading.value = false
    uploadProgress.value = 0
    uploadError.value = null
  }

  return {
    isUploading,
    uploadProgress,
    uploadError,
    validateFile,
    uploadFile,
    resetUpload
  }
}
```

### useSelection.ts

```typescript
// frontend/src/components/library/composables/useSelection.ts

import { ref, computed } from 'vue'

export function useSelection() {
  const selectionMode = ref(false)
  const selectedIds = ref<Set<number>>(new Set())

  const selectedCount = computed(() => selectedIds.value.size)

  const toggleSelectionMode = () => {
    selectionMode.value = !selectionMode.value
    if (!selectionMode.value) {
      clearSelection()
    }
  }

  const toggleSelect = (id: number) => {
    if (selectedIds.value.has(id)) {
      selectedIds.value.delete(id)
    } else {
      selectedIds.value.add(id)
    }
    // Trigger reactivity
    selectedIds.value = new Set(selectedIds.value)
  }

  const selectAll = (ids: number[]) => {
    ids.forEach(id => selectedIds.value.add(id))
    selectedIds.value = new Set(selectedIds.value)
  }

  const clearSelection = () => {
    selectedIds.value = new Set()
    selectionMode.value = false
  }

  const isSelected = (id: number) => selectedIds.value.has(id)

  return {
    selectionMode,
    selectedIds,
    selectedCount,
    toggleSelectionMode,
    toggleSelect,
    selectAll,
    clearSelection,
    isSelected
  }
}
```

---

## 📝 Utils

### formatters.ts

```typescript
// frontend/src/components/library/utils/formatters.ts

export function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

export function formatDate(isoString: string): string {
  const date = new Date(isoString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // Today
  if (diff < 86400000 && date.getDate() === now.getDate()) {
    return `Hoy ${date.toLocaleTimeString('es-CL', {
      hour: '2-digit',
      minute: '2-digit'
    })}`
  }

  // Yesterday
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.getDate() === yesterday.getDate() &&
      date.getMonth() === yesterday.getMonth()) {
    return `Ayer ${date.toLocaleTimeString('es-CL', {
      hour: '2-digit',
      minute: '2-digit'
    })}`
  }

  // Full date
  return date.toLocaleDateString('es-CL', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength - 3) + '...'
}

export function escapeHtml(text: string): string {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}
```

---

## 🔄 Flujos de Usuario

### 1. Categorizar Mensaje

```
1. Usuario ve mensaje en Library
2. Click en badge de categoría
3. Aparece dropdown con categorías dinámicas
4. Selecciona nueva categoría
5. API: PATCH /api/v1/library/{id} { category_id: "nueva" }
6. Badge se actualiza inmediatamente
7. Si hay schedules activos, se sincronizan
```

### 2. Marcar Favorito

```
1. Usuario ve mensaje
2. Click en estrella ☆
3. API: PATCH /api/v1/library/{id} { is_favorite: true }
4. Estrella cambia a ★ (amarilla)
5. Mensaje aparece en filtro "Favoritos"
```

### 3. Editar en Dashboard

```
1. Usuario en Library selecciona mensaje
2. Click "Editar en Dashboard" (✏️)
3. Sistema:
   - Almacena texto en sessionStorage
   - Navega a /dashboard
4. Dashboard detecta texto pendiente
5. Pre-llena textarea con texto
6. Usuario edita y genera NUEVO mensaje
7. Original permanece intacto
```

### 4. Programar Mensaje

```
1. Usuario click 📅 en mensaje
2. Abre ScheduleModal
3. Selecciona tipo (Intervalo/Específico/Una vez)
4. Configura parámetros
5. API: POST /api/v1/schedules
6. Mensaje aparece en calendario
7. Cron ejecuta según programación
```

### 5. Subir Audio Externo

```
1. Usuario click "Subir Audio" en header
2. Abre UploadModal
3. Selecciona archivo (drag & drop o file picker)
4. Validación:
   - Formato: MP3, WAV, FLAC, AAC, OGG, M4A
   - Tamaño: < 50MB
5. Muestra barra de progreso
6. API: POST /api/v1/library/upload (multipart)
7. Archivo aparece en grid
8. Sin categoría por defecto
```

---

## 🎨 Estilos (Tailwind + DaisyUI)

### Clases Principales

```css
/* Library Container */
.library-container {
  @apply p-6 max-w-7xl mx-auto;
}

/* Message Card */
.message-card {
  @apply card bg-base-100 shadow-md hover:shadow-lg transition-shadow;
  @apply border border-base-300;
}

.message-card.selected {
  @apply ring-2 ring-primary border-primary;
}

/* Category Badge */
.category-badge {
  @apply badge badge-sm font-medium;
}

/* Favorite Button */
.favorite-btn {
  @apply text-xl transition-colors;
}

.favorite-btn.active {
  @apply text-warning;
}

/* Actions */
.actions button {
  @apply btn btn-ghost btn-sm;
}

/* View Toggle */
.view-toggle {
  @apply btn-group;
}

/* Grid View */
.library-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4;
}

/* List View */
.library-list {
  @apply table table-zebra w-full;
}
```

---

## ✅ Checklist de Implementación

### Fase 1: Core (Prioridad Alta)
- [ ] libraryStore.ts - Estado Pinia
- [ ] libraryApi.ts - Llamadas API
- [ ] Library.vue - Container
- [ ] LibraryGrid.vue - Vista grid
- [ ] MessageCard.vue - Card individual
- [ ] useAudioPlayer.ts - Reproducción

### Fase 2: Categorización
- [ ] CategoryBadge.vue - Dropdown categorías
- [ ] LibraryFilters.vue - Filtros
- [ ] Favoritos (toggle + filtro)

### Fase 3: Acciones
- [ ] ScheduleModal.vue - Programación
- [ ] UploadModal.vue - Subir audio
- [ ] Eliminar (individual + batch)
- [ ] Editar en Dashboard

### Fase 4: Vista Lista
- [ ] LibraryList.vue - Vista tabla
- [ ] MessageRow.vue - Fila
- [ ] ViewToggle.vue - Switch

### Fase 5: Polish
- [ ] EmptyState.vue
- [ ] SelectionBar.vue
- [ ] Paginación
- [ ] Ordenamiento

---

**Documento creado**: 2025-11-29
**Autor**: Claude (Anthropic)
**Versión**: 1.0
