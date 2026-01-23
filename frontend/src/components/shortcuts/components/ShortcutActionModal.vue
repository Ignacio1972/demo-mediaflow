<template>
  <dialog class="modal modal-open">
    <div class="modal-box max-w-sm">
      <!-- Header -->
      <div class="flex items-center gap-3 mb-6">
        <div
          class="w-14 h-14 rounded-xl flex items-center justify-center text-3xl"
          :style="iconStyle"
        >
          {{ shortcut.custom_icon || '⚡' }}
        </div>
        <div>
          <h3 class="font-bold text-lg">{{ shortcut.custom_name }}</h3>
          <p v-if="shortcut.duration" class="text-sm text-base-content/50">
            {{ formatDuration(shortcut.duration) }}
          </p>
        </div>
      </div>

      <!-- Audio Player -->
      <div class="bg-base-200 rounded-xl p-4 mb-6">
        <audio
          ref="audioRef"
          :src="shortcut.audio_url"
          @timeupdate="updateProgress"
          @ended="handleEnded"
          @loadedmetadata="handleLoaded"
        />

        <!-- Progress Bar -->
        <div class="flex items-center gap-3 mb-3">
          <button
            class="btn btn-circle btn-sm"
            @click="togglePlay"
          >
            <PlayIcon v-if="!isPlaying" class="w-4 h-4" />
            <PauseIcon v-else class="w-4 h-4" />
          </button>

          <div class="flex-1">
            <input
              type="range"
              :value="progress"
              @input="seek"
              min="0"
              max="100"
              class="range range-primary range-xs"
            />
          </div>

          <span class="text-xs text-base-content/50 w-12 text-right">
            {{ formatTime(currentTime) }}
          </span>
        </div>

        <!-- Volume (optional) -->
        <div class="flex items-center gap-2">
          <SpeakerWaveIcon class="w-4 h-4 text-base-content/50" />
          <input
            type="range"
            v-model="volume"
            @input="updateVolume"
            min="0"
            max="100"
            class="range range-xs flex-1"
          />
        </div>
      </div>

      <!-- Actions -->
      <div class="space-y-3">
        <!-- Preview Button -->
        <button
          class="btn btn-outline btn-block gap-2"
          @click="togglePlay"
        >
          <PlayIcon v-if="!isPlaying" class="w-5 h-5" />
          <PauseIcon v-else class="w-5 h-5" />
          {{ isPlaying ? 'Pausar' : 'Reproducir' }}
        </button>

        <!-- Broadcast Button -->
        <button
          class="btn btn-primary btn-block gap-2"
          :disabled="isBroadcasting"
          @click="handleBroadcast"
        >
          <span v-if="isBroadcasting" class="loading loading-spinner loading-sm"></span>
          <SignalIcon v-else class="w-5 h-5" />
          Enviar a Parlantes
        </button>

        <!-- Cancel -->
        <button
          class="btn btn-ghost btn-block"
          @click="handleClose"
        >
          Cancelar
        </button>
      </div>
    </div>

    <form method="dialog" class="modal-backdrop">
      <button @click="handleClose">close</button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import {
  PlayIcon,
  PauseIcon,
  SpeakerWaveIcon,
  SignalIcon,
} from '@heroicons/vue/24/solid'
import type { ShortcutPublic } from '@/types/shortcut'

const props = defineProps<{
  shortcut: ShortcutPublic
}>()

const emit = defineEmits<{
  close: []
  broadcast: []
}>()

// Audio state
const audioRef = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(80)
const isBroadcasting = ref(false)

// Computed
const progress = computed(() => {
  if (duration.value === 0) return 0
  return (currentTime.value / duration.value) * 100
})

const iconStyle = computed(() => {
  const color = props.shortcut.custom_color || '#10B981'
  return {
    backgroundColor: `${color}20`,
  }
})

// Format helpers
const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Audio controls
const togglePlay = () => {
  if (!audioRef.value) return

  if (isPlaying.value) {
    audioRef.value.pause()
    isPlaying.value = false
  } else {
    audioRef.value.play()
    isPlaying.value = true
  }
}

const updateProgress = () => {
  if (audioRef.value) {
    currentTime.value = audioRef.value.currentTime
  }
}

const handleLoaded = () => {
  if (audioRef.value) {
    duration.value = audioRef.value.duration
    audioRef.value.volume = volume.value / 100
  }
}

const handleEnded = () => {
  isPlaying.value = false
  currentTime.value = 0
}

const seek = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (audioRef.value && duration.value > 0) {
    const newTime = (parseFloat(target.value) / 100) * duration.value
    audioRef.value.currentTime = newTime
    currentTime.value = newTime
  }
}

const updateVolume = () => {
  if (audioRef.value) {
    audioRef.value.volume = volume.value / 100
  }
}

// Broadcast handler
const handleBroadcast = async () => {
  isBroadcasting.value = true
  try {
    emit('broadcast')
  } finally {
    isBroadcasting.value = false
  }
}

// Close handler
const handleClose = () => {
  if (audioRef.value) {
    audioRef.value.pause()
  }
  emit('close')
}

// Cleanup on unmount
onUnmounted(() => {
  if (audioRef.value) {
    audioRef.value.pause()
  }
})
</script>
