<template>
  <div class="recording-view h-full flex flex-col items-center justify-center p-6 bg-base-100">
    <!-- REC Indicator -->
    <div class="flex items-center gap-3 mb-8">
      <div class="rec-dot w-4 h-4 rounded-full bg-error animate-pulse"></div>
      <span class="text-error font-bold text-xl">REC</span>
      <span class="text-base-content text-2xl font-mono ml-2">
        {{ formattedDuration }}
      </span>
    </div>

    <!-- Listening indicator -->
    <div class="mb-8">
      <div class="flex items-center gap-2 text-base-content/60">
        <span class="loading loading-dots loading-md"></span>
        <span>Escuchando...</span>
      </div>
    </div>

    <!-- Stop Button -->
    <button
      @click="$emit('stop')"
      class="btn btn-circle btn-lg btn-error w-24 h-24 shadow-lg"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="currentColor" viewBox="0 0 24 24">
        <rect x="6" y="6" width="12" height="12" rx="1" />
      </svg>
    </button>
    <p class="text-base-content/60 mt-4 text-sm">
      Toca para detener
    </p>

    <!-- Cancel link -->
    <button
      @click="$emit('cancel')"
      class="btn btn-ghost btn-sm mt-8 text-base-content/50"
    >
      Cancelar
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Props
interface Props {
  duration: number
}

const props = defineProps<Props>()

// Emits
defineEmits<{
  (e: 'stop'): void
  (e: 'cancel'): void
}>()

// Formatted duration MM:SS
const formattedDuration = computed(() => {
  const minutes = Math.floor(props.duration / 60)
  const seconds = props.duration % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})
</script>

<style scoped>
.recording-view {
  background: radial-gradient(circle at center, oklch(var(--er) / 0.05) 0%, transparent 70%);
}

.rec-dot {
  animation: blink 1s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}
</style>
