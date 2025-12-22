<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import type { CampaignAudio } from '@/types/campaign'

interface Props {
  audio: CampaignAudio
}

const props = defineProps<Props>()

const emit = defineEmits<{
  play: [audio: CampaignAudio]
  delete: [audio: CampaignAudio]
}>()

// Playback state
const isPlaying = ref(false)
const audioElement = ref<HTMLAudioElement | null>(null)

function togglePlay() {
  if (isPlaying.value) {
    audioElement.value?.pause()
    isPlaying.value = false
  } else {
    if (!audioElement.value) {
      audioElement.value = new Audio(props.audio.audio_url)
      audioElement.value.onended = () => {
        isPlaying.value = false
      }
    }
    audioElement.value.play()
    isPlaying.value = true
    emit('play', props.audio)
  }
}

function handleDelete() {
  emit('delete', props.audio)
}

// Format duration
function formatDuration(seconds: number | null): string {
  if (!seconds) return '--'
  const mins = Math.floor(seconds / 60)
  const secs = Math.round(seconds % 60)
  return mins > 0 ? `${mins}:${secs.toString().padStart(2, '0')}` : `${secs}s`
}

// Cleanup on unmount
onUnmounted(() => {
  if (audioElement.value) {
    audioElement.value.pause()
    audioElement.value = null
  }
})
</script>

<template>
  <div class="card bg-base-200 hover:shadow-md transition-shadow">
    <div class="card-body p-4">
      <!-- Play button + Title -->
      <div class="flex items-start gap-3">
        <button
          class="btn btn-circle btn-sm"
          :class="isPlaying ? 'btn-primary' : 'btn-ghost'"
          @click="togglePlay"
        >
          {{ isPlaying ? '⏸️' : '▶️' }}
        </button>

        <div class="flex-1 min-w-0">
          <h3 class="font-medium truncate">
            {{ audio.display_name }}
          </h3>
          <p class="text-sm opacity-70 line-clamp-2">
            "{{ audio.original_text?.slice(0, 60) }}{{ audio.original_text?.length > 60 ? '...' : '' }}"
          </p>
        </div>
      </div>

      <!-- Meta info -->
      <div class="flex items-center gap-2 mt-2 text-sm opacity-70">
        <span>🎤 {{ audio.voice_id }}</span>
        <span>·</span>
        <span>{{ formatDuration(audio.duration) }}</span>
        <span v-if="audio.has_jingle">· 🎵</span>
      </div>

      <!-- Actions -->
      <div class="card-actions justify-end mt-3 gap-1">
        <button
          class="btn btn-ghost btn-xs"
          title="Programar"
          disabled
        >
          📅
        </button>
        <button
          class="btn btn-ghost btn-xs"
          title="Enviar a parlantes"
          disabled
        >
          📤
        </button>
        <button
          class="btn btn-ghost btn-xs text-error"
          title="Eliminar"
          @click="handleDelete"
        >
          🗑️
        </button>
      </div>
    </div>
  </div>
</template>
