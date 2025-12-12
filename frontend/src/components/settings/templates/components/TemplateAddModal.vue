<template>
  <dialog class="modal modal-open">
    <div class="modal-box max-w-2xl">
      <h3 class="font-bold text-lg mb-4">Nueva Plantilla</h3>

      <div class="space-y-4">
        <!-- ID -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">ID</span>
            <span class="label-text-alt text-base-content/60">Solo minusculas, numeros y guion bajo</span>
          </label>
          <input
            v-model="formData.id"
            type="text"
            placeholder="vehiculos_estandar"
            class="input input-bordered w-full"
            :class="{ 'input-error': formData.id && !isIdValid }"
          />
          <label v-if="formData.id && !isIdValid" class="label">
            <span class="label-text-alt text-error">
              {{ idError }}
            </span>
          </label>
        </div>

        <!-- Name -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">Nombre</span>
          </label>
          <input
            v-model="formData.name"
            type="text"
            placeholder="Vehiculos - Estandar"
            class="input input-bordered w-full"
            @input="autoGenerateId"
          />
        </div>

        <!-- Description -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">Descripcion</span>
            <span class="label-text-alt text-base-content/60">Opcional</span>
          </label>
          <input
            v-model="formData.description"
            type="text"
            placeholder="Breve descripcion de esta plantilla"
            class="input input-bordered w-full"
          />
        </div>

        <!-- Module -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">Modulo</span>
          </label>
          <select
            v-model="formData.module"
            class="select select-bordered w-full"
          >
            <option value="" disabled>Selecciona un modulo</option>
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
            v-model="formData.template_text"
            placeholder="Atencion clientes: Se solicita al dueno del vehiculo marca {marca} color {color}..."
            class="textarea textarea-bordered w-full h-32 font-mono text-sm"
          ></textarea>
          <label class="label">
            <span class="label-text-alt text-base-content/60">
              Usa {'{'}variable{'}'} para insertar valores dinamicos
            </span>
          </label>
        </div>

        <!-- Detected Variables -->
        <div v-if="detectedVariables.length > 0" class="form-control">
          <label class="label">
            <span class="label-text font-medium">Variables Detectadas</span>
          </label>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="variable in detectedVariables"
              :key="variable"
              class="badge badge-primary"
            >
              {{ variable }}
            </span>
          </div>
        </div>

        <!-- Is Default -->
        <div class="form-control">
          <label class="label cursor-pointer justify-start gap-4">
            <input
              type="checkbox"
              v-model="formData.is_default"
              class="toggle toggle-primary"
            />
            <span class="label-text">Establecer como plantilla por defecto para este modulo</span>
          </label>
        </div>
      </div>

      <div class="modal-action">
        <button @click="$emit('close')" class="btn btn-ghost">
          Cancelar
        </button>
        <button
          @click="handleCreate"
          class="btn btn-primary"
          :disabled="!isFormValid"
        >
          Crear Plantilla
        </button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button @click="$emit('close')">close</button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ModuleInfo } from '../composables/useTemplateManager'

interface Props {
  existingIds: string[]
  availableModules: ModuleInfo[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'create', data: any): void
}>()

// Form data
const formData = ref({
  id: '',
  name: '',
  description: '',
  template_text: '',
  module: 'vehicles',
  is_default: false,
})

// ID already typed manually
const idManuallyEdited = ref(false)

// Auto-generate ID from name
const autoGenerateId = () => {
  if (idManuallyEdited.value) return

  formData.value.id = formData.value.name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .substring(0, 50)
}

// Detect variables from template text
const detectedVariables = computed(() => {
  const pattern = /\{([a-zA-Z_][a-zA-Z0-9_]*)\}/g
  const matches: string[] = []
  let match
  while ((match = pattern.exec(formData.value.template_text)) !== null) {
    if (!matches.includes(match[1])) {
      matches.push(match[1])
    }
  }
  return matches
})

// ID validation
const isIdValid = computed(() => {
  const id = formData.value.id
  if (!id) return false
  if (!/^[a-z0-9_]+$/.test(id)) return false
  if (props.existingIds.includes(id)) return false
  return true
})

const idError = computed(() => {
  const id = formData.value.id
  if (!id) return 'ID requerido'
  if (!/^[a-z0-9_]+$/.test(id)) return 'Solo minusculas, numeros y guion bajo'
  if (props.existingIds.includes(id)) return 'Este ID ya existe'
  return ''
})

// Form validation
const isFormValid = computed(() => {
  return (
    isIdValid.value &&
    formData.value.name.trim().length > 0 &&
    formData.value.template_text.trim().length > 0 &&
    formData.value.module.trim().length > 0
  )
})

// Create handler
const handleCreate = () => {
  if (!isFormValid.value) return

  emit('create', {
    id: formData.value.id,
    name: formData.value.name,
    description: formData.value.description || null,
    template_text: formData.value.template_text,
    variables: detectedVariables.value,
    module: formData.value.module,
    is_default: formData.value.is_default,
    active: true,
  })
}
</script>
