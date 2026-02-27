<template>
  <div class="flex flex-wrap items-center justify-between gap-4 mb-4 md:mb-6">
    <div class="flex items-center gap-3 text-sm text-base-content/50">
      <span>{{ total }} mensaje{{ total !== 1 ? 's' : '' }}</span>
      <span class="text-base-content/20">·</span>
      <router-link
        to="/recent"
        class="inline-flex items-center gap-1.5 text-primary hover:text-primary/80 transition-colors"
      >
        <ClockIcon class="h-4 w-4" />
        Recientes
      </router-link>
    </div>

    <div class="flex items-center gap-3">
      <!-- Selection Mode Toggle (hidden on mobile) -->
      <button
        class="hidden md:inline-flex btn btn-sm"
        :class="{ 'btn-active': selectionMode }"
        @click="emit('toggle-selection')"
      >
        <CheckCircleIcon class="h-4 w-4" />
        {{ selectionMode ? 'Cancelar' : 'Seleccionar' }}
      </button>

      <!-- Upload Button (hidden on mobile) -->
      <button
        class="hidden md:inline-flex btn btn-sm btn-secondary"
        @click="emit('upload')"
      >
        <ArrowUpTrayIcon class="h-4 w-4" />
        Subir Audio
      </button>

      <!-- View Toggle (hidden on mobile) -->
      <ViewToggle
        class="hidden md:flex"
        :model-value="viewMode"
        @update:model-value="emit('update:viewMode', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  CheckCircleIcon,
  ArrowUpTrayIcon,
  ClockIcon
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
