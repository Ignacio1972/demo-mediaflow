<template>
  <dialog class="modal modal-open">
    <div class="modal-box max-w-lg">
      <h3 class="font-bold text-lg flex items-center gap-2">
        <span class="text-2xl">📂</span>
        Nueva Categoría
      </h3>

      <form @submit.prevent="handleSubmit" class="mt-6 space-y-4">
        <!-- Name -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">Nombre *</span>
          </label>
          <input
            v-model="formData.name"
            type="text"
            class="input input-bordered"
            placeholder="Ej: Pedidos Listos"
            required
            maxlength="100"
            @input="generateId"
          />
        </div>

        <!-- ID (auto-generated) -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">ID</span>
            <span class="label-text-alt text-base-content/50">Auto-generado</span>
          </label>
          <input
            v-model="formData.id"
            type="text"
            class="input input-bordered font-mono"
            placeholder="pedidos_listos"
            required
            maxlength="50"
            pattern="^[a-z0-9_]+$"
          />
          <label class="label">
            <span v-if="!isIdValid" class="label-text-alt text-error">
              {{ idError }}
            </span>
            <span v-else class="label-text-alt text-success">
              ID disponible
            </span>
          </label>
        </div>

        <!-- Visual Settings -->
        <div class="grid grid-cols-2 gap-4">
          <!-- Icon -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Icono</span>
            </label>
            <div class="flex gap-2">
              <input
                v-model="formData.icon"
                type="text"
                class="input input-bordered flex-1 text-center text-2xl"
                placeholder="📦"
                maxlength="4"
              />
            </div>
            <!-- Quick Emoji Picker -->
            <div class="flex flex-wrap gap-1 mt-2">
              <button
                v-for="emoji in quickEmojis"
                :key="emoji"
                type="button"
                class="btn btn-ghost btn-xs text-lg"
                @click="formData.icon = emoji"
              >
                {{ emoji }}
              </button>
            </div>
          </div>

          <!-- Color -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Color</span>
            </label>
            <div class="flex gap-2">
              <input
                v-model="formData.color"
                type="color"
                class="w-12 h-12 rounded-lg cursor-pointer"
              />
              <input
                v-model="formData.color"
                type="text"
                class="input input-bordered flex-1 font-mono text-sm"
                placeholder="#FF4444"
                maxlength="7"
              />
            </div>
            <!-- Quick Color Picker -->
            <div class="flex flex-wrap gap-1 mt-2">
              <button
                v-for="color in quickColors"
                :key="color"
                type="button"
                class="w-5 h-5 rounded-full cursor-pointer hover:scale-110 transition-transform"
                :style="{ backgroundColor: color }"
                @click="formData.color = color"
              />
            </div>
          </div>
        </div>

        <!-- Preview -->
        <div class="bg-base-200 rounded-lg p-4">
          <p class="text-sm text-base-content/60 mb-2">Vista Previa:</p>
          <span
            class="badge gap-1 text-white"
            :style="{ backgroundColor: formData.color }"
          >
            {{ formData.icon }} {{ formData.name || 'Nueva Categoría' }}
          </span>
        </div>

        <!-- Actions -->
        <div class="modal-action">
          <button
            type="button"
            class="btn btn-ghost"
            @click="emit('close')"
          >
            Cancelar
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="!isFormValid"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Crear Categoría
          </button>
        </div>
      </form>
    </div>

    <form method="dialog" class="modal-backdrop">
      <button @click="emit('close')">close</button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
import { reactive, computed } from 'vue'

const props = defineProps<{
  existingIds: string[]
}>()

const emit = defineEmits<{
  close: []
  create: [data: { id: string; name: string; icon: string; color: string }]
}>()

// Quick selection options
const quickEmojis = ['📦', '🎉', '📢', '🎵', '🔔', '⭐', '🛒', '🎁', '📻', '🚀']
const quickColors = [
  '#EF4444', '#F97316', '#22C55E', '#3B82F6', '#8B5CF6',
  '#EC4899', '#6B7280', '#14B8A6', '#F59E0B', '#6366F1',
]

// Form data
const formData = reactive({
  name: '',
  id: '',
  icon: '📦',
  color: '#3B82F6',
})

// Generate ID from name
const generateId = () => {
  formData.id = formData.name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .substring(0, 50)
}

// Validate ID
const idError = computed(() => {
  if (!formData.id) return 'El ID es requerido'
  if (!/^[a-z0-9_]+$/.test(formData.id)) return 'Solo letras minúsculas, números y guiones bajos'
  if (props.existingIds.includes(formData.id)) return 'Este ID ya existe'
  return ''
})

const isIdValid = computed(() => {
  return formData.id && !idError.value
})

// Form validation
const isFormValid = computed(() => {
  return formData.name.trim() && isIdValid.value
})

// Handle submit
const handleSubmit = () => {
  if (!isFormValid.value) return

  emit('create', {
    id: formData.id,
    name: formData.name.trim(),
    icon: formData.icon || '📦',
    color: formData.color || '#6B7280',
  })
}
</script>
