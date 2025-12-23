<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { CampaignCreate } from '@/types/campaign'
import IconSelector from '@/components/shared/ui/IconSelector.vue'

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

// Available colors
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

// Generate ID from name
const generatedId = computed(() => {
  return name.value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remove accents
    .replace(/[^a-z0-9\s]/g, '')     // Remove special chars
    .replace(/\s+/g, '_')            // Spaces to underscore
    .slice(0, 30)
})

// Validation
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
      <h3 class="font-bold text-lg mb-4">Nueva Campaña</h3>

      <!-- Name -->
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

      <!-- Icon selector -->
      <div class="form-control mb-4">
        <label class="label">
          <span class="label-text">Icono</span>
        </label>
        <div class="p-3 bg-base-200 rounded-lg">
          <IconSelector v-model="selectedIcon" />
        </div>
      </div>

      <!-- Color selector -->
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
          Crear Campaña
        </button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop" @click="close">
      <button>close</button>
    </form>
  </dialog>
</template>
