<template>
  <div class="music-list card bg-base-100 shadow-xl">
    <div class="card-body p-4">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold text-lg">Tracks Disponibles</h3>
        <span class="badge badge-primary">{{ tracks.length }}</span>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex justify-center py-8">
        <span class="loading loading-spinner loading-lg text-primary"></span>
      </div>

      <!-- Empty State -->
      <div v-else-if="tracks.length === 0" class="text-center py-8 text-base-content/50">
        <div class="text-4xl mb-2">🎵</div>
        <p>No hay música disponible</p>
        <p class="text-sm">Sube tu primera canción</p>
      </div>

      <!-- Track List -->
      <div v-else class="space-y-2 max-h-[500px] overflow-y-auto pr-1">
        <div
          v-for="track in tracks"
          :key="track.id"
          @click="$emit('select', track)"
          class="flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all border-2"
          :class="[
            selectedTrack?.id === track.id
              ? 'bg-primary/10 border-primary'
              : 'bg-base-200 border-transparent hover:bg-base-300'
          ]"
        >
          <!-- Play/Pause Button -->
          <button
            @click.stop="togglePlay(track)"
            class="btn btn-circle btn-sm btn-ghost"
            :class="{ 'btn-primary': currentlyPlaying === track.id }"
          >
            <svg v-if="currentlyPlaying === track.id" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>

          <!-- Track Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-medium truncate">{{ track.display_name }}</span>
              <span v-if="track.is_default" class="badge badge-warning badge-xs">Default</span>
              <span v-if="!track.active" class="badge badge-ghost badge-xs">Inactivo</span>
            </div>
            <div class="text-xs text-base-content/50 flex items-center gap-2">
              <span>{{ formatDuration(track.duration) }}</span>
              <span>•</span>
              <span>{{ track.bitrate || '--' }}</span>
              <span v-if="track.mood">•</span>
              <span v-if="track.mood" class="capitalize">{{ track.mood }}</span>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-1">
            <button
              v-if="!track.is_default"
              @click.stop="$emit('set-default', track.id)"
              class="btn btn-ghost btn-xs"
              title="Establecer como default"
            >
              ⭐
            </button>
          </div>
        </div>
      </div>

      <!-- Hidden Audio Player -->
      <audio ref="audioPlayer" @ended="currentlyPlaying = null"></audio>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { MusicTrack } from '@/types/audio'

defineProps<{
  tracks: MusicTrack[]
  selectedTrack: MusicTrack | null
  isLoading: boolean
}>()

defineEmits<{
  select: [track: MusicTrack]
  'set-default': [trackId: number]
}>()

// Audio player state
const audioPlayer = ref<HTMLAudioElement | null>(null)
const currentlyPlaying = ref<number | null>(null)

const togglePlay = (track: MusicTrack) => {
  if (!audioPlayer.value) return

  if (currentlyPlaying.value === track.id) {
    // Pause current
    audioPlayer.value.pause()
    currentlyPlaying.value = null
  } else {
    // Play new track
    audioPlayer.value.src = track.audio_url
    audioPlayer.value.play()
    currentlyPlaying.value = track.id
  }
}

const formatDuration = (seconds?: number): string => {
  if (!seconds) return '--:--'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>
