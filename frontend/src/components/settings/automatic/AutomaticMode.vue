<template>
  <div class="automatic-mode min-h-screen bg-base-100">
    <SettingsNav />
    <div class="p-6">
      <div class="container mx-auto max-w-4xl">
        <!-- Header -->
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h1 class="text-3xl font-bold text-primary flex items-center gap-3">
              <span class="text-4xl">🎙️</span>
              Modo Automático
            </h1>
            <p class="text-sm text-base-content/60 mt-1">
              Habla y genera jingles automáticamente con mejora de IA
            </p>
          </div>
        </div>

        <!-- Error Alert -->
        <div v-if="error" class="alert alert-error mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ error }}</span>
        </div>

        <!-- Success Alert -->
        <div v-if="successMessage" class="alert alert-success mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ successMessage }}</span>
        </div>

        <!-- Main Content Grid -->
        <div class="grid gap-6">
          <!-- Recording Section -->
          <RecordingSection
            :is-recording="isRecording"
            :is-listening="isListening"
            :transcript="transcript"
            :interim-transcript="interimTranscript"
            :status-message="statusMessage"
            :is-processing="isProcessing"
            @start="startRecording"
            @stop="stopRecording"
            @clear="clearTranscript"
            @update:transcript="transcript = $event"
          />

          <!-- Configuration Section -->
          <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h2 class="card-title text-lg mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Configuración
              </h2>

              <div class="grid md:grid-cols-2 gap-4">
                <!-- Voice Selector -->
                <VoiceSelector
                  :voices="activeVoices"
                  :selected-voice-id="selectedVoiceId"
                  @update:selected-voice-id="selectedVoiceId = $event"
                />

                <!-- Music Selector -->
                <MusicSelector
                  :music-tracks="activeMusicTracks"
                  :selected-music-file="selectedMusicFile"
                  @update:selected-music-file="selectedMusicFile = $event"
                />
              </div>

              <div class="grid md:grid-cols-2 gap-4 mt-4">
                <!-- Duration Selector -->
                <DurationSelector
                  :target-duration="targetDuration"
                  :word-limits="wordLimits"
                  @update:target-duration="targetDuration = $event"
                />

                <!-- AI Improvement Toggle -->
                <div class="form-control">
                  <label class="label">
                    <span class="label-text font-medium">Mejora con IA</span>
                  </label>
                  <label class="label cursor-pointer justify-start gap-3 bg-base-200 rounded-lg p-3">
                    <input
                      type="checkbox"
                      class="toggle toggle-primary"
                      v-model="improveTextEnabled"
                    />
                    <span class="label-text">
                      {{ improveTextEnabled ? 'Activada' : 'Desactivada' }}
                    </span>
                  </label>
                  <label class="label">
                    <span class="label-text-alt text-base-content/50">
                      Claude mejorará el texto para que suene más profesional
                    </span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Generate Button -->
          <div class="flex justify-center">
            <button
              @click="generateJingle"
              :disabled="!canGenerate"
              class="btn btn-primary btn-lg gap-2"
              :class="{ 'loading': isGenerating }"
            >
              <span v-if="!isGenerating">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </span>
              {{ isGenerating ? 'Generando...' : 'Generar Jingle' }}
            </button>
          </div>

          <!-- Audio Player (Result) -->
          <AudioResultPlayer
            v-if="generatedAudio"
            :audio-data="generatedAudio"
            @regenerate="generateJingle"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAutomaticMode } from './composables/useAutomaticMode'
import SettingsNav from '../SettingsNav.vue'
import RecordingSection from './components/RecordingSection.vue'
import VoiceSelector from './components/VoiceSelector.vue'
import MusicSelector from './components/MusicSelector.vue'
import DurationSelector from './components/DurationSelector.vue'
import AudioResultPlayer from './components/AudioResultPlayer.vue'

// Composable
const {
  // Recording state
  isRecording,
  isListening,
  transcript,
  interimTranscript,

  // Processing state
  isProcessing,
  isGenerating,

  // Selection
  selectedVoiceId,
  selectedMusicFile,
  targetDuration,
  improveTextEnabled,

  // Result
  generatedAudio,

  // Messages
  error,
  successMessage,
  statusMessage,

  // Computed
  activeVoices,
  activeMusicTracks,
  canGenerate,
  wordLimits,

  // Actions
  initialize,
  startRecording,
  stopRecording,
  clearTranscript,
  generateJingle,
} = useAutomaticMode()

// Initialize on mount
onMounted(() => {
  initialize()
})
</script>

<style scoped>
.automatic-mode {
  min-height: calc(100vh - 64px);
}
</style>
