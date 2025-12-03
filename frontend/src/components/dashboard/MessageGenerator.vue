<template>
  <div class="message-generator">
    <div class="card bg-base-200 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">
          📝 Generar Mensaje TTS
        </h2>

        <!-- Text Input -->
        <div class="form-control mb-6">
          <textarea
            v-model="messageText"
            :maxlength="maxLength"
            class="textarea textarea-bordered h-32 text-lg"
            placeholder="Escribe tu mensaje aquí..."
            :disabled="isLoading"
          ></textarea>
        </div>

        <!-- Controls Row: Music | Voice | Generate -->
        <div class="flex items-center gap-4">
          <!-- Music Selector -->
          <div class="flex-1">
            <select
              v-model="selectedMusic"
              class="select select-bordered w-full"
              :disabled="isLoading || activeMusicTracks.length === 0"
            >
              <option value="">🎵 Sin música</option>
              <option
                v-for="track in activeMusicTracks"
                :key="track.id"
                :value="track.filename"
              >
                {{ getMusicIcon(track.mood) }} {{ track.display_name }}
              </option>
            </select>
          </div>

          <!-- Voice Selector -->
          <div class="flex-1">
            <select
              v-model="selectedVoiceId"
              @change="handleVoiceChange"
              class="select select-bordered w-full"
              :disabled="isLoading || voices.length === 0"
            >
              <option v-if="voices.length === 0" value="">Cargando voces...</option>
              <option
                v-for="voice in voices"
                :key="voice.id"
                :value="voice.id"
              >
                {{ getGenderIcon(voice.gender) }} {{ voice.name }}
              </option>
            </select>
          </div>

          <!-- Generate Button -->
          <button
            @click="handleGenerate"
            class="btn btn-primary btn-lg px-8"
            :disabled="!canGenerate"
          >
            <span v-if="isLoading" class="loading loading-spinner"></span>
            <span v-else class="flex items-center gap-2">
              <MicrophoneIcon class="h-5 w-5" />
              Generar Audio
            </span>
          </button>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="alert alert-error mt-4">
          <div class="flex items-center gap-2">
            <XCircleIcon class="h-5 w-5" />
            <span>{{ error }}</span>
          </div>
          <button @click="clearError" class="btn btn-sm btn-ghost">
            <XMarkIcon class="h-4 w-4" />
          </button>
        </div>

        <!-- Progress Info -->
        <div v-if="isLoading" class="mt-4">
          <progress class="progress progress-primary w-full"></progress>
          <p class="text-sm text-center mt-2 opacity-70">
            Generando audio con {{ selectedVoiceName }}...
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useAudioStore } from '@/stores/audio'
import { storeToRefs } from 'pinia'
import { MicrophoneIcon, XCircleIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import type { Voice } from '@/types/audio'

// Emit events
const emit = defineEmits<{
  audioGenerated: [response: any]
}>()

// Store
const audioStore = useAudioStore()
const { voices, activeMusicTracks, isLoading, error } = storeToRefs(audioStore)

// Form state
const messageText = ref('')
const selectedMusic = ref('')
const selectedVoiceId = ref('')
const priority = ref(4)
const maxLength = 500

// Computed
const textLength = computed(() => messageText.value.length)

const selectedVoiceName = computed(() => {
  const voice = voices.value.find(v => v.id === selectedVoiceId.value)
  return voice?.name || ''
})

const canGenerate = computed(() => {
  return (
    messageText.value.trim().length > 0 &&
    selectedVoiceId.value !== '' &&
    !isLoading.value
  )
})

// Methods
const getGenderIcon = (gender?: string) => {
  if (gender === 'M') return '♂'
  if (gender === 'F') return '♀'
  return '🎤'
}

const getMusicIcon = (mood?: string) => {
  const icons: Record<string, string> = {
    energetic: '🎸',
    calm: '🎻',
    happy: '🎈',
    inspiring: '🎹',
    relaxed: '🎷',
    upbeat: '🎤',
    festive: '🎉',
  }
  return icons[mood || ''] || '🎵'
}

const handleVoiceChange = () => {
  const voice = voices.value.find(v => v.id === selectedVoiceId.value)
  if (voice) {
    audioStore.setSelectedVoice(voice)
  }
}

const clearError = () => {
  audioStore.clearError()
}

const handleGenerate = async () => {
  if (!canGenerate.value) return

  try {
    const hasMusic = selectedMusic.value !== ''

    const response = await audioStore.generateAudio({
      text: messageText.value.trim(),
      voice_id: selectedVoiceId.value,
      add_jingles: hasMusic,
      music_file: hasMusic ? selectedMusic.value : undefined,
      priority: priority.value,
    })

    // Emit event
    emit('audioGenerated', response)

    // Keep text in the form (don't clear - like legacy system)
    // messageText.value = ''

    console.log('✅ Audio generated successfully')
  } catch (e) {
    console.error('❌ Failed to generate audio:', e)
    // Error is already in store
  }
}

// Method to set text from AI suggestions
const setMessageText = (text: string) => {
  messageText.value = text
  console.log('✅ Message text set from AI suggestion')
}

// Load voices and music on mount
onMounted(async () => {
  if (voices.value.length === 0) {
    await audioStore.loadVoices()
  }
  if (activeMusicTracks.value.length === 0) {
    await audioStore.loadMusicTracks()
  }
})

// Auto-select first voice when voices are loaded
watch(voices, (newVoices) => {
  if (newVoices.length > 0 && !selectedVoiceId.value) {
    const defaultVoice = newVoices.find(v => v.is_default) || newVoices[0]
    selectedVoiceId.value = defaultVoice.id
    audioStore.setSelectedVoice(defaultVoice)
  }
}, { immediate: true })

// Expose methods for parent component
defineExpose({
  setMessageText
})
</script>

<style scoped>
.message-generator {
  width: 100%;
}
</style>
