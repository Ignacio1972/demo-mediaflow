<template>
  <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
    <div>
      <h1 class="text-2xl font-bold flex items-center gap-3">
        <BookOpenIcon class="h-7 w-7 text-primary" />
        Biblioteca de Audio
      </h1>
      <p class="text-base-content/60 mt-1">
        {{ total }} mensaje{{ total !== 1 ? 's' : '' }} guardado{{ total !== 1 ? 's' : '' }}
      </p>
    </div>

    <div class="flex items-center gap-3">
      <!-- Selection Mode Toggle -->
      <button
        class="btn btn-sm"
        :class="{ 'btn-active': selectionMode }"
        @click="emit('toggle-selection')"
      >
        <CheckCircleIcon class="h-4 w-4" />
        {{ selectionMode ? 'Cancelar' : 'Seleccionar' }}
      </button>

      <!-- Upload Button -->
      <button
        class="btn btn-sm btn-secondary"
        @click="emit('upload')"
      >
        <ArrowUpTrayIcon class="h-4 w-4" />
        Subir Audio
      </button>

      <!-- View Toggle -->
      <ViewToggle
        :model-value="viewMode"
        @update:model-value="emit('update:viewMode', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  BookOpenIcon,
  CheckCircleIcon,
  ArrowUpTrayIcon
} from '@heroicons/vue/24/outline'
import ViewToggle from './ViewToggle.vue'
import type { ViewMode } from '../types/library.types'

defineProps<{
  total: number
  selectionMode: boolean
  viewMode: ViewMode
}>()

const emit = defineEmits<{
  'toggle-selection': []
  'upload': []
  'update:viewMode': [mode: ViewMode]
}>()
</script>
