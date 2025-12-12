<template>
  <div class="preview-text">
    <div class="card bg-base-200 shadow-lg">
      <div class="card-body">
        <h2 class="card-title text-lg mb-4">Vista Previa del Mensaje</h2>

        <!-- Loading state -->
        <div v-if="loading" class="flex justify-center py-8">
          <span class="loading loading-dots loading-lg"></span>
        </div>

        <!-- Empty state -->
        <div
          v-else-if="!preview"
          class="text-center py-8 text-base-content/50"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-12 w-12 mx-auto mb-3 opacity-50"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <p>Complete los datos del vehiculo para ver la vista previa</p>
        </div>

        <!-- Preview content -->
        <div v-else class="space-y-4">
          <!-- Normalized text (what TTS will say) -->
          <div>
            <label class="label">
              <span class="label-text font-medium text-primary">
                Texto para TTS (normalizado)
              </span>
            </label>
            <div class="bg-base-300 rounded-lg p-4 text-base-content">
              <p class="leading-relaxed">{{ preview.normalized }}</p>
            </div>
          </div>

          <!-- Original text -->
          <div class="collapse collapse-arrow bg-base-300">
            <input type="checkbox" />
            <div class="collapse-title text-sm font-medium">
              Ver texto original (sin normalizar)
            </div>
            <div class="collapse-content">
              <p class="text-base-content/70 text-sm">{{ preview.original }}</p>
            </div>
          </div>

          <!-- Plate pronunciation details -->
          <div v-if="preview.plate_info" class="flex items-center gap-2 text-sm">
            <span
              class="badge"
              :class="preview.plate_info.valid ? 'badge-success' : 'badge-error'"
            >
              {{ preview.plate_info.format || 'Formato personalizado' }}
            </span>
            <span class="text-base-content/60">
              Patente: {{ preview.components.patente_original }}
              <span class="mx-1">→</span>
              {{ preview.components.patente_normalized }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TextPreviewResponse } from '../composables/useVehicleAnnouncement'

defineProps<{
  preview: TextPreviewResponse | null
  loading: boolean
}>()
</script>
