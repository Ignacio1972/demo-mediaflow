# Fase 3: Frontend - Composable y AITrainingPanel

**Plan Maestro**: `CLIENT_PROFILE_SYSTEM.md`
**Dependencia**: Fase 2 completada
**Estado**: Pendiente

---

## Objetivo

Crear el composable para gestionar instrucciones de campaña y modificar AITrainingPanel para usar el nuevo sistema vinculado al cliente activo.

---

## Tareas

### 3.1 Crear Composable

**Archivo**: `frontend/src/composables/useClientCampaignPrompts.ts`

```typescript
/**
 * Composable para gestionar instrucciones de campaña
 * vinculadas al cliente activo.
 *
 * Las instrucciones se guardan en AIClient.custom_prompts[campaign_id]
 * del cliente actualmente activo.
 */

import { ref, readonly } from 'vue'
import apiClient from '@/api/client'

// Tipos
interface ActiveClientInfo {
  client_id: string
  client_name: string
}

interface CampaignPromptResponse {
  client_id: string
  client_name: string
  campaign_id: string
  instructions: string
}

interface AllPromptsResponse {
  client_id: string
  client_name: string
  prompts: Record<string, string>
}

// Estado compartido (singleton)
const activeClient = ref<ActiveClientInfo | null>(null)
const isLoadingClient = ref(false)
const clientError = ref<string | null>(null)

export function useClientCampaignPrompts() {
  // Estado local por instancia
  const isLoading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)
  const successMessage = ref<string | null>(null)

  /**
   * Carga información del cliente activo.
   * Se cachea en estado compartido.
   */
  async function loadActiveClient(): Promise<ActiveClientInfo | null> {
    if (activeClient.value) {
      return activeClient.value
    }

    isLoadingClient.value = true
    clientError.value = null

    try {
      const response = await apiClient.get('/api/v1/settings/ai-clients/active')
      activeClient.value = {
        client_id: response.id,
        client_name: response.name
      }
      return activeClient.value
    } catch (e: any) {
      console.error('Error loading active client:', e)
      clientError.value = e.message || 'Error al cargar cliente activo'
      activeClient.value = null
      return null
    } finally {
      isLoadingClient.value = false
    }
  }

  /**
   * Invalida el cache del cliente activo.
   * Usar cuando se cambia de cliente en Settings.
   */
  function invalidateClientCache() {
    activeClient.value = null
  }

  /**
   * Obtiene las instrucciones de una campaña específica
   * del cliente activo.
   */
  async function getCampaignInstructions(campaignId: string): Promise<string> {
    isLoading.value = true
    error.value = null

    try {
      const response: CampaignPromptResponse = await apiClient.get(
        `/api/v1/settings/ai-clients/active/campaign-prompts/${campaignId}`
      )

      // Actualizar info del cliente si no la teníamos
      if (!activeClient.value) {
        activeClient.value = {
          client_id: response.client_id,
          client_name: response.client_name
        }
      }

      return response.instructions || ''
    } catch (e: any) {
      console.error('Error loading campaign instructions:', e)
      error.value = e.message || 'Error al cargar instrucciones'
      return ''
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtiene todas las instrucciones del cliente activo.
   */
  async function getAllCampaignInstructions(): Promise<Record<string, string>> {
    isLoading.value = true
    error.value = null

    try {
      const response: AllPromptsResponse = await apiClient.get(
        '/api/v1/settings/ai-clients/active/campaign-prompts'
      )

      // Actualizar info del cliente
      activeClient.value = {
        client_id: response.client_id,
        client_name: response.client_name
      }

      return response.prompts || {}
    } catch (e: any) {
      console.error('Error loading all campaign instructions:', e)
      error.value = e.message || 'Error al cargar instrucciones'
      return {}
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Guarda las instrucciones de una campaña en el cliente activo.
   */
  async function saveCampaignInstructions(
    campaignId: string,
    instructions: string
  ): Promise<boolean> {
    isSaving.value = true
    error.value = null
    successMessage.value = null

    try {
      const response: CampaignPromptResponse = await apiClient.patch(
        `/api/v1/settings/ai-clients/active/campaign-prompts/${campaignId}`,
        { instructions }
      )

      successMessage.value = 'Instrucciones guardadas'

      // Auto-clear success message
      setTimeout(() => {
        successMessage.value = null
      }, 3000)

      return true
    } catch (e: any) {
      console.error('Error saving campaign instructions:', e)
      error.value = e.message || 'Error al guardar instrucciones'
      return false
    } finally {
      isSaving.value = false
    }
  }

  /**
   * Elimina las instrucciones de una campaña del cliente activo.
   */
  async function deleteCampaignInstructions(campaignId: string): Promise<boolean> {
    isSaving.value = true
    error.value = null

    try {
      await apiClient.delete(
        `/api/v1/settings/ai-clients/active/campaign-prompts/${campaignId}`
      )
      return true
    } catch (e: any) {
      console.error('Error deleting campaign instructions:', e)
      error.value = e.message || 'Error al eliminar instrucciones'
      return false
    } finally {
      isSaving.value = false
    }
  }

  return {
    // Estado compartido (readonly para prevenir mutaciones externas)
    activeClient: readonly(activeClient),
    isLoadingClient: readonly(isLoadingClient),
    clientError: readonly(clientError),

    // Estado local
    isLoading: readonly(isLoading),
    isSaving: readonly(isSaving),
    error: readonly(error),
    successMessage: readonly(successMessage),

    // Métodos
    loadActiveClient,
    invalidateClientCache,
    getCampaignInstructions,
    getAllCampaignInstructions,
    saveCampaignInstructions,
    deleteCampaignInstructions
  }
}
```

