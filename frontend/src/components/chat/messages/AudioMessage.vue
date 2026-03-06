<script setup lang="ts">
import { ref } from 'vue'
import { Play, Pause } from 'lucide-vue-next'

defineProps<{
  audioUrl: string
  duration?: number
  audioId?: number
}>()

const audioRef = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const progress = ref(0)

function togglePlay() {
  if (!audioRef.value) return
  if (isPlaying.value) audioRef.value.pause()
  else audioRef.value.play()
  isPlaying.value = !isPlaying.value
}

function onTimeUpdate() {
  if (audioRef.value && audioRef.value.duration)
    progress.value = (audioRef.value.currentTime / audioRef.value.duration) * 100
}

function onEnded() {
  isPlaying.value = false
  progress.value = 0
}

function formatDuration(s?: number): string {
  if (!s) return '0:00'
  return `${Math.floor(s / 60)}:${Math.floor(s % 60).toString().padStart(2, '0')}`
}
</script>

<template>
  <div class="flex justify-start">
    <div class="bg-base-200 rounded-2xl px-4 py-3 max-w-[85%] flex items-center gap-3">
      <button @click="togglePlay" class="btn btn-circle btn-sm btn-primary">
        <Pause v-if="isPlaying" class="w-4 h-4" />
        <Play v-else class="w-4 h-4" />
      </button>
      <div class="flex-1 min-w-[120px]">
        <div class="w-full bg-base-300 rounded-full h-1.5">
          <div class="bg-primary h-1.5 rounded-full transition-all duration-100"
               :style="{ width: `${progress}%` }" />
        </div>
        <p class="text-[10px] text-base-content/40 mt-1">{{ formatDuration(duration) }}</p>
      </div>
      <audio ref="audioRef" :src="audioUrl" @timeupdate="onTimeUpdate"
             @ended="onEnded" preload="metadata" />
    </div>
  </div>
</template>
