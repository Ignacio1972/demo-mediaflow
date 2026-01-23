<template>
  <div class="audio-result">
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

        <!-- Actions -->
        <div class="space-y-3">
          <!-- Send to Speakers -->
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

          <!-- Generate Another -->
          <button
            @click="$emit('reset')"
            class="btn btn-ghost w-full h-10 rounded-xl"
          >
            <ArrowPathIcon class="w-4 h-4" />
            <span>Generar otro anuncio</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { CheckCircleIcon, SpeakerWaveIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'
import type { GenerateResponse } from '../composables/useScheduleAnnouncement'

const props = defineProps<{
  audio: GenerateResponse
}>()

defineEmits<{
  reset: []
}>()

// State
const audioPlayer = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const sendingToSpeakers = ref(false)

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

// Send to Speakers (Local Player)
async function sendToSpeakers() {
  sendingToSpeakers.value = true

  try {
    // TODO: Implement local player API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    alert('Audio enviado a los parlantes')
  } catch (e) {
    console.error('Error sending to speakers:', e)
    alert('Error al enviar a los parlantes')
  } finally {
    sendingToSpeakers.value = false
  }
}
</script>
