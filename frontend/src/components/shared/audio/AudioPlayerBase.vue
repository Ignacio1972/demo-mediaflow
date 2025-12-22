<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'

interface Props {
  audioUrl: string
  duration?: number
  title?: string
  subtitle?: string
  showWaveform?: boolean
  autoplay?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showWaveform: false,
  autoplay: false
})

const emit = defineEmits<{
  play: []
  pause: []
  ended: []
  timeupdate: [currentTime: number]
}>()

// Refs
const audioElement = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const audioDuration = ref(props.duration || 0)

// Format time as mm:ss
function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Progress percentage
function getProgress(): number {
  if (!audioDuration.value) return 0
  return (currentTime.value / audioDuration.value) * 100
}

// Toggle play/pause
function togglePlay() {
  if (!audioElement.value) return

  if (isPlaying.value) {
    audioElement.value.pause()
  } else {
    audioElement.value.play()
  }
}

// Event handlers
function onPlay() {
  isPlaying.value = true
  emit('play')
}

function onPause() {
  isPlaying.value = false
  emit('pause')
}

function onEnded() {
  isPlaying.value = false
  currentTime.value = 0
  emit('ended')
}

function onTimeUpdate() {
  if (audioElement.value) {
    currentTime.value = audioElement.value.currentTime
    emit('timeupdate', currentTime.value)
  }
}

function onLoadedMetadata() {
  if (audioElement.value) {
    audioDuration.value = audioElement.value.duration
  }
}

// Seek to position
function seek(event: MouseEvent) {
  if (!audioElement.value || !audioDuration.value) return

  const target = event.currentTarget as HTMLElement
  const rect = target.getBoundingClientRect()
  const clickX = event.clientX - rect.left
  const percentage = clickX / rect.width

  audioElement.value.currentTime = percentage * audioDuration.value
}

// Watch for URL changes
watch(() => props.audioUrl, () => {
  isPlaying.value = false
  currentTime.value = 0

  // Autoplay if enabled
  if (props.autoplay && audioElement.value) {
    setTimeout(() => {
      audioElement.value?.play().catch(() => {
        // Autoplay blocked by browser
      })
    }, 100)
  }
})

// Cleanup
onUnmounted(() => {
  if (audioElement.value) {
    audioElement.value.pause()
  }
})
</script>

<template>
  <div class="audio-player-base">
    <!-- Hidden audio element -->
    <audio
      ref="audioElement"
      :src="audioUrl"
      @play="onPlay"
      @pause="onPause"
      @ended="onEnded"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoadedMetadata"
    />

    <!-- Player UI -->
    <div class="bg-base-300 rounded-lg p-4">
      <!-- Title & Subtitle -->
      <div v-if="title || subtitle" class="mb-3">
        <p v-if="title" class="font-medium truncate">{{ title }}</p>
        <p v-if="subtitle" class="text-sm opacity-70">{{ subtitle }}</p>
      </div>

      <!-- Controls row -->
      <div class="flex items-center gap-3">
        <!-- Play/Pause button -->
        <button
          type="button"
          class="btn btn-circle btn-sm btn-primary"
          @click="togglePlay"
        >
          {{ isPlaying ? '⏸' : '▶' }}
        </button>

        <!-- Progress bar -->
        <div
          class="flex-1 h-2 bg-base-100 rounded-full cursor-pointer relative overflow-hidden"
          @click="seek"
        >
          <div
            class="h-full bg-primary transition-all duration-100"
            :style="{ width: `${getProgress()}%` }"
          />
        </div>

        <!-- Time display -->
        <div class="text-sm opacity-70 font-mono min-w-[80px] text-right">
          {{ formatTime(currentTime) }} / {{ formatTime(audioDuration) }}
        </div>
      </div>

      <!-- Actions slot -->
      <div v-if="$slots.actions" class="mt-3 pt-3 border-t border-base-200">
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>
