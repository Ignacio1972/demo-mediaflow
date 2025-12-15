/**
 * Audio Store - Pinia
 * Manages audio generation state, voices, and recent messages
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import audioApi from '@/api/audio'
import type {
  Voice,
  AudioMessage,
  AudioGenerateRequest,
  AudioGenerateResponse,
  MusicTrack
} from '@/types/audio'

export const useAudioStore = defineStore('audio', () => {
  // State
  const voices = ref<Voice[]>([])
  const musicTracks = ref<MusicTrack[]>([])
  const selectedVoice = ref<Voice | null>(null)
  const recentMessages = ref<AudioMessage[]>([])
  const currentAudio = ref<AudioGenerateResponse | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const defaultVoice = computed(() => {
    return voices.value.find(v => v.is_default) || voices.value[0] || null
  })

  const activeVoices = computed(() => {
    return voices.value.filter(v => v.active)
  })

  const activeMusicTracks = computed(() => {
    return musicTracks.value.filter(t => t.active)
  })

  const defaultMusicTrack = computed(() => {
    return musicTracks.value.find(t => t.is_default) || null
  })

  // Actions

  /**
   * Load all available voices from API
   */
  async function loadVoices() {
    try {
      isLoading.value = true
      error.value = null

      console.log('📋 Loading voices from API...')
      voices.value = await audioApi.getVoices()

      // Set default voice if not already selected
      if (!selectedVoice.value && voices.value.length > 0) {
        selectedVoice.value = defaultVoice.value
      }

      console.log(`✅ Loaded ${voices.value.length} voices`)
      return voices.value
    } catch (e: any) {
      error.value = `Failed to load voices: ${e.message}`
      console.error('❌ Error loading voices:', e)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Set selected voice
   */
  function setSelectedVoice(voice: Voice) {
    selectedVoice.value = voice
    console.log(`🎙️ Selected voice: ${voice.name}`)
  }

  /**
   * Generate audio from text
   */
  async function generateAudio(request: AudioGenerateRequest): Promise<AudioGenerateResponse> {
    try {
      isLoading.value = true
      error.value = null

      console.log('🎙️ Generating audio...', request)

      const response = await audioApi.generateAudio(request)

      currentAudio.value = response

      // Refresh recent messages
      await loadRecentMessages()

      console.log('✅ Audio generated successfully:', response.filename)
      return response
    } catch (e: any) {
      error.value = `Failed to generate audio: ${e.response?.data?.detail || e.message}`
      console.error('❌ Error generating audio:', e)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Load recent messages
   */
  async function loadRecentMessages(limit: number = 10) {
    try {
      console.log('📋 Loading recent messages...')
      recentMessages.value = await audioApi.getRecentMessages(limit)
      console.log(`✅ Loaded ${recentMessages.value.length} recent messages`)
      return recentMessages.value
    } catch (e: any) {
      console.error('❌ Error loading recent messages:', e)
      // No throw - no es crítico si falla
    }
  }

  /**
   * Load music tracks from API
   */
  async function loadMusicTracks() {
    try {
      console.log('🎵 Loading music tracks from API...')
      musicTracks.value = await audioApi.getMusicTracks()
      console.log(`✅ Loaded ${musicTracks.value.length} music tracks`)
      return musicTracks.value
    } catch (e: any) {
      console.error('❌ Error loading music tracks:', e)
      // No throw - no es crítico si falla
    }
  }

  /**
   * Clear current audio
   */
  function clearCurrentAudio() {
    currentAudio.value = null
  }

  /**
   * Clear error
   */
  function clearError() {
    error.value = null
  }

  /**
   * Save current audio to library
   */
  async function saveToLibrary(audioId: number) {
    try {
      isLoading.value = true
      error.value = null

      console.log('Saving audio to library...', audioId)

      const response = await audioApi.saveToLibrary(audioId)

      // Update current audio if it matches
      if (currentAudio.value && currentAudio.value.audio_id === audioId) {
        // Mark as saved in local state (for UI feedback)
        (currentAudio.value as any).is_saved = true
      }

      console.log('Audio saved to library:', response.message)
      return response
    } catch (e: any) {
      error.value = `Error al guardar: ${e.response?.data?.detail || e.message}`
      console.error('Error saving to library:', e)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Delete audio message
   */
  async function deleteMessage(audioId: number) {
    try {
      console.log('Deleting audio message...', audioId)

      const response = await audioApi.deleteMessage(audioId)

      // Remove from local state
      recentMessages.value = recentMessages.value.filter(m => m.id !== audioId)

      console.log('Audio deleted:', response.message)
      return response
    } catch (e: any) {
      error.value = `Error al eliminar: ${e.response?.data?.detail || e.message}`
      console.error('Error deleting message:', e)
      throw e
    }
  }

  return {
    // State
    voices,
    musicTracks,
    selectedVoice,
    recentMessages,
    currentAudio,
    isLoading,
    error,

    // Computed
    defaultVoice,
    activeVoices,
    activeMusicTracks,
    defaultMusicTrack,

    // Actions
    loadVoices,
    loadMusicTracks,
    setSelectedVoice,
    generateAudio,
    loadRecentMessages,
    clearCurrentAudio,
    clearError,
    saveToLibrary,
    deleteMessage,
  }
})