### 3.2 Modificar AITrainingPanel

**Archivo**: `frontend/src/components/campaigns/components/AITrainingPanel.vue`

```vue
<template>
  <CollapsiblePanel
    title="Entrenamiento IA"
    :default-open="!hasInstructions"
  >
    <!-- Indicador de cliente activo -->
    <div class="mb-4 p-3 bg-base-200 rounded-lg">
      <div class="flex items-center gap-2">
        <span class="text-lg">🏪</span>
        <div class="flex-1">
          <div class="text-xs text-base-content/60 uppercase tracking-wide">
            Cliente activo
          </div>
          <div class="font-medium">
            <template v-if="isLoadingClient">
              <span class="loading loading-dots loading-xs"></span>
            </template>
            <template v-else-if="activeClient">
              {{ activeClient.client_name }}
            </template>
            <template v-else>
              <span class="text-error">Sin cliente configurado</span>
            </template>
          </div>
        </div>
      </div>
      <p class="text-xs text-base-content/50 mt-2">
        Las instrucciones se guardan para este cliente.
        Para cambiar de cliente, contacte al administrador.
      </p>
    </div>

    <!-- Error state -->
    <div v-if="error" class="alert alert-error mb-4">
      <span>{{ error }}</span>
    </div>

    <!-- Success state -->
    <div v-if="successMessage" class="alert alert-success mb-4">
      <span>{{ successMessage }}</span>
    </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="flex justify-center py-8">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <!-- Editor -->
    <template v-else>
      <label class="label">
        <span class="label-text">
          Instrucciones para la IA cuando genere sugerencias para esta campaña
        </span>
      </label>

      <textarea
        v-model="localInstructions"
        class="textarea textarea-bordered w-full h-32 font-mono text-sm"
        :placeholder="placeholder"
        :disabled="!activeClient"
        @input="markDirty"
      />

      <div class="flex items-center justify-between mt-3">
        <span class="text-xs text-base-content/50">
          {{ localInstructions.length }} / 5000 caracteres
        </span>

        <div class="flex gap-2">
          <button
            v-if="isDirty"
            class="btn btn-ghost btn-sm"
            @click="handleCancel"
          >
            Cancelar
          </button>
          <button
            class="btn btn-primary btn-sm"
            :disabled="!isDirty || isSaving || !activeClient"
            @click="handleSave"
          >
            <span v-if="isSaving" class="loading loading-spinner loading-xs" />
            {{ isSaving ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </div>
    </template>
  </CollapsiblePanel>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useClientCampaignPrompts } from '@/composables/useClientCampaignPrompts'
import CollapsiblePanel from '@/components/shared/ui/CollapsiblePanel.vue'

const props = defineProps<{
  campaignId: string
}>()

const emit = defineEmits<{
  saved: []
}>()

// Composable
const {
  activeClient,
  isLoadingClient,
  isLoading,
  isSaving,
  error,
  successMessage,
  loadActiveClient,
  getCampaignInstructions,
  saveCampaignInstructions
} = useClientCampaignPrompts()

// Estado local
const localInstructions = ref('')
const originalInstructions = ref('')
const isDirty = ref(false)

// Computeds
const hasInstructions = computed(() => localInstructions.value.trim().length > 0)

const placeholder = computed(() =>
  `Ej: Usa un tono festivo y navideño. Menciona ofertas especiales.
