<template>
  <div class="audio-result">
    <div class="card bg-base-200 shadow-lg">
      <div class="card-body">
        <h2 class="card-title text-lg mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6 text-success"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          Audio Generado
        </h2>

        <!-- Audio Player -->
        <div class="mb-4">
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

        <!-- Action button -->
        <div class="card-actions justify-end">
          <button
            @click="sendToSpeakers"
            class="btn btn-primary"
            :disabled="sendingToSpeakers"
          >
            <span
              v-if="sendingToSpeakers"
              class="loading loading-spinner loading-sm"
            ></span>
            <span v-else>Enviar a los Parlantes</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { VehicleAnnouncementResponse } from '../composables/useVehicleAnnouncement'

const props = defineProps<{
  audio: VehicleAnnouncementResponse
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
