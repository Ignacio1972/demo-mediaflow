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

      <!-- Action Buttons -->
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
import type { AutomaticGenerateResponse } from '../composables/useAutomaticMode'

const props = defineProps<{
  audioData: AutomaticGenerateResponse
}>()

defineEmits<{
  (e: 'regenerate'): void
}>()

const audioRef = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)

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
</script>
