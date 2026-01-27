<template>
  <div class="audio-result">
    <!-- Success Toast -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="showSuccessToast"
        class="fixed inset-0 flex items-center justify-center z-50 pointer-events-none pb-32"
      >
        <div class="bg-success/80 text-success-content px-10 py-3 rounded-xl shadow-lg">
          <span class="font-semibold">Audio enviado exitosamente</span>
        </div>
      </div>
    </Transition>

    <div class="card bg-base-100 border-2 border-success/30 rounded-2xl shadow-sm">
      <div class="card-body p-6">
        <!-- Header -->
        <div class="flex items-center gap-3 mb-6">
          <div class="flex items-center justify-center w-10 h-10 bg-success/10 rounded-xl">
            <CheckCircleIcon class="w-5 h-5 text-success" />
          </div>
          <div>
            <h2 class="text-xl font-bold tracking-tight">Audio Generado</h2>
            <p class="text-sm text-base-content/50">Listo para reproducir o enviar</p>
          </div>
        </div>

        <!-- Audio Player -->
        <div class="mb-6">
          <div class="bg-base-200/50 border-2 border-base-300 rounded-xl p-4">
            <audio
              ref="audioPlayer"
              :src="audio.audio_url"
              controls
              class="w-full"
              @play="isPlaying = true"
              @pause="isPlaying = false"
              @ended="isPlaying = false"
            ></audio>
          </div>
        </div>

        <!-- Action button -->
        <button
          @click="sendToSpeakers"
          class="btn btn-primary w-full h-12 rounded-xl font-semibold
                 shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30
                 transition-all duration-200"
          :disabled="sendingToSpeakers"
        >
          <span
            v-if="sendingToSpeakers"
            class="loading loading-spinner loading-sm"
          ></span>
          <template v-else>
            <SpeakerWaveIcon class="w-5 h-5" />
            <span>Enviar a los Parlantes</span>
          </template>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { CheckCircleIcon, SpeakerWaveIcon } from '@heroicons/vue/24/outline'
import type { VehicleAnnouncementResponse } from '../composables/useVehicleAnnouncement'
import { libraryApi } from '@/components/library/services/libraryApi'

const props = defineProps<{
  audio: VehicleAnnouncementResponse
}>()

// State
const audioPlayer = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const sendingToSpeakers = ref(false)
const showSuccessToast = ref(false)
const errorMessage = ref('')

// Auto-play when audio changes
watch(
  () => props.audio,
  async (newAudio) => {
    if (newAudio) {
      await nextTick()

      if (audioPlayer.value) {
        setTimeout(async () => {
          try {
            await audioPlayer.value!.play()
          } catch (error) {
            console.warn('Auto-play prevented:', error)
          }
        }, 100)
      }
    }
  },
  { immediate: true }
)

// Send to Speakers (AzuraCast Radio)
async function sendToSpeakers() {
  sendingToSpeakers.value = true
  errorMessage.value = ''

  try {
    const result = await libraryApi.sendToRadio(props.audio.audio_id, true)

    if (result.success) {
      // Show success toast
      showSuccessToast.value = true
      setTimeout(() => {
        showSuccessToast.value = false
      }, 3000)
    } else {
      throw new Error(result.message || 'Error al enviar')
    }
  } catch (e: any) {
    console.error('Error sending to speakers:', e)
    errorMessage.value = e.response?.data?.detail || e.message || 'Error al enviar a los parlantes'
    setTimeout(() => {
      errorMessage.value = ''
    }, 5000)
  } finally {
    sendingToSpeakers.value = false
  }
}
</script>
