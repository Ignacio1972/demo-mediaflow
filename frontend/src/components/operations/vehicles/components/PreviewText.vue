<template>
  <div class="preview-text">
    <div class="card bg-base-100 border-2 border-base-300 rounded-2xl shadow-sm">
      <div class="card-body p-6">
        <!-- Header -->
        <div class="mb-6">
          <h2 class="text-xl font-bold tracking-tight">Vista Previa</h2>
          <p class="text-sm text-base-content/50 mt-1">Edita el texto si deseas y regenera el audio</p>
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
            Completa los datos del vehículo para ver cómo quedará el mensaje
          </p>
        </div>

        <!-- Preview content - editable -->
        <div v-else class="space-y-4">
          <textarea
            v-model="localText"
            rows="4"
            class="textarea bg-base-200/50 border-2 border-base-300 focus:border-primary focus:bg-base-100 rounded-xl w-full leading-relaxed transition-all duration-200"
          ></textarea>

          <!-- Regenerate button -->
          <button
            @click="handleRegenerate"
            class="btn btn-outline btn-primary w-full h-12 rounded-xl font-semibold transition-all duration-200"
            :disabled="regenerating || !canRegenerate"
          >
            <span v-if="regenerating" class="loading loading-spinner loading-sm"></span>
            <template v-else>
              <ArrowPathIcon class="w-5 h-5" />
              <span>Regenerar Audio</span>
            </template>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { DocumentTextIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'
import type { TextPreviewResponse } from '../composables/useVehicleAnnouncement'

const props = defineProps<{
  preview: TextPreviewResponse | null
  loading: boolean
  regenerating: boolean
  hasAudio: boolean
}>()

const emit = defineEmits<{
  (e: 'regenerate', text: string): void
}>()

// Local editable text
const localText = ref('')

// Track if text has been modified
const hasChanges = computed(() => {
  return props.preview && localText.value !== props.preview.original
})

// Allow regeneration when text changed OR when there's already an audio (to regenerate with different voice, etc)
const canRegenerate = computed(() => {
  return hasChanges.value || props.hasAudio
})

// Sync local text when preview changes
watch(
  () => props.preview,
  (newPreview) => {
    if (newPreview) {
      localText.value = newPreview.original
    }
  },
  { immediate: true }
)

function handleRegenerate() {
  emit('regenerate', localText.value)
}
</script>
