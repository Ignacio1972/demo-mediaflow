<template>
  <div class="category-form">
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <!-- Header with Preview -->
        <div class="flex items-center justify-between mb-6">
          <h2 class="card-title text-lg">Editar Categoría</h2>

          <!-- Live Preview Badge -->
          <div class="flex items-center gap-2">
            <span class="text-sm text-base-content/60">Preview:</span>
            <span
              class="badge gap-1 text-white"
              :style="{ backgroundColor: formData.color }"
            >
              {{ formData.icon }} {{ formData.name || 'Sin nombre' }}
            </span>
          </div>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Basic Info Section -->
          <div class="grid md:grid-cols-2 gap-4">
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
              />
            </div>

            <!-- ID (read-only) -->
            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">ID</span>
                <span class="label-text-alt text-base-content/50">No editable</span>
              </label>
              <input
                :value="category.id"
                type="text"
                class="input input-bordered bg-base-200"
                disabled
              />
            </div>
          </div>

          <!-- Visual Section -->
          <div class="divider">Apariencia</div>

          <div class="grid md:grid-cols-2 gap-4">
            <!-- Icon -->
            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Icono (Emoji)</span>
              </label>
              <div class="flex gap-2">
                <input
                  v-model="formData.icon"
                  type="text"
                  class="input input-bordered flex-1 text-center text-2xl"
                  placeholder="📦"
                  maxlength="4"
                />
                <div class="dropdown dropdown-end">
                  <label tabindex="0" class="btn btn-outline">
                    Emojis
                  </label>
                  <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52 mt-2">
                    <li class="menu-title">Comunes</li>
                    <li>
                      <div class="grid grid-cols-5 gap-1">
                        <button
                          v-for="emoji in commonEmojis"
                          :key="emoji"
                          type="button"
                          class="btn btn-ghost btn-sm text-xl p-1"
                          @click="formData.icon = emoji"
                        >
                          {{ emoji }}
                        </button>
                      </div>
                    </li>
                  </ul>
                </div>
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
                  class="w-14 h-12 rounded-lg cursor-pointer border-2 border-base-300"
                />
                <input
                  v-model="formData.color"
                  type="text"
                  class="input input-bordered flex-1 font-mono"
                  placeholder="#FF4444"
                  maxlength="7"
                />
              </div>
              <!-- Preset Colors -->
              <div class="flex gap-1 mt-2">
                <button
                  v-for="color in presetColors"
                  :key="color"
                  type="button"
                  class="w-6 h-6 rounded-full cursor-pointer hover:scale-110 transition-transform border-2"
                  :class="{ 'border-primary': formData.color === color, 'border-transparent': formData.color !== color }"
                  :style="{ backgroundColor: color }"
                  @click="formData.color = color"
                />
              </div>
            </div>
          </div>

          <!-- Status Section -->
          <div class="divider">Estado</div>

          <div class="flex items-center justify-between p-4 bg-base-200 rounded-lg">
            <div>
              <h3 class="font-medium">Categoría Activa</h3>
              <p class="text-sm text-base-content/60">
                Las categorías inactivas no aparecen en la biblioteca
              </p>
            </div>
            <input
              v-model="formData.active"
              type="checkbox"
              class="toggle toggle-primary toggle-lg"
            />
          </div>

          <!-- Statistics -->
          <div v-if="category.message_count !== undefined" class="stats shadow w-full">
            <div class="stat">
              <div class="stat-figure text-primary">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
              </div>
              <div class="stat-title">Mensajes</div>
              <div class="stat-value text-primary">{{ category.message_count }}</div>
              <div class="stat-desc">En esta categoría</div>
            </div>

            <div class="stat">
              <div class="stat-figure text-secondary">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="stat-title">Creada</div>
              <div class="stat-value text-secondary text-lg">{{ formatDate(category.created_at) }}</div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex flex-col sm:flex-row gap-3 pt-4 border-t border-base-300">
            <button
              type="button"
              class="btn btn-error btn-outline flex-none"
              @click="emit('delete', category.id)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Eliminar
            </button>

            <div class="flex-1"></div>

            <button
              type="button"
              class="btn btn-ghost"
              @click="resetForm"
            >
              Cancelar
            </button>

            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isSaving || !hasChanges"
            >
              <span v-if="isSaving" class="loading loading-spinner loading-sm"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              Guardar Cambios
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import type { Category, CategoryUpdate } from '../composables/useCategoryEditor'

const props = defineProps<{
  category: Category
  isSaving: boolean
}>()

const emit = defineEmits<{
  save: [updates: CategoryUpdate]
  cancel: []
  delete: [categoryId: string]
}>()

// Common emojis for quick selection
const commonEmojis = [
  '📦', '🎉', '📢', '🎵', '🔔',
  '⭐', '🏷️', '📌', '🎯', '💡',
  '🛒', '🎁', '📻', '🎤', '📣',
  '🚀', '💬', '📝', '🔥', '✨',
]

// Preset colors
const presetColors = [
  '#EF4444', '#F97316', '#F59E0B', '#84CC16', '#22C55E',
  '#14B8A6', '#06B6D4', '#3B82F6', '#6366F1', '#8B5CF6',
  '#A855F7', '#D946EF', '#EC4899', '#F43F5E', '#6B7280',
]

// Form data
const formData = reactive({
  name: '',
  icon: '',
  color: '',
  active: true,
})

// Initialize form data when category changes
watch(() => props.category, (newCategory) => {
  formData.name = newCategory.name
  formData.icon = newCategory.icon || '📁'
  formData.color = newCategory.color || '#6B7280'
  formData.active = newCategory.active
}, { immediate: true })

// Check if form has changes
const hasChanges = computed(() => {
  return (
    formData.name !== props.category.name ||
    formData.icon !== (props.category.icon || '📁') ||
    formData.color !== (props.category.color || '#6B7280') ||
    formData.active !== props.category.active
  )
})

// Reset form to original values
const resetForm = () => {
  formData.name = props.category.name
  formData.icon = props.category.icon || '📁'
  formData.color = props.category.color || '#6B7280'
  formData.active = props.category.active
  emit('cancel')
}

// Handle form submission
const handleSubmit = () => {
  if (!hasChanges.value) return

  const updates: CategoryUpdate = {}

  if (formData.name !== props.category.name) {
    updates.name = formData.name
  }
  if (formData.icon !== (props.category.icon || '📁')) {
    updates.icon = formData.icon
  }
  if (formData.color !== (props.category.color || '#6B7280')) {
    updates.color = formData.color
  }
  if (formData.active !== props.category.active) {
    updates.active = formData.active
  }

  emit('save', updates)
}

// Format date
const formatDate = (dateString?: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('es-CL', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
</script>
