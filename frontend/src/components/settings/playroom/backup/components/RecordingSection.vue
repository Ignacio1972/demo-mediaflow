<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title text-lg mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
        Grabación de Voz
      </h2>

      <!-- Status Message -->
      <div v-if="statusMessage" class="mb-4">
        <div
          class="flex items-center gap-2 text-sm"
          :class="{
            'text-success': isListening,
            'text-warning': isRecording && !isListening,
            'text-base-content/60': !isRecording
          }"
        >
          <span v-if="isListening" class="relative flex h-3 w-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-success"></span>
          </span>
          <span v-else-if="isProcessing" class="loading loading-spinner loading-xs"></span>
          {{ statusMessage }}
        </div>
      </div>

      <!-- Recording Button -->
      <div class="flex justify-center mb-4">
        <button
          v-if="!isRecording"
          @click="$emit('start')"
          class="btn btn-circle btn-lg btn-primary"
          :disabled="isProcessing"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        </button>
        <button
          v-else
          @click="$emit('stop')"
          class="btn btn-circle btn-lg btn-error animate-pulse"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
          </svg>
        </button>
      </div>

      <p class="text-center text-sm text-base-content/60 mb-4">
        {{ isRecording ? 'Presiona para detener' : 'Presiona para comenzar a grabar' }}
      </p>

      <!-- Transcript Area -->
      <div class="form-control">
        <label class="label">
          <span class="label-text font-medium">Texto Transcrito</span>
          <span class="label-text-alt">
            {{ wordCount }} palabras
          </span>
        </label>
        <div class="relative">
          <textarea
            :value="displayTranscript"
            @input="updateTranscript"
            class="textarea textarea-bordered w-full h-32 resize-none"
            :class="{ 'textarea-primary': isRecording }"
            placeholder="El texto transcrito aparecerá aquí... También puedes escribir directamente."
            :disabled="isProcessing"
          ></textarea>

          <!-- Clear button -->
          <button
            v-if="transcript"
            @click="$emit('clear')"
            class="btn btn-ghost btn-sm btn-circle absolute top-2 right-2"
            :disabled="isProcessing"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Interim transcript indicator -->
        <div v-if="interimTranscript" class="mt-2 text-sm text-base-content/50 italic">
          ... {{ interimTranscript }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  isRecording: boolean
  isListening: boolean
  transcript: string
  interimTranscript: string
  statusMessage: string
  isProcessing: boolean
}>()

const emit = defineEmits<{
  (e: 'start'): void
  (e: 'stop'): void
  (e: 'clear'): void
  (e: 'update:transcript', value: string): void
}>()

const displayTranscript = computed(() => props.transcript)

const wordCount = computed(() => {
  const text = props.transcript.trim()
  return text ? text.split(/\s+/).length : 0
})

const updateTranscript = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  emit('update:transcript', target.value)
}
</script>

<style scoped>
.animate-pulse {
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}
</style>
