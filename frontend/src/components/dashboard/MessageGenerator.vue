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
            class="textarea textarea-bordered h-56 text-lg"
            placeholder="Escribe tu mensaje aquí..."
            :disabled="isLoading"
          ></textarea>
        </div>

        <!-- Controls Row: Voice Avatars | Generate -->
        <div class="flex items-center gap-4">
          <!-- Voice Avatars -->
          <div class="flex-1 flex items-center gap-2">
            <span class="text-lg">🎤</span>
            <div class="flex items-center gap-2">
              <button
                v-for="(voice, index) in voices"
                :key="voice.id"
                @click="selectVoice(index)"
                class="voice-avatar relative rounded-full overflow-hidden transition-all duration-200"
                :class="{
                  'ring-2 ring-primary ring-offset-2 ring-offset-base-200 scale-110': voiceIndex === index,
                  'opacity-60 hover:opacity-100': voiceIndex !== index,
                  'pointer-events-none': isLoading
                }"
                :title="voice.name"
              >
                <img
                  v-if="getVoicePhoto(voice)"
                  :src="getVoicePhoto(voice)!"
                  :alt="voice.name"
                  class="w-9 h-9 object-cover"
                />
                <div
                  v-else
                  class="w-9 h-9 bg-primary text-primary-content flex items-center justify-center text-xs font-bold"
                >
                  {{ getInitials(voice.name) }}
                </div>
              </button>
            </div>
            <span class="text-sm font-medium ml-2">{{ selectedVoiceName }}</span>
          </div>

          <!-- Generate Button -->
          <button
            @click="handleGenerate"
            class="btn btn-primary"
            :disabled="!canGenerate"
          >
            <span v-if="isLoading" class="loading loading-spinner"></span>
            <span v-else class="flex items-center gap-2">
              <MicrophoneIcon class="h-5 w-5" />
              Generar
            </span>
          </button>
        </div>

        <!-- Music Toggle Row -->
        <div class="flex items-center gap-3 mt-4">
          <span class="text-lg">🎵</span>
          <span class="text-sm">Agregar música</span>
          <input
            type="checkbox"
            v-model="addMusic"
            class="toggle toggle-sm toggle-primary"
            :disabled="isLoading || activeMusicTracks.length === 0"
          />
        </div>

        <!-- Collapsible Music Badges -->
        <div
          class="overflow-hidden transition-all duration-300 ease-in-out"
          :class="addMusic ? 'max-h-28 opacity-100 mt-3' : 'max-h-0 opacity-0'"
        >
          <div class="flex flex-wrap items-center gap-2 pl-7">
            <button
              v-for="(track, index) in activeMusicTracks"
              :key="track.id"
              @click="selectMusic(index)"
              class="badge badge-lg gap-1 cursor-pointer transition-all"
              :class="{
                'badge-secondary': musicIndex === index,
                'badge-outline opacity-60 hover:opacity-100': musicIndex !== index
              }"
              :disabled="isLoading"
              :title="track.display_name"
            >
              <span v-if="track.is_default">⭐</span>
              <span>{{ track.display_name }}</span>
            </button>
          </div>
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
import { voicePhotos } from '@/assets/Characters'
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

// Slider state
const voiceIndex = ref(0)
const musicIndex = ref(0)
const addMusic = ref(false)

// Computed
const textLength = computed(() => messageText.value.length)

const selectedVoiceName = computed(() => {
  const voice = voices.value[voiceIndex.value]
  return voice?.name || ''
})


const selectedMusicName = computed(() => {
  const track = activeMusicTracks.value[musicIndex.value]
  return track?.display_name || ''
})

// Get voice photo by name (lowercase match)
const getVoicePhoto = (voice: Voice): string | null => {
  const name = voice.name.toLowerCase()
  return voicePhotos[name] || null
}

// Get initials for fallback avatar
const getInitials = (name: string): string => {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

const canGenerate = computed(() => {
  return (
    messageText.value.trim().length > 0 &&
    selectedVoiceId.value !== '' &&
    !isLoading.value
  )
})

// Methods
const selectVoice = (index: number) => {
  if (isLoading.value) return
  voiceIndex.value = index
}

const selectMusic = (index: number) => {
  if (isLoading.value) return
  musicIndex.value = index
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

// Sync voice index with selectedVoiceId
watch(voiceIndex, (index) => {
  const voice = voices.value[index]
  if (voice) {
    selectedVoiceId.value = voice.id
    audioStore.setSelectedVoice(voice)
  }
})

// Sync music index with selectedMusic
watch(musicIndex, (index) => {
  if (addMusic.value) {
    const track = activeMusicTracks.value[index]
    selectedMusic.value = track?.filename || ''
  }
})

// Handle music toggle
watch(addMusic, (enabled) => {
  if (!enabled) {
    selectedMusic.value = ''
  } else if (activeMusicTracks.value.length > 0) {
    const track = activeMusicTracks.value[musicIndex.value]
    selectedMusic.value = track?.filename || ''
  }
})

// Auto-select first voice when voices are loaded
watch(voices, (newVoices) => {
  if (newVoices.length > 0 && !selectedVoiceId.value) {
    const defaultVoice = newVoices.find(v => v.is_default) || newVoices[0]
    const defaultIndex = newVoices.findIndex(v => v.id === defaultVoice.id)
    voiceIndex.value = defaultIndex >= 0 ? defaultIndex : 0
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

.voice-avatar {
  cursor: pointer;
  flex-shrink: 0;
}

.voice-avatar:hover {
  transform: scale(1.05);
}

.voice-avatar:active {
  transform: scale(0.95);
}
</style>
