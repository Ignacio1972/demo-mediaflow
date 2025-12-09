<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="card-title">{{ localClient.name }}</h2>
          <p class="text-sm text-base-content/60">{{ localClient.category }}</p>
        </div>
        <div class="flex gap-2">
          <button
            v-if="!localClient.is_default"
            @click="$emit('set-default', localClient.id)"
            class="btn btn-outline btn-sm"
            :disabled="isSaving"
          >
            Establecer como Activo
          </button>
          <button
            v-if="!localClient.is_default"
            @click="$emit('delete', localClient.id)"
            class="btn btn-error btn-outline btn-sm"
            :disabled="isSaving"
          >
            Eliminar
          </button>
        </div>
      </div>

      <!-- Form -->
      <div class="space-y-6">
        <!-- Basic Info -->
        <div class="collapse collapse-open bg-base-200 rounded-box">
          <input type="checkbox" checked />
          <div class="collapse-title font-medium">
            Informacion Basica
          </div>
          <div class="collapse-content">
            <div class="grid gap-4">
              <!-- Name -->
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Nombre</span>
                </label>
                <input
                  v-model="localClient.name"
                  type="text"
                  class="input input-bordered"
                  placeholder="Nombre del cliente"
                />
              </div>

              <!-- Category -->
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Categoria</span>
                </label>
                <select v-model="localClient.category" class="select select-bordered">
                  <option value="general">General</option>
                  <option value="supermercado">Supermercado</option>
                  <option value="mall">Centro Comercial</option>
                  <option value="retail">Retail</option>
                  <option value="servicios">Servicios</option>
                  <option value="otro">Otro</option>
                </select>
              </div>

              <!-- Active -->
              <div class="form-control">
                <label class="label cursor-pointer justify-start gap-4">
                  <input
                    v-model="localClient.active"
                    type="checkbox"
                    class="toggle toggle-primary"
                  />
                  <span class="label-text">Cliente activo</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Context -->
        <div class="collapse collapse-open bg-base-200 rounded-box">
          <input type="checkbox" checked />
          <div class="collapse-title font-medium">
            Contexto de IA (System Prompt)
          </div>
          <div class="collapse-content">
            <div class="form-control">
              <textarea
                v-model="localClient.context"
                class="textarea textarea-bordered h-48 font-mono text-sm"
                placeholder="Describe el contexto del negocio para Claude..."
              ></textarea>
              <label class="label">
                <span class="label-text-alt">
                  {{ localClient.context?.length || 0 }} / 5000 caracteres
                </span>
              </label>
            </div>
          </div>
        </div>

        <!-- Custom Prompts (Optional) -->
        <div class="collapse bg-base-200 rounded-box">
          <input type="checkbox" />
          <div class="collapse-title font-medium">
            Prompts Personalizados (Opcional)
          </div>
          <div class="collapse-content">
            <p class="text-sm text-base-content/60 mb-4">
              Define prompts especificos para diferentes categorias de anuncios.
            </p>
            <div class="grid gap-4">
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Ofertas</span>
                </label>
                <textarea
                  v-model="customPrompts.ofertas"
                  class="textarea textarea-bordered h-20 text-sm"
                  placeholder="Instrucciones especiales para anuncios de ofertas..."
                ></textarea>
              </div>
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Eventos</span>
                </label>
                <textarea
                  v-model="customPrompts.eventos"
                  class="textarea textarea-bordered h-20 text-sm"
                  placeholder="Instrucciones especiales para anuncios de eventos..."
                ></textarea>
              </div>
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Informacion</span>
                </label>
                <textarea
                  v-model="customPrompts.informacion"
                  class="textarea textarea-bordered h-20 text-sm"
                  placeholder="Instrucciones especiales para anuncios informativos..."
                ></textarea>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="modal-action mt-6">
        <button @click="handleCancel" class="btn btn-ghost">
          Cancelar
        </button>
        <button
          @click="handleSave"
          class="btn btn-primary"
          :disabled="isSaving || !hasChanges"
        >
          <span v-if="isSaving" class="loading loading-spinner loading-sm"></span>
          Guardar Cambios
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import type { AIClient } from '@/composables/useAIClients'

const props = defineProps<{
  client: AIClient
  isSaving: boolean
}>()

const emit = defineEmits<{
  save: [updates: Partial<AIClient>]
  cancel: []
  delete: [clientId: string]
  'set-default': [clientId: string]
}>()

// Local copy for editing
const localClient = ref<AIClient>({ ...props.client })
const customPrompts = reactive({
  ofertas: props.client.custom_prompts?.ofertas || '',
  eventos: props.client.custom_prompts?.eventos || '',
  informacion: props.client.custom_prompts?.informacion || ''
})

// Track if there are changes
const hasChanges = computed(() => {
  return (
    localClient.value.name !== props.client.name ||
    localClient.value.context !== props.client.context ||
    localClient.value.category !== props.client.category ||
    localClient.value.active !== props.client.active ||
    customPrompts.ofertas !== (props.client.custom_prompts?.ofertas || '') ||
    customPrompts.eventos !== (props.client.custom_prompts?.eventos || '') ||
    customPrompts.informacion !== (props.client.custom_prompts?.informacion || '')
  )
})

// Reset when client changes
watch(() => props.client, (newClient) => {
  localClient.value = { ...newClient }
  customPrompts.ofertas = newClient.custom_prompts?.ofertas || ''
  customPrompts.eventos = newClient.custom_prompts?.eventos || ''
  customPrompts.informacion = newClient.custom_prompts?.informacion || ''
})

function handleSave() {
  const updates: Partial<AIClient> = {}

  if (localClient.value.name !== props.client.name) {
    updates.name = localClient.value.name
  }
  if (localClient.value.context !== props.client.context) {
    updates.context = localClient.value.context
  }
  if (localClient.value.category !== props.client.category) {
    updates.category = localClient.value.category
  }
  if (localClient.value.active !== props.client.active) {
    updates.active = localClient.value.active
  }

  // Custom prompts
  const newCustomPrompts: Record<string, string> = {}
  if (customPrompts.ofertas) newCustomPrompts.ofertas = customPrompts.ofertas
  if (customPrompts.eventos) newCustomPrompts.eventos = customPrompts.eventos
  if (customPrompts.informacion) newCustomPrompts.informacion = customPrompts.informacion

  if (Object.keys(newCustomPrompts).length > 0) {
    updates.custom_prompts = newCustomPrompts
  }

  emit('save', updates)
}

function handleCancel() {
  localClient.value = { ...props.client }
  customPrompts.ofertas = props.client.custom_prompts?.ofertas || ''
  customPrompts.eventos = props.client.custom_prompts?.eventos || ''
  customPrompts.informacion = props.client.custom_prompts?.informacion || ''
  emit('cancel')
}
</script>
