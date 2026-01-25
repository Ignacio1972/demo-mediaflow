<template>
  <div class="vehicle-announcement">
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
          <TruckIcon class="w-5 h-5 text-primary" />
        </div>
        <h1 class="text-3xl font-bold tracking-tight">
          Vehículos Mal Estacionados
        </h1>
      </div>
      <p class="text-base-content/50 ml-13">
        Genera anuncios de audio con pronunciación correcta de patentes
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
      <VehicleForm
        v-model:marca="marca"
        v-model:color="color"
        v-model:platePart1="platePart1"
        v-model:platePart2="platePart2"
        v-model:platePart3="platePart3"
        v-model:voiceId="voiceId"
        v-model:numberMode="numberMode"
        v-model:useAnnouncementSound="useAnnouncementSound"
        :brands="brands"
        :colors="colors"
        :voices="voices"
        :plate-validation="plateValidation"
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
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, nextTick } from 'vue'
import { TruckIcon, ExclamationCircleIcon, ArrowLeftIcon } from '@heroicons/vue/24/outline'
import VehicleForm from './components/VehicleForm.vue'
import PreviewText from './components/PreviewText.vue'
import AudioResult from './components/AudioResult.vue'
import { useVehicleAnnouncement } from './composables/useVehicleAnnouncement'

// Ref for auto-scroll
const audioResultRef = ref<HTMLElement | null>(null)

const {
  // Form state
  marca,
  color,
  platePart1,
  platePart2,
  platePart3,
  voiceId,
  numberMode,
  useAnnouncementSound,

  // Options
  brands,
  colors,
  voices,

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

// Auto-scroll when generation starts
watch(loadingGenerate, (isLoading) => {
  if (isLoading) {
    nextTick(() => {
      audioResultRef.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    })
  }
})
</script>