Incluye palabras como "alegría", "familia", "celebración".
Evita mensajes negativos o tristes.`
)

// Métodos
function markDirty() {
  isDirty.value = localInstructions.value !== originalInstructions.value
}

function handleCancel() {
  localInstructions.value = originalInstructions.value
  isDirty.value = false
}

async function handleSave() {
  const success = await saveCampaignInstructions(
    props.campaignId,
    localInstructions.value
  )

  if (success) {
    originalInstructions.value = localInstructions.value
    isDirty.value = false
    emit('saved')
  }
}

async function loadInstructions() {
  const instructions = await getCampaignInstructions(props.campaignId)
  localInstructions.value = instructions
  originalInstructions.value = instructions
}

// Lifecycle
onMounted(async () => {
  await loadActiveClient()
  await loadInstructions()
})

// Watch para cuando cambie el campaignId (navegación)
watch(() => props.campaignId, async (newId) => {
  if (newId) {
    await loadInstructions()
  }
})
</script>
```

### 3.3 Actualizar Tipos

**Archivo**: `frontend/src/types/ai-client.ts` (crear si no existe)

```typescript
/**
 * Tipos para el sistema de clientes AI
 */

export interface AIClient {
  id: string
  name: string
  context: string
  category: string
  active: boolean
  is_default: boolean
  order: number
  settings?: Record<string, any>
  custom_prompts?: Record<string, string>
  created_at?: string
  updated_at?: string
}

export interface ActiveClientInfo {
  client_id: string
  client_name: string
}

export interface CampaignPromptResponse {
  client_id: string
  client_name: string
  campaign_id: string
  instructions: string
}

export interface AllCampaignPromptsResponse {
  client_id: string
  client_name: string
  prompts: Record<string, string>
}

export interface CampaignPromptUpdate {
  instructions: string
}
```

### 3.4 Actualizar CampaignDetail

**Archivo**: `frontend/src/components/campaigns/CampaignDetail.vue`

Verificar que AITrainingPanel se usa correctamente:

```vue
<template>
  <!-- ... -->
  <div class="lg:col-span-2">
    <!-- Panel de entrenamiento IA -->
    <AITrainingPanel
      :campaign-id="campaignId"
      @saved="handleInstructionsSaved"
    />

    <!-- Otros paneles... -->
  </div>
  <!-- ... -->
</template>

<script setup lang="ts">
// ...

function handleInstructionsSaved() {
  // Opcional: mostrar notificación o recargar datos
  console.log('Instrucciones guardadas')
}
</script>
```

---

## Verificación

```bash
# 1. Verificar que compila
cd /var/www/mediaflow-v2/frontend
npm run build

# 2. Verificar tipos
npm run type-check

# 3. Test manual en navegador
npm run dev
# Abrir http://localhost:5173/campaigns/navidad
# - Verificar que aparece el cliente activo
# - Editar instrucciones
# - Guardar y verificar que persiste
```

---

## Tests E2E (Manual)

### Test 1: Ver Cliente Activo
1. Ir a `/campaigns/navidad`
2. Ver panel "Entrenamiento IA"
3. Verificar que muestra el nombre del cliente activo
4. Verificar mensaje "Para cambiar de cliente, contacte al administrador"

### Test 2: Editar Instrucciones
1. Escribir nuevas instrucciones en el textarea
2. Verificar que botón "Guardar" se habilita
3. Click en "Guardar"
4. Verificar mensaje de éxito
5. Recargar página
6. Verificar que instrucciones persisten

### Test 3: Cancelar Cambios
1. Editar instrucciones
2. Click en "Cancelar"
3. Verificar que vuelve al valor original

### Test 4: Sin Cliente Activo
1. (En BD) Desactivar todos los clientes
2. Ir a `/campaigns/navidad`
3. Verificar mensaje de error "Sin cliente configurado"
4. Verificar que textarea está deshabilitado

---

## Checklist

- [ ] Composable `useClientCampaignPrompts` creado
- [ ] AITrainingPanel modificado
- [ ] Indicador de cliente activo visible
- [ ] Mensaje de read-only para cambio de cliente
- [ ] Guardado funciona correctamente
- [ ] Cancelar funciona correctamente
- [ ] Estados de loading/error manejados
- [ ] Watch para cambio de campaignId
- [ ] Tipos TypeScript actualizados
- [ ] Build sin errores
- [ ] Tests manuales pasando

---

## Siguiente Fase

Una vez completada esta fase, continuar con **Fase 4: Frontend - Settings Integration**.
