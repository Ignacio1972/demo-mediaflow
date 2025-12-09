/**
 * Mobile Playroom Composable
 * State machine for the mobile-first playroom interface
 * Flow: Selection -> Recording -> Generating -> Playing -> (Edit/Confirm) -> Reset
 */
import { ref, computed, onUnmounted, watch } from 'vue'
import { apiClient } from '@/api/client'
import type { Voice, MusicTrack } from '@/types/audio'
import { voicePhotos } from '@/assets/Characters'

// ==================== TYPES ====================

export interface VoiceProfile {
  id: string
  name: string
  type: string
  color: string
  initials: string
  photoPath: string
  hasMusic: boolean
  defaultMusicFile: string | null
  targetDuration: number
}

export type PlayroomState =
  | 'selection'
  | 'recording'
  | 'generating'
  | 'playing'

export type PlayingTab = 'preview' | 'text' | 'voice'

export interface GeneratedAudioData {
  success: boolean
  original_text: string
  improved_text: string
  voice_used: string
  audio_url: string
  filename: string
  duration: number | null
  audio_id: number | null
}

export interface AutomaticConfig {
  default_voice_id: string | null
  default_music: string | null
  available_durations: number[]
  word_limits: Record<number, { min: number; max: number }>
}

// ==================== VOICE PROFILES ====================

// Color palette for profiles
const PROFILE_COLORS = [
  '#8B5CF6', // Purple
  '#EC4899', // Pink
  '#10B981', // Green
  '#F59E0B', // Amber
  '#3B82F6', // Blue
  '#EF4444', // Red
]

// ==================== COMPOSABLE ====================

