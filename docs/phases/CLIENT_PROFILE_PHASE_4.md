# Fase 4: Frontend - Settings Integration

**Plan Maestro**: `CLIENT_PROFILE_SYSTEM.md`
**Dependencia**: Fase 3 completada
**Estado**: Pendiente

---

## Objetivo

Agregar una sección en AIClientEditor para ver y editar las instrucciones de todas las campañas de un cliente desde Settings.

---

## Tareas

### 4.1 Crear Componente de Edición de Prompts

**Archivo**: `frontend/src/components/settings/ai-clients/components/CampaignPromptsEditor.vue`

```vue
<template>
  <CollapsiblePanel
    title="Instrucciones por Campaña"
    :default-open="false"
  >
    <template #header-extra>
      <span class="badge badge-ghost badge-sm">
        {{ promptCount }} configuradas
      </span>
    </template>

    <p class="text-sm text-base-content/60 mb-4">
      Configure instrucciones específicas de IA para cada campaña.
      Estas instrucciones se añaden al contexto general cuando se genera audio.
    </p>

    <!-- Loading -->
    <div v-if="isLoadingCampaigns" class="flex justify-center py-8">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <!-- No campaigns -->
    <div v-else-if="campaigns.length === 0" class="text-center py-8 text-base-content/50">
      No hay campañas configuradas.
      <br>
      <span class="text-sm">Cree campañas primero en la sección Campañas.</span>
    </div>

    <!-- Campaign list -->
    <div v-else class="space-y-4">
      <div
        v-for="campaign in campaigns"
        :key="campaign.id"
        class="border border-base-300 rounded-lg overflow-hidden"
      >
        <!-- Campaign header -->
        <div
          class="flex items-center gap-3 p-3 bg-base-200 cursor-pointer"
          @click="toggleCampaign(campaign.id)"
        >
          <span class="text-xl">{{ campaign.icon || '📁' }}</span>
          <div class="flex-1">
            <span class="font-medium">{{ campaign.name }}</span>
            <span
              v-if="hasInstructions(campaign.id)"
              class="badge badge-success badge-xs ml-2"
            >
              Configurada
            </span>
          </div>
          <button class="btn btn-ghost btn-xs btn-circle">
            <svg
              class="w-4 h-4 transition-transform"
              :class="{ 'rotate-180': expandedCampaigns.has(campaign.id) }"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>

        <!-- Campaign editor (expandible) -->
        <div
          v-show="expandedCampaigns.has(campaign.id)"
          class="p-4 border-t border-base-300"
        >
          <textarea
            v-model="localPrompts[campaign.id]"
            class="textarea textarea-bordered textarea-sm w-full h-24 font-mono"
            :placeholder="`Instrucciones específicas para ${campaign.name}...`"
            @input="markDirty(campaign.id)"
          />

          <div class="flex items-center justify-between mt-2">
            <span class="text-xs text-base-content/50">
              {{ (localPrompts[campaign.id] || '').length }} caracteres
            </span>

            <div class="flex gap-2">
              <button
                v-if="isDirty(campaign.id)"
                class="btn btn-ghost btn-xs"
                @click="resetCampaign(campaign.id)"
              >
                Cancelar
              </button>
              <button
                class="btn btn-primary btn-xs"
                :disabled="!isDirty(campaign.id) || savingCampaigns.has(campaign.id)"
                @click="saveCampaign(campaign.id)"
              >
                <span
                  v-if="savingCampaigns.has(campaign.id)"
                  class="loading loading-spinner loading-xs"
                />
                Guardar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tip -->
    <div class="mt-4 text-xs text-base-content/50 flex items-start gap-2">
      <span>💡</span>
      <span>
        Deje vacío para usar solo el contexto general del cliente.
        Las instrucciones de campaña se añaden al final del prompt.
      </span>
    </div>
  </CollapsiblePanel>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import CollapsiblePanel from '@/components/shared/ui/CollapsiblePanel.vue'
import apiClient from '@/api/client'

// Props
const props = defineProps<{
  clientId: string
  customPrompts: Record<string, string> | null
}>()

// Emits
const emit = defineEmits<{
  'update:customPrompts': [prompts: Record<string, string>]
}>()

// Types
interface Campaign {
  id: string
  name: string
  icon: string | null
  color: string | null
  active: boolean
}

// State
const campaigns = ref<Campaign[]>([])
const isLoadingCampaigns = ref(false)
const expandedCampaigns = ref<Set<string>>(new Set())
const savingCampaigns = ref<Set<string>>(new Set())
const localPrompts = ref<Record<string, string>>({})
const originalPrompts = ref<Record<string, string>>({})
const dirtyPrompts = ref<Set<string>>(new Set())

// Computed
const promptCount = computed(() => {
  return Object.values(localPrompts.value).filter(p => p && p.trim()).length
})

// Methods
function hasInstructions(campaignId: string): boolean {
  return !!(localPrompts.value[campaignId]?.trim())
}

function toggleCampaign(campaignId: string) {
  if (expandedCampaigns.value.has(campaignId)) {
    expandedCampaigns.value.delete(campaignId)
  } else {
    expandedCampaigns.value.add(campaignId)
  }
}

function markDirty(campaignId: string) {
  const current = localPrompts.value[campaignId] || ''
  const original = originalPrompts.value[campaignId] || ''

  if (current !== original) {
    dirtyPrompts.value.add(campaignId)
  } else {
    dirtyPrompts.value.delete(campaignId)
  }
}

function isDirty(campaignId: string): boolean {
  return dirtyPrompts.value.has(campaignId)
}

function resetCampaign(campaignId: string) {
  localPrompts.value[campaignId] = originalPrompts.value[campaignId] || ''
  dirtyPrompts.value.delete(campaignId)
}

async function saveCampaign(campaignId: string) {
  savingCampaigns.value.add(campaignId)

  try {
    const instructions = localPrompts.value[campaignId] || ''

    // Guardar en el cliente específico (no en el activo)
    await apiClient.patch(
      `/api/v1/settings/ai-clients/${props.clientId}`,
      {
        custom_prompts: {
          ...props.customPrompts,
          [campaignId]: instructions
        }
      }
    )

    // Actualizar original y limpiar dirty
    originalPrompts.value[campaignId] = instructions
    dirtyPrompts.value.delete(campaignId)

    // Notificar al padre
    emit('update:customPrompts', {
      ...props.customPrompts,
      [campaignId]: instructions
    })

  } catch (error) {
    console.error('Error saving campaign prompt:', error)
  } finally {
    savingCampaigns.value.delete(campaignId)
  }
}

async function loadCampaigns() {
  isLoadingCampaigns.value = true

  try {
    // Cargar lista de campañas (categorías activas)
    const response = await apiClient.get('/api/v1/categories')
    campaigns.value = response.filter((c: Campaign) => c.active)
  } catch (error) {
    console.error('Error loading campaigns:', error)
    campaigns.value = []
  } finally {
    isLoadingCampaigns.value = false
  }
}

function initializePrompts() {
  const prompts = props.customPrompts || {}
  localPrompts.value = { ...prompts }
  originalPrompts.value = { ...prompts }
  dirtyPrompts.value.clear()
}

// Lifecycle
onMounted(async () => {
  await loadCampaigns()
  initializePrompts()
})

// Watch para cuando cambien los props
watch(() => props.customPrompts, () => {
  initializePrompts()
}, { deep: true })

watch(() => props.clientId, async () => {
  initializePrompts()
})
</script>
```

