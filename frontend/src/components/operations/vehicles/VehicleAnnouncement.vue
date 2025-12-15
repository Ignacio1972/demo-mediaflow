<template>
  <div class="vehicle-announcement">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-base-content">
        Vehiculos Mal Estacionados
      </h1>
      <p class="text-base-content/60 mt-1">
        Genera anuncios de audio para vehiculos mal estacionados con pronunciacion correcta de patentes
      </p>
    </div>

    <!-- Error alert -->
    <div v-if="error" class="alert alert-error mb-6">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="stroke-current shrink-0 h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <span>{{ error }}</span>
      <button @click="error = null" class="btn btn-sm btn-ghost">
        Cerrar
      </button>
    </div>

    <!-- Main content -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Left column: Form -->
      <VehicleForm
        v-model:marca="marca"
        v-model:color="color"
        v-model:platePart1="platePart1"
        v-model:platePart2="platePart2"
        v-model:platePart3="platePart3"
        v-model:voiceId="voiceId"
        v-model:musicFile="musicFile"
        v-model:template="template"
        v-model:numberMode="numberMode"
        :brands="brands"
        :colors="colors"
        :templates="templates"
        :voices="voices"
        :music-tracks="musicTracks"
        :plate-validation="plateValidation"
        :is-form-valid="isFormValid"
        :loading-voices="loadingVoices"
        :loading-generate="loadingGenerate"
        @generate="generateAnnouncement"
      />

      <!-- Right column: Preview and Result -->
      <div class="space-y-6">
        <!-- Text Preview -->
        <PreviewText
          :preview="previewText"
          :loading="loadingPreview"
        />

        <!-- Audio Result (shown after generation) -->
        <AudioResult
          v-if="generatedAudio"
          :audio="generatedAudio"
          @reset="resetForm"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import VehicleForm from './components/VehicleForm.vue'
import PreviewText from './components/PreviewText.vue'
import AudioResult from './components/AudioResult.vue'
import { useVehicleAnnouncement } from './composables/useVehicleAnnouncement'

const {
  // Form state
  marca,
  color,
  platePart1,
  platePart2,
  platePart3,
  voiceId,
  musicFile,
  template,
  numberMode,

  // Options
  brands,
  colors,
  templates,
  voices,
  musicTracks,

  // Preview
  previewText,
  plateValidation,

  // Generated audio
  generatedAudio,

  // Loading states
  loadingPreview,
  loadingGenerate,
  loadingVoices,

  // Error
  error,

  // Computed
  isFormValid,

  // Actions
  initialize,
  generateAnnouncement,
  resetForm
} = useVehicleAnnouncement()

// Initialize on mount
onMounted(() => {
  initialize()
})
</script>
