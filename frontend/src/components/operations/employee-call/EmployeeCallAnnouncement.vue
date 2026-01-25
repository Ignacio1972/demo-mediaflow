<template>
  <div class="employee-call-announcement">
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
          <PhoneIcon class="w-5 h-5 text-primary" />
        </div>
        <h1 class="text-3xl font-bold tracking-tight">
          Llamado a Empleado o Cliente
        </h1>
      </div>
      <p class="text-base-content/50 ml-13">
        Genera anuncios para solicitar la presencia de personas
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
      <CallForm
        v-model:call-type="callType"
        v-model:nombre="nombre"
        v-model:ubicacion="ubicacion"
        v-model:voice-id="voiceId"
        v-model:use-announcement-sound="useAnnouncementSound"
        :locations="locations"
        :voices="voices"
        :is-form-valid="isFormValid"
        :loading-voices="loadingVoices"
        :loading-generate="loadingGenerate"
        @generate="generateAnnouncement"
      />

      <!-- Right column: Result and Preview -->
      <div class="space-y-6">
        <!-- Loading indicator while generating -->
        <div
          ref="audioResultRef"
          v-if="loadingGenerate"
          class="card bg-base-100 border-2 border-primary/30 rounded-2xl shadow-sm"
        >
          <div class="card-body p-6 flex flex-col items-center justify-center gap-4">
            <span class="loading loading-spinner loading-lg text-primary"></span>
            <p class="text-sm text-base-content/60">Generando audio...</p>
          </div>
        </div>

        <!-- Audio Result (shown after generation) -->
        <AudioResult
          v-if="generatedAudio && !loadingGenerate"
          :audio="generatedAudio"
          @reset="resetForm"
        />

        <!-- Text Preview -->
        <PreviewText
          :preview="previewText"
          :loading="loadingPreview"
          :regenerating="loadingGenerate"
          :has-audio="hasAudio"
          @regenerate="handleRegenerate"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, nextTick } from 'vue'
import { PhoneIcon, ExclamationCircleIcon, ArrowLeftIcon } from '@heroicons/vue/24/outline'
import CallForm from './components/CallForm.vue'
import PreviewText from './components/PreviewText.vue'
import AudioResult from './components/AudioResult.vue'
import { useEmployeeCallAnnouncement } from './composables/useEmployeeCallAnnouncement'

// Ref for auto-scroll
const audioResultRef = ref<HTMLElement | null>(null)

const {
  // Form state
  callType,
  nombre,
  ubicacion,
  voiceId,
  useAnnouncementSound,

  // Options
  locations,
  voices,

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

  // Computed
  isFormValid,
  hasAudio,

  // Actions
  initialize,
  generateAnnouncement,
  resetForm
} = useEmployeeCallAnnouncement()

// Initialize on mount
onMounted(() => {
  initialize()
})

// Handle regenerate with custom text
async function handleRegenerate(customText: string) {
  await generateAnnouncement(customText)
}

// Auto-scroll when generation starts
watch(loadingGenerate, (isLoading) => {
  if (isLoading) {
    nextTick(() => {
      audioResultRef.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    })
  }
})
</script>

<style scoped>
.ml-13 {
  margin-left: 3.25rem;
}
</style>