### 4.2 Integrar en AIClientEditor

**Archivo**: `frontend/src/components/settings/ai-clients/components/AIClientEditor.vue`

Agregar el nuevo componente:

```vue
<template>
  <div class="space-y-6">
    <!-- Secciones existentes... -->

    <!-- Basic Info -->
    <CollapsiblePanel title="Información Básica" :default-open="true">
      <!-- ... campos existentes ... -->
    </CollapsiblePanel>

    <!-- Context -->
    <CollapsiblePanel title="Contexto de IA" :default-open="true">
      <!-- ... textarea de contexto ... -->
    </CollapsiblePanel>

    <!-- NUEVA SECCIÓN: Instrucciones por Campaña -->
    <CampaignPromptsEditor
      v-if="client"
      :client-id="client.id"
      :custom-prompts="client.custom_prompts || {}"
      @update:custom-prompts="handlePromptsUpdate"
    />

    <!-- Botones de acción -->
    <div class="flex justify-end gap-2">
      <!-- ... botones existentes ... -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import CollapsiblePanel from '@/components/shared/ui/CollapsiblePanel.vue'
import CampaignPromptsEditor from './CampaignPromptsEditor.vue'

// ... código existente ...

function handlePromptsUpdate(prompts: Record<string, string>) {
  if (client.value) {
    client.value.custom_prompts = prompts
  }
}
</script>
```