export function useMobilePlayroom() {
  // ==================== STATE ====================

  // App state
  const currentState = ref<PlayroomState>('selection')
  const playingTab = ref<PlayingTab>('preview')
  const isInitialized = ref(false)

  // Profile state
  const voiceProfiles = ref<VoiceProfile[]>([])
  const selectedProfileIndex = ref(0)
  const selectedProfile = computed(() => voiceProfiles.value[selectedProfileIndex.value] || null)

  // Recording state
  const isRecording = ref(false)
  const recordingDuration = ref(0)
  const transcript = ref('')
  const interimTranscript = ref('')
  let recordingTimer: ReturnType<typeof setInterval> | null = null
  let recognition: any = null

  // Generation state
  const isGenerating = ref(false)
  const generatedAudio = ref<GeneratedAudioData | null>(null)
  const editedText = ref('')
  const selectedVoiceIdForRegenerate = ref<string | null>(null)

  // Audio state
  const audioElement = ref<HTMLAudioElement | null>(null)
  const isPlaying = ref(false)
  const currentTime = ref(0)
  const audioDuration = ref(0)

  // Data from API
  const voices = ref<Voice[]>([])
  const musicTracks = ref<MusicTrack[]>([])
  const config = ref<AutomaticConfig | null>(null)

  // UI state
  const error = ref<string | null>(null)
  const showConfirmModal = ref(false)
  const showMusicModal = ref(false)
  const musicModalProfileIndex = ref(0)
  const toastMessage = ref<string | null>(null)

  // ==================== COMPUTED ====================

  const activeVoices = computed(() => voices.value.filter(v => v.active))

  const activeMusicTracks = computed(() => musicTracks.value.filter(t => t.active))

  const canStartRecording = computed(() =>
    currentState.value === 'selection' && selectedProfile.value !== null
  )

  const canGenerate = computed(() =>
    transcript.value.trim().length > 0 && selectedProfile.value !== null
  )

  // Get the profile being edited in music modal
  const musicModalProfile = computed(() =>
    voiceProfiles.value[musicModalProfileIndex.value] || null
  )

  // ==================== HELPERS ====================

  const showToast = (message: string, duration = 3000) => {
    toastMessage.value = message
    setTimeout(() => {
      toastMessage.value = null
    }, duration)
  }

  const clearError = () => {
    error.value = null
  }

  const getInitials = (name: string): string => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  // ==================== PROFILE MANAGEMENT ====================

  const buildVoiceProfiles = () => {
    const profiles: VoiceProfile[] = activeVoices.value.map((voice, index) => {
      // Default: sin música (el usuario puede elegir música haciendo clic en el badge)
      return {
        id: voice.id,
        name: voice.name,
        type: getVoiceType(voice),
        color: PROFILE_COLORS[index % PROFILE_COLORS.length],
        initials: getInitials(voice.name),
        photoPath: getVoicePhoto(voice.name),
        hasMusic: false,
        defaultMusicFile: null,
        targetDuration: 15,
      }
    })

    voiceProfiles.value = profiles
    console.log('✅ [MOBILE PLAYROOM] Built voice profiles:', profiles.length)
  }

  const getVoiceType = (voice: Voice): string => {
    // Try to infer type from voice name or settings
    const name = voice.name.toLowerCase()
    if (name.includes('mario')) return 'Anuncios'
    if (name.includes('juan carlos')) return 'Ofertas y Promociones'
    if (name.includes('jose') || name.includes('miguel')) return 'Jingles'
    if (name.includes('francisca')) return 'Celebraciones'
    return 'Locutor'
  }

  const getVoicePhoto = (voiceName: string): string => {
    // Map voice names to photo files using imported photos
    const name = voiceName.toLowerCase()

    // Try to find a matching photo
    for (const [key, photoUrl] of Object.entries(voicePhotos)) {
      if (name.includes(key)) {
        return photoUrl
      }
    }

    // Fallback: no photo (will show initials placeholder)
    return ''
  }

  const selectProfile = (index: number) => {
    selectedProfileIndex.value = index
  }

  // ==================== MUSIC SELECTION ====================

  const openMusicSelector = (profileIndex: number) => {
    musicModalProfileIndex.value = profileIndex
    showMusicModal.value = true
  }

  const closeMusicSelector = () => {
    showMusicModal.value = false
  }

  const updateProfileMusic = (musicFile: string | null) => {
    const profile = voiceProfiles.value[musicModalProfileIndex.value]
    if (profile) {
      // Update the profile's music settings
      profile.defaultMusicFile = musicFile
      profile.hasMusic = musicFile !== null

      console.log(`🎵 [MOBILE PLAYROOM] Updated music for ${profile.name}: ${musicFile || 'No music'}`)
    }
    closeMusicSelector()
  }

  // ==================== SPEECH RECOGNITION ====================

  const initSpeechRecognition = (): boolean => {
    const SpeechRecognition = (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition

    if (!SpeechRecognition) {
      error.value = 'Tu navegador no soporta reconocimiento de voz. Usa Chrome o Edge.'
      return false
    }

    recognition = new SpeechRecognition()
    recognition.lang = 'es-CL'
    recognition.continuous = true
    recognition.interimResults = true
    recognition.maxAlternatives = 1

    recognition.onstart = () => {
      console.log('🎤 [MOBILE PLAYROOM] Speech recognition started')
    }

    recognition.onresult = (event: any) => {
      let finalTranscript = ''
      let interim = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        if (result.isFinal) {
          finalTranscript += result[0].transcript
        } else {
          interim += result[0].transcript
        }
      }

      if (finalTranscript) {
        transcript.value += (transcript.value ? ' ' : '') + finalTranscript.trim()
      }
      interimTranscript.value = interim
    }

    recognition.onerror = (event: any) => {
      console.error('[MOBILE PLAYROOM] Speech recognition error:', event.error)

      switch (event.error) {
        case 'no-speech':
          // Don't show error for no-speech, just continue
          break
        case 'audio-capture':
          error.value = 'No se pudo acceder al micrófono.'
          stopRecording()
          break
        case 'not-allowed':
          error.value = 'Permiso de micrófono denegado.'
          stopRecording()
          break
        case 'network':
          error.value = 'Error de red.'
          stopRecording()
          break
        default:
          // Don't stop for other errors
          break
      }
    }

    recognition.onend = () => {
      if (isRecording.value) {
        // Auto-restart if still recording
        try {
          recognition.start()
        } catch (e) {
          console.log('[MOBILE PLAYROOM] Recognition ended')
        }
      }
    }

    return true
  }

  // ==================== RECORDING ====================

  const startRecording = async () => {
    if (!canStartRecording.value) return

    clearError()

    // Request microphone permission
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch (e) {
      error.value = 'No se pudo acceder al micrófono.'
      return
    }

    // Initialize speech recognition if needed
    if (!recognition) {
      if (!initSpeechRecognition()) {
        return
      }
    }

    // Reset state
    transcript.value = ''
    interimTranscript.value = ''
    recordingDuration.value = 0
    generatedAudio.value = null

    // Start recording
    try {
      recognition.start()
      isRecording.value = true
      currentState.value = 'recording'

      // Start timer
      recordingTimer = setInterval(() => {
        recordingDuration.value++
      }, 1000)

      console.log('🎤 [MOBILE PLAYROOM] Recording started')
    } catch (e: any) {
      console.error('[MOBILE PLAYROOM] Failed to start recording:', e)
      error.value = 'Error al iniciar grabación'
    }
  }

  const stopRecording = () => {
    if (recordingTimer) {
      clearInterval(recordingTimer)
      recordingTimer = null
    }

    if (recognition) {
      isRecording.value = false
      try {
        recognition.stop()
      } catch (e) {
        // Ignore
      }
    }

    interimTranscript.value = ''

    // Check if we have transcript
    if (transcript.value.trim()) {
      console.log('🎤 [MOBILE PLAYROOM] Recording stopped, transcript:', transcript.value)
      // Auto-generate
      generateAudio()
    } else {
      error.value = 'No se detectó voz. Por favor, intenta de nuevo.'
      currentState.value = 'selection'
    }
  }

  // ==================== AUDIO GENERATION ====================

  const generateAudio = async (customText?: string, customVoiceId?: string) => {
    const profile = selectedProfile.value
    if (!profile) return

    const textToUse = customText || transcript.value.trim()
    if (!textToUse) return

    const voiceId = customVoiceId || profile.id

    currentState.value = 'generating'
    isGenerating.value = true
    clearError()

    try {
      const request = {
        text: textToUse,
        voice_id: voiceId,
        music_file: profile.hasMusic ? profile.defaultMusicFile : null,
        target_duration: profile.targetDuration,
        improve_text: true,
      }

      console.log('🪄 [MOBILE PLAYROOM] Generating audio:', request)

      const response = await apiClient.post<GeneratedAudioData>(
        '/api/v1/settings/playroom/generate',
        request
      )

      if (response.success) {
        generatedAudio.value = response
        editedText.value = response.improved_text
        selectedVoiceIdForRegenerate.value = voiceId
        currentState.value = 'playing'
        playingTab.value = 'preview'

        // Auto-play the generated audio
        setTimeout(() => {
          playAudio()
        }, 500)

        console.log('✅ [MOBILE PLAYROOM] Audio generated:', response.filename)
      } else {
        throw new Error(response.improved_text || 'Error al generar audio')
      }
    } catch (e: any) {
      console.error('[MOBILE PLAYROOM] Generation error:', e)
      error.value = e.message || 'Error al generar audio'
      currentState.value = 'selection'
    } finally {
      isGenerating.value = false
    }
  }

  const regenerateWithText = async () => {
    if (!editedText.value.trim()) return
    await generateAudio(editedText.value, selectedVoiceIdForRegenerate.value || undefined)
  }

  const regenerateWithVoice = async (voiceId: string) => {
    selectedVoiceIdForRegenerate.value = voiceId
    // Usa el texto mejorado actual (editedText) para mantener consistencia
    await generateAudio(editedText.value || transcript.value, voiceId)
  }

  // Regenerar con nuevo texto de IA (usa el transcript original)
  const regenerateNewAudio = async () => {
    if (!transcript.value.trim()) return
    // Usa el transcript original para que la IA genere un nuevo texto mejorado
    await generateAudio(transcript.value, selectedVoiceIdForRegenerate.value || undefined)
  }

  // ==================== AUDIO PLAYBACK ====================

  const initAudioElement = () => {
    if (audioElement.value) {
      audioElement.value.removeEventListener('timeupdate', onTimeUpdate)
      audioElement.value.removeEventListener('loadedmetadata', onLoadedMetadata)
      audioElement.value.removeEventListener('ended', onEnded)
    }

    audioElement.value = new Audio()
    audioElement.value.addEventListener('timeupdate', onTimeUpdate)
    audioElement.value.addEventListener('loadedmetadata', onLoadedMetadata)
    audioElement.value.addEventListener('ended', onEnded)
  }

  const onTimeUpdate = () => {
    if (audioElement.value) {
      currentTime.value = audioElement.value.currentTime
    }
  }

  const onLoadedMetadata = () => {
    if (audioElement.value) {
      audioDuration.value = audioElement.value.duration
    }
  }

  const onEnded = () => {
    isPlaying.value = false
    currentTime.value = 0
  }

  const playAudio = () => {
    if (!generatedAudio.value || !audioElement.value) return

    // Use the URL as-is - if it's relative, the browser will resolve it correctly
    const audioUrl = generatedAudio.value.audio_url

    if (audioElement.value.src !== audioUrl) {
      audioElement.value.src = audioUrl
    }

    audioElement.value.play()
      .then(() => {
        isPlaying.value = true
      })
      .catch(e => {
        console.error('[MOBILE PLAYROOM] Play error:', e)
      })
  }

  const pauseAudio = () => {
    if (audioElement.value) {
      audioElement.value.pause()
      isPlaying.value = false
    }
  }

  const togglePlayPause = () => {
    if (isPlaying.value) {
      pauseAudio()
    } else {
      playAudio()
    }
  }

  const seekTo = (time: number) => {
    if (audioElement.value) {
      audioElement.value.currentTime = time
      currentTime.value = time
    }
  }

  // ==================== SEND TO SPEAKERS (MOCK) ====================

  const sendToSpeakers = async () => {
    if (!generatedAudio.value) return

    showConfirmModal.value = false

    // Mock sending to speakers
    console.log('📢 [MOBILE PLAYROOM] Sending to speakers:', generatedAudio.value.filename)

    // Simulate a small delay
    await new Promise(resolve => setTimeout(resolve, 500))

    showToast('✅ Mensaje enviado a los parlantes')

    // Reset to initial state
    resetToSelection()
  }

  // ==================== STATE MANAGEMENT ====================

  const resetToSelection = () => {
    // Stop audio if playing
    if (audioElement.value) {
      audioElement.value.pause()
      audioElement.value.currentTime = 0
    }

    // Reset all state
    currentState.value = 'selection'
    playingTab.value = 'preview'
    transcript.value = ''
    interimTranscript.value = ''
    recordingDuration.value = 0
    generatedAudio.value = null
    editedText.value = ''
    isPlaying.value = false
    currentTime.value = 0
    audioDuration.value = 0
    showConfirmModal.value = false
    clearError()
  }

  const goBack = () => {
    switch (currentState.value) {
      case 'recording':
        stopRecording()
        currentState.value = 'selection'
        break
      case 'generating':
        // Can't go back during generation
        break
      case 'playing':
        resetToSelection()
        break
      default:
        break
    }
  }

  // ==================== API LOADING ====================

  const loadConfig = async () => {
    try {
      const response = await apiClient.get<AutomaticConfig>('/api/v1/settings/playroom/config')
      config.value = response
      console.log('✅ [MOBILE PLAYROOM] Config loaded')
    } catch (e: any) {
      console.error('[MOBILE PLAYROOM] Failed to load config:', e)
    }
  }

  const loadVoices = async () => {
    try {
      const response = await apiClient.get<Voice[]>('/api/v1/settings/voices')
      voices.value = response
      console.log(`✅ [MOBILE PLAYROOM] Loaded ${voices.value.length} voices`)
    } catch (e: any) {
      console.error('[MOBILE PLAYROOM] Failed to load voices:', e)
      error.value = 'Error al cargar voces'
    }
  }

  const loadMusicTracks = async () => {
    try {
      const response = await apiClient.get<MusicTrack[]>('/api/v1/settings/music')
      musicTracks.value = response
      console.log(`✅ [MOBILE PLAYROOM] Loaded ${musicTracks.value.length} music tracks`)
    } catch (e: any) {
      console.error('[MOBILE PLAYROOM] Failed to load music:', e)
    }
  }

  // ==================== INITIALIZATION ====================

  const initialize = async () => {
    console.log('🎮 [MOBILE PLAYROOM] Initializing...')

    // Initialize audio element
    initAudioElement()

    // Load data
    await Promise.all([
      loadConfig(),
      loadVoices(),
      loadMusicTracks(),
    ])

    // Build profiles from voices
    buildVoiceProfiles()

    isInitialized.value = true
    console.log('✅ [MOBILE PLAYROOM] Initialized')
  }

  // Watch for voice changes to rebuild profiles
  watch(activeVoices, () => {
    if (isInitialized.value) {
      buildVoiceProfiles()
    }
  })

  // ==================== CLEANUP ====================

  onUnmounted(() => {
    if (recordingTimer) {
      clearInterval(recordingTimer)
    }

    if (recognition) {
      try {
        recognition.stop()
      } catch (e) {
        // Ignore
      }
      recognition = null
    }

    if (audioElement.value) {
      audioElement.value.pause()
      audioElement.value.removeEventListener('timeupdate', onTimeUpdate)
      audioElement.value.removeEventListener('loadedmetadata', onLoadedMetadata)
      audioElement.value.removeEventListener('ended', onEnded)
      audioElement.value = null
    }
  })

  // ==================== RETURN ====================

  return {
    // State
    currentState,
    playingTab,
    isInitialized,

    // Profiles
    voiceProfiles,
    selectedProfileIndex,
    selectedProfile,

    // Recording
    isRecording,
    recordingDuration,
    transcript,
    interimTranscript,

    // Generation
    isGenerating,
    generatedAudio,
    editedText,
    selectedVoiceIdForRegenerate,

    // Audio playback
    isPlaying,
    currentTime,
    audioDuration,

    // Data
    voices,
    activeVoices,
    musicTracks,
    activeMusicTracks,

    // UI
    error,
    showConfirmModal,
    showMusicModal,
    musicModalProfileIndex,
    musicModalProfile,
    toastMessage,

    // Computed
    canStartRecording,
    canGenerate,

    // Actions
    initialize,
    selectProfile,
    openMusicSelector,
    closeMusicSelector,
    updateProfileMusic,
    startRecording,
    stopRecording,
    generateAudio,
    regenerateWithText,
    regenerateWithVoice,
    regenerateNewAudio,
    playAudio,
    pauseAudio,
    togglePlayPause,
    seekTo,
    sendToSpeakers,
    resetToSelection,
    goBack,
    clearError,
  }
}
