<template>
  <div class="mobile-playroom h-full flex flex-col bg-base-100">
    <!-- Loading State -->
    <div
      v-if="!isInitialized"
      class="flex-1 flex items-center justify-center"
    >
      <div class="text-center">
        <span class="loading loading-spinner loading-lg text-primary"></span>
        <p class="mt-4 text-base-content/60">Cargando Playroom...</p>
      </div>
    </div>

    <!-- Error Alert (Global) -->
    <div
      v-if="error"
      class="fixed top-20 left-4 right-4 z-40"
    >
      <div class="alert alert-error shadow-lg">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ error }}</span>
        <button class="btn btn-ghost btn-sm" @click="clearError">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Main Content Area -->
    <div v-if="isInitialized" class="flex-1 overflow-hidden">
      <!-- State 1: Voice Selection Carousel -->
      <Transition name="fade" mode="out-in">
        <VoiceCarousel
          v-if="currentState === 'selection'"
          :profiles="voiceProfiles"
          :selected-index="selectedProfileIndex"
          @select="selectProfile"
          @start-recording="startRecording"
          @open-music-selector="openMusicSelector"
        />

        <!-- State 2: Recording -->
        <RecordingView
          v-else-if="currentState === 'recording'"
          :duration="recordingDuration"
          @stop="stopRecording"
          @cancel="resetToSelection"
        />

        <!-- State 3: Generating -->
        <GeneratingView
          v-else-if="currentState === 'generating'"
        />

        <!-- State 4: Playing / Editing -->
        <AudioPlayerView
          v-else-if="currentState === 'playing'"
          :profile="selectedProfile"
          :improved-text="generatedAudio?.improved_text || ''"
          :edited-text="editedText"
          :is-playing="isPlaying"
          :current-time="currentTime"
          :duration="audioDuration"
          :active-tab="playingTab"
          :voices="activeVoices"
          :selected-voice-id="selectedVoiceIdForRegenerate"
          @toggle-play="togglePlayPause"
          @seek="seekTo"
          @show-confirm="showConfirmModal = true"
          @reset="resetToSelection"
          @regenerate-text="regenerateWithText"
          @regenerate-voice="regenerateWithVoice(selectedVoiceIdForRegenerate!)"
          @select-voice="selectedVoiceIdForRegenerate = $event"
          @update:active-tab="playingTab = $event"
          @update:edited-text="editedText = $event"
        />
      </Transition>
    </div>

    <!-- Confirm Modal -->
    <ConfirmModal
      :show="showConfirmModal"
      @confirm="sendToSpeakers"
      @cancel="showConfirmModal = false"
    />

    <!-- Music Selector Modal -->
    <MusicSelectorModal
      :show="showMusicModal"
      :profile-name="musicModalProfile?.name || ''"
      :current-music="musicModalProfile?.defaultMusicFile || null"
      :music-tracks="activeMusicTracks"
      @close="closeMusicSelector"
      @select="updateProfileMusic"
    />

    <!-- Toast Notifications -->
    <Toast :message="toastMessage" />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useMobilePlayroom } from '../composables/useMobilePlayroom'

// Components
import VoiceCarousel from './components/VoiceCarousel.vue'
import RecordingView from './components/RecordingView.vue'
import GeneratingView from './components/GeneratingView.vue'
import AudioPlayerView from './components/AudioPlayerView.vue'
import ConfirmModal from './components/ConfirmModal.vue'
import MusicSelectorModal from './components/MusicSelectorModal.vue'
import Toast from './components/Toast.vue'

// Composable
const {
  // State
  currentState,
  playingTab,
  isInitialized,

  // Profiles
  voiceProfiles,
  selectedProfileIndex,
  selectedProfile,

  // Recording
  recordingDuration,
  transcript,
  interimTranscript,

  // Generation
  generatedAudio,
  editedText,
  selectedVoiceIdForRegenerate,

  // Audio playback
  isPlaying,
  currentTime,
  audioDuration,

  // Data
  activeVoices,
  activeMusicTracks,

  // UI
  error,
  showConfirmModal,
  showMusicModal,
  musicModalProfile,
  toastMessage,

  // Actions
  initialize,
  selectProfile,
  openMusicSelector,
  closeMusicSelector,
  updateProfileMusic,
  startRecording,
  stopRecording,
  regenerateWithText,
  regenerateWithVoice,
  togglePlayPause,
  seekTo,
  sendToSpeakers,
  resetToSelection,
  clearError,
} = useMobilePlayroom()

// Initialize on mount
onMounted(() => {
  initialize()
})
</script>

<style scoped>
.mobile-playroom {
  /* Full height minus navbar */
  height: calc(100vh - 64px);
  overflow: hidden;
}

/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
