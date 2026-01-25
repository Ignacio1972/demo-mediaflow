<template>
  <div class="preview-text">
    <div class="card bg-base-100 border-2 border-base-300 rounded-2xl shadow-sm">
      <div class="card-body p-6">
        <!-- Header -->
        <div class="mb-6">
          <h2 class="text-xl font-bold tracking-tight">Vista Previa</h2>
          <p class="text-sm text-base-content/50 mt-1">Texto que se convertirá a audio</p>
        </div>

        <!-- Loading state -->
        <div v-if="loading" class="flex flex-col items-center justify-center py-12">
          <span class="loading loading-spinner loading-lg text-primary"></span>
          <p class="text-sm text-base-content/50 mt-4">Generando vista previa...</p>
        </div>

        <!-- Empty state -->
        <div
          v-else-if="!preview"
          class="flex flex-col items-center justify-center py-12"
        >
          <!-- Decorative container -->
          <div class="relative mb-6">
            <div class="absolute -inset-4 bg-primary/5 rounded-full animate-pulse"></div>
            <div class="relative flex items-center justify-center w-20 h-20 bg-base-200 rounded-2xl">
              <DocumentTextIcon class="w-10 h-10 text-base-content/20" />
            </div>
          </div>
          <h3 class="text-lg font-semibold mb-2">Sin vista previa</h3>
          <p class="text-base-content/50 text-center text-sm max-w-xs">
            Selecciona las opciones para ver cómo quedará el mensaje
          </p>
        </div>

        <!-- Preview content -->
        <div v-else>
          <!-- Announcement sound indicator -->
          <div
            v-if="preview.use_announcement_sound"
            class="flex items-center gap-2 mb-4 p-3 bg-warning/10 border border-warning/20 rounded-xl"
          >
            <SpeakerWaveIcon class="w-5 h-5 text-warning shrink-0" />
            <span class="text-sm text-warning">
              Este mensaje incluirá sonido de anuncio (intro + outro)
            </span>
          </div>

          <div class="bg-base-200/50 border-2 border-base-300 rounded-xl p-5">
            <p class="leading-relaxed text-base-content">{{ preview.text }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { DocumentTextIcon, SpeakerWaveIcon } from '@heroicons/vue/24/outline'
import type { PreviewResponse } from '../composables/useScheduleAnnouncement'

defineProps<{
  preview: PreviewResponse | null
  loading: boolean
}>()
</script>
