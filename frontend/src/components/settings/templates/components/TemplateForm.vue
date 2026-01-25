<template>
  <div class="template-form">
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
          <h2 class="card-title text-lg">
            Editar Plantilla
          </h2>
          <div class="flex items-center gap-2">
            <span
              v-if="localTemplate.is_default"
              class="badge badge-primary"
            >
              Default
            </span>
            <span
              :class="localTemplate.active ? 'badge-success' : 'badge-ghost'"
              class="badge"
            >
              {{ localTemplate.active ? 'Activa' : 'Inactiva' }}
            </span>
          </div>
        </div>

        <!-- Form -->
        <div class="space-y-4">
          <!-- Name -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Nombre</span>
            </label>
            <input
              v-model="localTemplate.name"
              type="text"
              placeholder="Nombre de la plantilla"
              class="input input-bordered w-full"
              :class="{ 'input-error': !localTemplate.name }"
            />
          </div>

          <!-- Description -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Descripcion</span>
              <span class="label-text-alt text-base-content/60">Opcional</span>
            </label>
            <input
              v-model="localTemplate.description"
              type="text"
              placeholder="Breve descripcion de cuando usar esta plantilla"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Module -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Modulo</span>
            </label>
            <select
              v-model="localTemplate.module"
              class="select select-bordered w-full"
            >
              <option
                v-for="mod in availableModules"
                :key="mod.id"
                :value="mod.id"
              >
                {{ mod.icon }} {{ mod.name }}
              </option>
            </select>
          </div>

          <!-- Template Text -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Texto de la Plantilla</span>
            </label>
            <textarea
              v-model="localTemplate.template_text"
              placeholder="Escribe el texto de la plantilla usando {variables}..."
              class="textarea textarea-bordered w-full h-40 font-mono text-sm"
              :class="{ 'textarea-error': !localTemplate.template_text }"
            ></textarea>
            <label class="label">
              <span class="label-text-alt text-base-content/60">
                Usa {'{'}variable{'}'} para insertar valores dinamicos
              </span>
            </label>
          </div>

          <!-- Detected Variables -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Variables Detectadas</span>
            </label>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="variable in detectedVariables"
                :key="variable"
                class="badge badge-primary badge-lg"
              >
                {{ variable }}
              </span>
              <span
                v-if="detectedVariables.length === 0"
                class="text-base-content/50 text-sm"
              >
                No se detectaron variables
              </span>
            </div>
          </div>

          <!-- Preview -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Vista Previa</span>
            </label>
            <div class="bg-base-200 rounded-lg p-4">
              <p class="text-sm whitespace-pre-wrap">{{ previewText }}</p>
            </div>
          </div>

          <!-- Active Toggle -->
          <div class="form-control">
            <label class="label cursor-pointer justify-start gap-4">
              <input
                type="checkbox"
                v-model="localTemplate.active"
                class="toggle toggle-primary"
              />
              <span class="label-text">Plantilla activa</span>
            </label>
          </div>

          <!-- Default Toggle -->
          <div class="form-control">
            <label class="label cursor-pointer justify-start gap-4">
              <input
                type="checkbox"
                v-model="localTemplate.is_default"
                class="toggle toggle-secondary"
                :disabled="localTemplate.is_default"
              />
              <span class="label-text">
                Plantilla por defecto para este modulo
              </span>
            </label>
          </div>

          <!-- Announcement Sound Toggle -->
          <div class="form-control">
            <label class="label cursor-pointer justify-start gap-4">
              <input
                type="checkbox"
                v-model="localTemplate.use_announcement_sound"
                class="toggle toggle-warning"
              />
              <div>
                <span class="label-text">Sonido de anuncio</span>
                <p class="text-xs text-base-content/50 mt-0.5">
                  Agrega sonido de intro y outro al mensaje (sin musica de fondo)
                </p>
              </div>
            </label>
          </div>
        </div>

        <!-- Actions -->
        <div class="card-actions justify-between mt-6 pt-4 border-t border-base-200">
          <button
            @click="$emit('delete', template.id)"
            class="btn btn-error btn-outline"
          >
            Eliminar
          </button>

          <div class="flex gap-2">
            <button
              @click="$emit('cancel')"
              class="btn btn-ghost"
              :disabled="isSaving"
            >
              Cancelar
            </button>
            <button
              @click="handleSave"
              class="btn btn-primary"
              :disabled="!isValid || isSaving"
            >
              <span v-if="isSaving" class="loading loading-spinner loading-sm"></span>
              Guardar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { MessageTemplate, TemplateUpdate, ModuleInfo } from '../composables/useTemplateManager'

interface Props {
  template: MessageTemplate
  isSaving: boolean
  availableModules: ModuleInfo[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'save', updates: TemplateUpdate): void
  (e: 'cancel'): void
  (e: 'delete', templateId: string): void
  (e: 'set-default', templateId: string): void
}>()

// Local editable copy
const localTemplate = ref<MessageTemplate>({ ...props.template })

// Watch for template changes
watch(() => props.template, (newTemplate) => {
  localTemplate.value = { ...newTemplate }
}, { deep: true })

// Extract variables from template text
const detectedVariables = computed(() => {
  const pattern = /\{([a-zA-Z_][a-zA-Z0-9_]*)\}/g
  const matches: string[] = []
  let match
  const text = localTemplate.value.template_text || ''
  while ((match = pattern.exec(text)) !== null) {
    if (!matches.includes(match[1])) {
      matches.push(match[1])
    }
  }
  return matches
})

// Preview with sample values
const previewText = computed(() => {
  let text = localTemplate.value.template_text || ''

  // Sample values for common variables
  const sampleValues: Record<string, string> = {
    marca: 'Toyota',
    color: 'gris',
    patente: 'BBCL-45',
    nombre: 'Juan',
    edad: '5 anos',
    descripcion: 'camisa azul',
    producto: 'Coca Cola',
    precio: '$990',
    descuento: '20%',
  }

  // Replace variables with sample values
  for (const variable of detectedVariables.value) {
    const value = sampleValues[variable] || `[${variable}]`
    text = text.replace(new RegExp(`\\{${variable}\\}`, 'g'), value)
  }

  return text
})

// Validation
const isValid = computed(() => {
  return (
    localTemplate.value.name?.trim().length > 0 &&
    localTemplate.value.template_text?.trim().length > 0 &&
    localTemplate.value.module?.trim().length > 0
  )
})

// Save handler
const handleSave = () => {
  if (!isValid.value) return

  const updates: TemplateUpdate = {
    name: localTemplate.value.name,
    description: localTemplate.value.description,
    template_text: localTemplate.value.template_text,
    variables: detectedVariables.value,
    module: localTemplate.value.module,
    active: localTemplate.value.active,
    is_default: localTemplate.value.is_default,
    use_announcement_sound: localTemplate.value.use_announcement_sound,
  }

  emit('save', updates)
}
</script>
