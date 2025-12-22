<script setup lang="ts">
import { computed } from 'vue'
import type { MusicTrack } from '@/types/audio'

interface Props {
  tracks: MusicTrack[]
  selectedTrackFilename?: string | null
  showToggle?: boolean
  enabled?: boolean
  disabled?: boolean
  badgeStyle?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showToggle: false,
  enabled: true,
  disabled: false,
  badgeStyle: true
})

const emit = defineEmits<{
  select: [filename: string | null]
  toggle: [enabled: boolean]
  'update:selectedTrackFilename': [filename: string | null]
  'update:enabled': [enabled: boolean]
}>()

// Active tracks only
const activeTracks = computed(() => {
  return props.tracks.filter(t => t.active)
})

// Find selected track index for highlighting
const selectedIndex = computed(() => {
  return activeTracks.value.findIndex(t => t.filename === props.selectedTrackFilename)
})

// Handle track selection
function selectTrack(index: number) {
  if (props.disabled) return
  const track = activeTracks.value[index]
  if (track) {
    emit('select', track.filename)
    emit('update:selectedTrackFilename', track.filename)
  }
}

// Handle toggle
function handleToggle(event: Event) {
  const checked = (event.target as HTMLInputElement).checked
  emit('toggle', checked)
  emit('update:enabled', checked)

  // If enabling and no track selected, select default or first
  if (checked && !props.selectedTrackFilename && activeTracks.value.length > 0) {
    const defaultTrack = activeTracks.value.find(t => t.is_default) || activeTracks.value[0]
    emit('select', defaultTrack.filename)
    emit('update:selectedTrackFilename', defaultTrack.filename)
  }

  // If disabling, clear selection
  if (!checked) {
    emit('select', null)
    emit('update:selectedTrackFilename', null)
  }
}
</script>

<template>
  <div class="music-selector-base">
    <!-- Toggle row (optional) -->
    <div v-if="showToggle" class="flex items-center gap-3 mb-2">
      <span class="text-lg">🎵</span>
      <span class="text-sm">Agregar música</span>
      <input
        type="checkbox"
        class="toggle toggle-sm toggle-primary"
        :checked="enabled"
        :disabled="disabled || activeTracks.length === 0"
        @change="handleToggle"
      />
    </div>

    <!-- Track badges -->
    <div
      v-if="enabled || !showToggle"
      class="flex flex-wrap items-center gap-2"
      :class="{ 'pl-7': showToggle }"
    >
      <button
        v-for="(track, index) in activeTracks"
        :key="track.id"
        type="button"
        @click="selectTrack(index)"
        class="transition-all"
        :class="[
          badgeStyle
            ? 'badge badge-lg gap-1 cursor-pointer'
            : 'btn btn-sm',
          {
            'badge-secondary': badgeStyle && selectedIndex === index,
            'badge-outline opacity-60 hover:opacity-100': badgeStyle && selectedIndex !== index,
            'btn-secondary': !badgeStyle && selectedIndex === index,
            'btn-outline': !badgeStyle && selectedIndex !== index,
            'pointer-events-none opacity-40': disabled
          }
        ]"
        :disabled="disabled"
        :title="track.display_name"
      >
        <span v-if="track.is_default">⭐</span>
        <span>{{ track.display_name }}</span>
      </button>

      <!-- Empty state -->
      <span v-if="activeTracks.length === 0" class="text-sm opacity-50">
        No hay pistas de música disponibles
      </span>
    </div>
  </div>
</template>
