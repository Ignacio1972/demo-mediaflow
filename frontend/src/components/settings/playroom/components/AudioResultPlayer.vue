<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title text-lg mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Audio Generado
      </h2>

      <!-- Audio Info -->
      <div class="bg-base-200 rounded-lg p-4 mb-4">
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-base-content/60">Voz:</span>
            <span class="ml-2 font-medium">{{ audioData.voice_used }}</span>
          </div>
          <div>
            <span class="text-base-content/60">Duración:</span>
            <span class="ml-2 font-medium">{{ formatDuration(audioData.duration) }}</span>
          </div>
        </div>
      </div>

      <!-- Text Comparison -->
      <div class="grid md:grid-cols-2 gap-4 mb-4" v-if="audioData.original_text !== audioData.improved_text">
        <div>
          <label class="label">
            <span class="label-text text-xs font-medium text-base-content/60">Texto Original</span>
          </label>
          <div class="bg-base-200 rounded-lg p-3 text-sm">
            {{ audioData.original_text }}
          </div>
        </div>
        <div>
          <label class="label">
            <span class="label-text text-xs font-medium text-primary">Texto Mejorado (IA)</span>
          </label>
          <div class="bg-primary/10 border border-primary/30 rounded-lg p-3 text-sm">
            {{ audioData.improved_text }}
          </div>
        </div>
      </div>

      <!-- Single text if no improvement -->
      <div v-else class="mb-4">
        <label class="label">
          <span class="label-text text-xs font-medium text-base-content/60">Texto</span>
        </label>
        <div class="bg-base-200 rounded-lg p-3 text-sm">
          {{ audioData.improved_text }}
        </div>
      </div>

      <!-- Audio Player -->
      <div class="mb-4">
        <audio
          ref="audioRef"
          :src="fullAudioUrl"
          controls
          class="w-full"
          @play="isPlaying = true"
          @pause="isPlaying = false"
          @ended="isPlaying = false"
        ></audio>
      </div>

      <!-- Action Buttons - Row 1: Library Actions -->
      <div class="flex flex-wrap gap-2 justify-end mb-2">
        <!-- Guardar en Biblioteca -->
        <button
          @click="saveToLibrary"
          class="btn btn-success btn-sm gap-2"
          :class="{ 'btn-disabled': isSaved }"
          :disabled="savingToLibrary || isSaved || !audioData.audio_id"
        >
          <span v-if="savingToLibrary" class="loading loading-spinner loading-xs"></span>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
          </svg>
          <span v-if="isSaved">Guardado</span>
          <span v-else>Guardar en Biblioteca</span>
        </button>

        <!-- Enviar a Máquina Local -->
        <button
          @click="sendToLocalPlayer"
          class="btn btn-outline btn-sm gap-2"
          :disabled="sendingToLocal"
        >
          <span v-if="sendingToLocal" class="loading loading-spinner loading-xs"></span>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          Enviar a Maquina Local
        </button>

        <!-- Enviar a AzuraCast -->
        <button
          @click="sendToAzuracast"
          class="btn btn-outline btn-sm gap-2"
          :disabled="sendingToAzuracast"
        >
          <span v-if="sendingToAzuracast" class="loading loading-spinner loading-xs"></span>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.636 18.364a9 9 0 010-12.728m12.728 0a9 9 0 010 12.728m-9.9-2.829a5 5 0 010-7.07m7.072 0a5 5 0 010 7.07M13 12a1 1 0 11-2 0 1 1 0 012 0z" />
          </svg>
          Enviar a AzuraCast
        </button>
      </div>

      <!-- Action Buttons - Row 2: Download & Regenerate -->
      <div class="flex flex-wrap gap-2 justify-end">
        <button
          @click="downloadAudio"
          class="btn btn-outline btn-sm gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Descargar
        </button>
        <button
          @click="$emit('regenerate')"
          class="btn btn-primary btn-sm gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Regenerar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useAudioStore } from '@/stores/audio'
import type { AutomaticGenerateResponse } from '../composables/useAutomaticMode'

const props = defineProps<{
  audioData: AutomaticGenerateResponse
}>()

defineEmits<{
  (e: 'regenerate'): void
}>()

// Store
const audioStore = useAudioStore()

const audioRef = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)

// Action states
const savingToLibrary = ref(false)
const sendingToLocal = ref(false)
const sendingToAzuracast = ref(false)
const isSaved = ref(false)

// Reset isSaved when audio changes
watch(() => props.audioData?.audio_id, () => {
  isSaved.value = false
})

// Auto-play when new audio is generated
watch(() => props.audioData, async (newAudio, oldAudio) => {
  if (newAudio && (!oldAudio || newAudio.filename !== oldAudio.filename)) {
    console.log('🎵 New audio detected, preparing auto-play:', newAudio.filename)

    await nextTick()

    if (audioRef.value) {
      setTimeout(async () => {
        try {
          await audioRef.value!.play()
          console.log('🔊 Auto-playing generated audio')
        } catch (error) {
          console.warn('⚠️ Auto-play prevented by browser:', error)
        }
      }, 100)
    }
  }
}, { deep: true, immediate: true })

// Build full URL for audio
const fullAudioUrl = computed(() => {
  // If already a full URL, use as-is
  if (props.audioData.audio_url.startsWith('http')) {
    return props.audioData.audio_url
  }
  // Build URL from API base
  const baseUrl = import.meta.env.VITE_API_URL || ''
  return `${baseUrl}${props.audioData.audio_url}`
})

const formatDuration = (seconds: number | null): string => {
  if (!seconds) return '--:--'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const downloadAudio = () => {
  const link = document.createElement('a')
  link.href = fullAudioUrl.value
  link.download = props.audioData.filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Save to Library
const saveToLibrary = async () => {
  if (!props.audioData?.audio_id) return

  savingToLibrary.value = true

  try {
    await audioStore.saveToLibrary(props.audioData.audio_id)
    isSaved.value = true
    console.log('💾 Guardado en biblioteca:', props.audioData.filename)
  } catch (e) {
    console.error('Error al guardar en biblioteca:', e)
    alert('Error al guardar en biblioteca')
  } finally {
    savingToLibrary.value = false
  }
}

// Send to Local Player
const sendToLocalPlayer = async () => {
  if (!props.audioData) return

  sendingToLocal.value = true

  try {
    // TODO: Implement local player API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    console.log('📺 Enviado a maquina local:', props.audioData.filename)
    alert('Audio enviado a Maquina Local')
  } catch (e) {
    console.error('Error al enviar a maquina local:', e)
    alert('Error al enviar a Maquina Local')
  } finally {
    sendingToLocal.value = false
  }
}

// Send to AzuraCast
const sendToAzuracast = async () => {
  if (!props.audioData) return

  sendingToAzuracast.value = true

  try {
    // TODO: Implement AzuraCast API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    console.log('📡 Enviado a AzuraCast:', props.audioData.filename)
    alert('Audio enviado a AzuraCast')
  } catch (e) {
    console.error('Error al enviar a AzuraCast:', e)
    alert('Error al enviar a AzuraCast')
  } finally {
    sendingToAzuracast.value = false
  }
}
</script>
