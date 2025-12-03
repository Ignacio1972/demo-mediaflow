<template>
  <div class="form-control">
    <label class="label">
      <span class="label-text font-medium">Música de Fondo</span>
    </label>
    <select
      class="select select-bordered w-full"
      :value="selectedMusicFile || ''"
      @change="handleChange"
    >
      <option value="">Sin música</option>
      <option
        v-for="track in sortedTracks"
        :key="track.id"
        :value="track.filename"
      >
        {{ track.display_name }}
        {{ track.is_default ? '(Default)' : '' }}
        {{ track.duration ? `(${formatDuration(track.duration)})` : '' }}
      </option>
    </select>
    <label class="label">
      <span class="label-text-alt text-base-content/50">
        {{ selectedMusic ? selectedMusic.filename : 'El jingle se generará solo con voz' }}
      </span>
    </label>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { MusicTrack } from '@/types/audio'

const props = defineProps<{
  musicTracks: MusicTrack[]
  selectedMusicFile: string | null
}>()

const emit = defineEmits<{
  (e: 'update:selected-music-file', value: string | null): void
}>()

const sortedTracks = computed(() =>
  [...props.musicTracks].sort((a, b) => {
    // Default track first, then by order
    if (a.is_default && !b.is_default) return -1
    if (!a.is_default && b.is_default) return 1
    return a.order - b.order
  })
)

const selectedMusic = computed(() =>
  props.musicTracks.find(t => t.filename === props.selectedMusicFile)
)

const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  emit('update:selected-music-file', target.value || null)
}
</script>
