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

        <!-- Success/Error Messages -->
        <div v-if="showSuccess" class="alert alert-success mb-4">
          <span>{{ successMessage }}</span>
        </div>
        <div v-if="errorMessage" class="alert alert-error mb-4">
          <span>{{ errorMessage }}</span>
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

          <!-- Save to Library -->
          <button
            @click="saveToLibrary"
            class="btn btn-secondary w-full h-10 rounded-xl"
            :disabled="savingToLibrary || savedToLibrary"
          >
            <span
              v-if="savingToLibrary"
              class="loading loading-spinner loading-sm"
            ></span>
            <template v-else-if="savedToLibrary">
              <CheckCircleIcon class="w-4 h-4" />
              <span>Guardado en Biblioteca</span>
            </template>
            <template v-else>
              <BookmarkIcon class="w-4 h-4" />
              <span>Guardar en Biblioteca</span>
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
import { CheckCircleIcon, SpeakerWaveIcon, ArrowPathIcon, BookmarkIcon } from '@heroicons/vue/24/outline'
import type { GenerateResponse } from '../composables/useScheduleAnnouncement'
import { libraryApi } from '@/components/library/services/libraryApi'

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
const savingToLibrary = ref(false)
const savedToLibrary = ref(false)
const showSuccess = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

// Auto-play when audio changes and reset saved state
watch(
  () => props.audio,
  async (newAudio) => {
    if (newAudio) {
      // Reset saved state for new audio
      savedToLibrary.value = false

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
      successMessage.value = 'Audio enviado a los parlantes'
      showSuccess.value = true
      setTimeout(() => {
        showSuccess.value = false
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

// Save to Library
async function saveToLibrary() {
  savingToLibrary.value = true
  errorMessage.value = ''

  try {
    await libraryApi.updateMessage(props.audio.audio_id, { is_favorite: true })
    savedToLibrary.value = true
    successMessage.value = 'Guardado en biblioteca'
    showSuccess.value = true
    setTimeout(() => {
      showSuccess.value = false
    }, 3000)
  } catch (e: any) {
    console.error('Error saving to library:', e)
    errorMessage.value = e.response?.data?.detail || e.message || 'Error al guardar en biblioteca'
    setTimeout(() => {
      errorMessage.value = ''
    }, 5000)
  } finally {
    savingToLibrary.value = false
  }
}
</script>
