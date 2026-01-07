<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { PlayIcon, PauseIcon } from '@heroicons/vue/24/outline'
import type { CampaignAudio } from '@/types/campaign'

interface Props {
  audio: CampaignAudio
}

const props = defineProps<Props>()

const emit = defineEmits<{
  play: [audio: CampaignAudio]
  delete: [audio: CampaignAudio]
  schedule: [audio: CampaignAudio]
  broadcast: [audio: CampaignAudio]
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
          class="btn btn-circle btn-sm btn-primary"
          :title="isPlaying ? 'Pausar' : 'Reproducir'"
          @click="togglePlay"
        >
          <PauseIcon v-if="isPlaying" class="h-4 w-4" />
          <PlayIcon v-else class="h-4 w-4" />
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

      <!-- Actions -->
      <div class="card-actions justify-end mt-3 gap-1">
        <button
          class="btn btn-ghost btn-xs"
          title="Programar"
          @click="emit('schedule', audio)"
        >
          📅
        </button>
        <button
          class="btn btn-ghost btn-xs"
          title="Enviar a radio"
          @click="emit('broadcast', audio)"
        >
          📻
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
