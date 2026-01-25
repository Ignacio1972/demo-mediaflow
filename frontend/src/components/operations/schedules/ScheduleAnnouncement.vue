<template>
  <div class="schedule-announcement">
    <!-- Header - hidden on mobile -->
    <div class="mb-10 hidden md:block">
      <!-- Back button -->
      <router-link
        to="/operations"
        class="inline-flex items-center gap-2 text-sm text-base-content/50 hover:text-primary transition-colors mb-4"
      >
        <ArrowLeftIcon class="w-4 h-4" />
        Operaciones
      </router-link>

      <div class="flex items-center gap-3 mb-2">
        <div class="flex items-center justify-center w-10 h-10 bg-primary/10 rounded-xl">
          <ClockIcon class="w-5 h-5 text-primary" />
        </div>
        <h1 class="text-3xl font-bold tracking-tight">
          Anuncio de Cierre
        </h1>
      </div>
      <p class="text-base-content/50 ml-13">
        Genera anuncios de audio para el cierre del local
      </p>
    </div>

    <!-- Error alert -->
    <div v-if="error" class="alert bg-error/10 border-2 border-error/20 rounded-2xl mb-6">
      <ExclamationCircleIcon class="w-6 h-6 text-error shrink-0" />
      <span class="text-error">{{ error }}</span>
      <button @click="error = null" class="btn btn-sm btn-ghost rounded-lg hover:bg-error/10">
        Cerrar
      </button>
    </div>

    <!-- Main content -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Left column: Form -->
      <ScheduleForm
        v-model:variant="variant"
        v-model:minutes="minutes"
        v-model:voice-id="voiceId"
        v-model:use-announcement-sound="useAnnouncementSound"
        :available-variants="availableVariants"
        :minutes-options="minutesOptions"
        :voices="voices"
        :show-minutes="showMinutes"
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
import { ClockIcon, ExclamationCircleIcon, ArrowLeftIcon } from '@heroicons/vue/24/outline'
import ScheduleForm from './components/ScheduleForm.vue'
import PreviewText from './components/PreviewText.vue'
import AudioResult from './components/AudioResult.vue'
import { useScheduleAnnouncement } from './composables/useScheduleAnnouncement'

const {
  // Form state
  variant,
  minutes,
  voiceId,
  useAnnouncementSound,

  // Options
  availableVariants,
  minutesOptions,
  voices,

  // Computed
  showMinutes,
  isFormValid,

  // Preview
  previewText,

  // Generated audio
  generatedAudio,

  // Loading states
  loadingPreview,
  loadingGenerate,
  loadingVoices,

  // Error
  error,

  // Actions
  initialize,
  generateAnnouncement,
  resetForm
} = useScheduleAnnouncement()

// Initialize on mount
onMounted(() => {
  initialize()
})
</script>

<style scoped>
.ml-13 {
  margin-left: 3.25rem;
}
</style>
