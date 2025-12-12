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

        <!-- Audio info -->
        <div class="flex flex-wrap gap-2 mb-4">
          <span class="badge badge-primary">{{ audio.voice_name }}</span>
          <span class="badge badge-ghost">
            {{ formatDuration(audio.duration) }}
          </span>
          <span class="badge badge-ghost">{{ audio.template_used }}</span>
        </div>

        <!-- Action buttons -->
        <div class="flex flex-wrap gap-3 justify-end">
          <!-- Save to Library -->
          <button
            @click="saveToLibrary"
            class="btn btn-success"
            :class="{ 'btn-disabled': isSaved }"
            :disabled="savingToLibrary || isSaved"
          >
            <span
              v-if="savingToLibrary"
              class="loading loading-spinner loading-xs"
            ></span>
            <span v-else-if="isSaved">Guardado</span>
            <span v-else>Guardar en Biblioteca</span>
          </button>

          <!-- Send to Local Player -->
          <button
            @click="sendToLocalPlayer"
            class="btn btn-outline"
            :disabled="sendingToLocal"
          >
            <span
              v-if="sendingToLocal"
              class="loading loading-spinner loading-xs"
            ></span>
            <span v-else>Enviar a Maquina Local</span>
          </button>

          <!-- Send to AzuraCast -->
          <button
            @click="sendToAzuracast"
            class="btn btn-outline"
            :disabled="sendingToAzuracast"
          >
            <span
              v-if="sendingToAzuracast"
              class="loading loading-spinner loading-xs"
            ></span>
            <span v-else>Enviar a AzuraCast</span>
          </button>

          <!-- New announcement -->
          <button @click="$emit('reset')" class="btn btn-ghost">
            Nuevo Anuncio
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useAudioStore } from '@/stores/audio'
import type { VehicleAnnouncementResponse } from '../composables/useVehicleAnnouncement'

const props = defineProps<{
  audio: VehicleAnnouncementResponse
}>()

const emit = defineEmits<{
  (e: 'reset'): void
}>()

const audioStore = useAudioStore()

// State
const audioPlayer = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const savingToLibrary = ref(false)
const sendingToLocal = ref(false)
const sendingToAzuracast = ref(false)
const isSaved = ref(false)

// Auto-play when audio changes
watch(
  () => props.audio,
  async (newAudio) => {
    if (newAudio) {
      isSaved.value = false
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

// Format duration
function formatDuration(seconds?: number): string {
  if (!seconds) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Save to Library
async function saveToLibrary() {
  savingToLibrary.value = true

  try {
    await audioStore.saveToLibrary(props.audio.audio_id)
    isSaved.value = true
  } catch (e) {
    console.error('Error saving to library:', e)
    alert('Error al guardar en biblioteca')
  } finally {
    savingToLibrary.value = false
  }
}

// Send to Local Player
async function sendToLocalPlayer() {
  sendingToLocal.value = true

  try {
    // TODO: Implement local player API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    alert('Audio enviado a Maquina Local')
  } catch (e) {
    console.error('Error sending to local:', e)
    alert('Error al enviar a Maquina Local')
  } finally {
    sendingToLocal.value = false
  }
}

// Send to AzuraCast
async function sendToAzuracast() {
  sendingToAzuracast.value = true

  try {
    // TODO: Implement AzuraCast API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    alert('Audio enviado a AzuraCast')
  } catch (e) {
    console.error('Error sending to AzuraCast:', e)
    alert('Error al enviar a AzuraCast')
  } finally {
    sendingToAzuracast.value = false
  }
}
</script>