### 4.3 Actualizar AIClientManager

**Archivo**: `frontend/src/components/settings/ai-clients/AIClientManager.vue`

Asegurarse de que custom_prompts se carga y guarda correctamente:

```vue
<script setup lang="ts">
// ... código existente ...

// En la función de guardar cliente, incluir custom_prompts:
async function saveClient() {
  if (!selectedClient.value) return

  isSaving.value = true

  try {
    await apiClient.patch(`/api/v1/settings/ai-clients/${selectedClient.value.id}`, {
      name: selectedClient.value.name,
      context: selectedClient.value.context,
      category: selectedClient.value.category,
      active: selectedClient.value.active,
      settings: selectedClient.value.settings,
      custom_prompts: selectedClient.value.custom_prompts  // ← Incluir esto
    })

    successMessage.value = 'Cliente guardado correctamente'
    await loadClients()
  } catch (error) {
    // ...
  } finally {
    isSaving.value = false
  }
}
</script>
```

### 4.4 Invalidar Cache al Cambiar Cliente Activo

Cuando se cambia el cliente activo en Settings, invalidar el cache del composable:

```vue
<!-- En AIClientManager.vue o donde se active un cliente -->
<script setup lang="ts">
import { useClientCampaignPrompts } from '@/composables/useClientCampaignPrompts'

const { invalidateClientCache } = useClientCampaignPrompts()

async function setActiveClient(clientId: string) {
  try {
    await apiClient.post(`/api/v1/settings/ai-clients/active/${clientId}`)

    // Invalidar cache para que Campaigns recargue el nuevo cliente
    invalidateClientCache()

    await loadClients()
    successMessage.value = 'Cliente activo cambiado'
  } catch (error) {
    // ...
  }
}
</script>
```

---

## Verificación

```bash
# 1. Verificar que compila
cd /var/www/mediaflow-v2/frontend
npm run build

# 2. Test manual en navegador
npm run dev
```

---

## Tests E2E (Manual)

### Test 1: Ver Instrucciones por Campaña en Settings
1. Ir a `/settings/ai`
2. Seleccionar un cliente
3. Expandir sección "Instrucciones por Campaña"
4. Verificar que aparece lista de campañas
5. Verificar contador "X configuradas"

### Test 2: Editar desde Settings
1. En Settings > AI Clients, seleccionar cliente
2. Expandir "Instrucciones por Campaña"
3. Expandir una campaña (ej: Navidad)
4. Escribir instrucciones
5. Click "Guardar"
6. Ir a `/campaigns/navidad`
7. Verificar que las instrucciones aparecen

### Test 3: Sincronización Bidireccional
1. En `/campaigns/navidad`, editar instrucciones
2. Guardar
3. Ir a `/settings/ai`
4. Expandir "Instrucciones por Campaña"
5. Verificar que las instrucciones de Navidad coinciden

### Test 4: Cambiar Cliente Activo
1. En Settings, activar cliente "Farmacia"
2. Ir a `/campaigns/navidad`
3. Verificar que ahora muestra "Cliente: Farmacia"
4. Verificar que las instrucciones son las de Farmacia (no Supermercado)

---

## Checklist

- [ ] CampaignPromptsEditor creado
- [ ] Integrado en AIClientEditor
- [ ] Lista de campañas carga correctamente
- [ ] Expandir/colapsar campañas funciona
- [ ] Editar instrucciones funciona
- [ ] Guardar individual por campaña funciona
- [ ] Badge "Configurada" aparece cuando hay instrucciones
- [ ] Contador de prompts correcto
- [ ] Invalidación de cache al cambiar cliente
- [ ] Sincronización Settings ↔ Campaigns funciona
- [ ] Build sin errores
- [ ] Tests manuales pasando

---

## Siguiente Fase

Una vez completada esta fase, continuar con **Fase 5: Testing y Documentación**.
