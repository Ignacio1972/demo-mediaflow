/**
 * Automatic Mode Composable
 * Handles speech recording, AI text improvement, and jingle generation
 */
import { ref, computed, onUnmounted } from 'vue'
import { apiClient } from '@/api/client'
import type { Voice, MusicTrack } from '@/types/audio'

// Types for automatic mode
export interface AutomaticConfig {
  default_voice_id: string | null
  default_music: string | null
  available_durations: number[]
  word_limits: Record<number, { min: number; max: number }>
}

export interface AutomaticGenerateRequest {
  text: string
  voice_id: string
  music_file: string | null
  target_duration: number
  improve_text: boolean
}

export interface AutomaticGenerateResponse {
  success: boolean
  original_text: string
  improved_text: string
  voice_used: string
  audio_url: string
  filename: string
  duration: number | null
  error: string | null
  audio_id: number | null  // ID for save-to-library functionality
}

export interface RecordingState {
  isRecording: boolean
  isListening: boolean
  transcript: string
  interimTranscript: string
  error: string | null
}

export function useAutomaticMode() {
  // ==================== STATE ====================

  // Recording state
  const isRecording = ref(false)
  const isListening = ref(false)
  const transcript = ref('')
  const interimTranscript = ref('')

  // Processing state
  const isProcessing = ref(false)
  const isGenerating = ref(false)

  // Config state
  const config = ref<AutomaticConfig | null>(null)
  const voices = ref<Voice[]>([])
  const musicTracks = ref<MusicTrack[]>([])

  // Selection state
  const selectedVoiceId = ref<string | null>(null)
  const selectedMusicFile = ref<string | null>(null)
  const targetDuration = ref(20)
  const improveTextEnabled = ref(true)

  // Result state
  const generatedAudio = ref<AutomaticGenerateResponse | null>(null)

  // Messages
  const error = ref<string | null>(null)
  const successMessage = ref<string | null>(null)
  const statusMessage = ref<string>('')

  // Speech Recognition
  let recognition: any = null

  // ==================== COMPUTED ====================

  const activeVoices = computed(() => voices.value.filter(v => v.active))

  const activeMusicTracks = computed(() => musicTracks.value.filter(t => t.active))

  const selectedVoice = computed(() =>
    voices.value.find(v => v.id === selectedVoiceId.value)
  )

  const selectedMusic = computed(() =>
    musicTracks.value.find(t => t.filename === selectedMusicFile.value)
  )

  const canGenerate = computed(() =>
    transcript.value.trim().length > 0 &&
    selectedVoiceId.value !== null &&
    !isProcessing.value &&
    !isGenerating.value
  )

  const wordLimits = computed(() => {
    if (!config.value) return { min: 20, max: 30 }
    return config.value.word_limits[targetDuration.value] || { min: 20, max: 30 }
  })

  // ==================== HELPERS ====================

  const clearMessages = () => {
    setTimeout(() => {
      error.value = null
      successMessage.value = null
    }, 5000)
  }

  const setStatus = (message: string) => {
    statusMessage.value = message
  }

  // ==================== SPEECH RECOGNITION ====================

  const initSpeechRecognition = () => {
    // Check for browser support
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
      isRecording.value = true
      isListening.value = true
      setStatus('Escuchando... Habla ahora')
      console.log('🎙️ Speech recognition started')
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
      console.error('Speech recognition error:', event.error)

      switch (event.error) {
        case 'no-speech':
          setStatus('No se detectó voz. Intenta de nuevo.')
          break
        case 'audio-capture':
          error.value = 'No se pudo acceder al micrófono. Verifica los permisos.'
          break
        case 'not-allowed':
          error.value = 'Permiso de micrófono denegado. Habilítalo en la configuración del navegador.'
          break
        case 'network':
          error.value = 'Error de red. Verifica tu conexión a internet.'
          break
        default:
          error.value = `Error de reconocimiento: ${event.error}`
      }

      stopRecording()
    }

    recognition.onend = () => {
      isListening.value = false
      if (isRecording.value) {
        // Auto-restart if still recording
        try {
          recognition.start()
        } catch (e) {
          console.log('Recognition ended, not restarting')
          isRecording.value = false
        }
      }
    }

    return true
  }

  const startRecording = async () => {
    error.value = null

    // Request microphone permission first
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch (e) {
      error.value = 'No se pudo acceder al micrófono. Verifica los permisos.'
      clearMessages()
      return
    }

    if (!recognition) {
      if (!initSpeechRecognition()) {
        return
      }
    }

    try {
      transcript.value = ''
      interimTranscript.value = ''
      recognition.start()
    } catch (e: any) {
      console.error('Failed to start recognition:', e)
      error.value = 'Error al iniciar el reconocimiento de voz'
      clearMessages()
    }
  }

  const stopRecording = () => {
    if (recognition) {
      isRecording.value = false
      try {
        recognition.stop()
      } catch (e) {
        console.log('Recognition already stopped')
      }
    }
    isListening.value = false
    interimTranscript.value = ''

    if (transcript.value.trim()) {
      setStatus('Grabación completada')
    } else {
      setStatus('No se detectó ningún mensaje')
    }
  }

  const clearTranscript = () => {
    transcript.value = ''
    interimTranscript.value = ''
    generatedAudio.value = null
    setStatus('')
  }

  // ==================== API CALLS ====================

  const loadConfig = async () => {
    try {
      const response = await apiClient.get<AutomaticConfig>('/api/v1/settings/automatic/config')
      config.value = response

      // Set defaults from config
      if (response.default_voice_id) {
        selectedVoiceId.value = response.default_voice_id
      }
      if (response.default_music) {
        selectedMusicFile.value = response.default_music
      }

      console.log('✅ Automatic config loaded')
    } catch (e: any) {
      console.error('Failed to load automatic config:', e)
      error.value = 'Error al cargar configuración'
      clearMessages()
    }
  }

  const loadVoices = async () => {
    try {
      const response = await apiClient.get<Voice[]>('/api/v1/settings/voices')
      voices.value = response

      // Set default voice if not already set
      if (!selectedVoiceId.value) {
        const defaultVoice = response.find(v => v.is_default && v.active)
        if (defaultVoice) {
          selectedVoiceId.value = defaultVoice.id
        } else if (response.length > 0) {
          const firstActive = response.find(v => v.active)
          if (firstActive) {
            selectedVoiceId.value = firstActive.id
          }
        }
      }

      console.log(`✅ Loaded ${voices.value.length} voices`)
    } catch (e: any) {
      console.error('Failed to load voices:', e)
      error.value = 'Error al cargar voces'
      clearMessages()
    }
  }

  const loadMusicTracks = async () => {
    try {
      const response = await apiClient.get<MusicTrack[]>('/api/v1/settings/music')
      musicTracks.value = response

      // Set default music if not already set
      if (!selectedMusicFile.value) {
        const defaultTrack = response.find(t => t.is_default && t.active)
        if (defaultTrack) {
          selectedMusicFile.value = defaultTrack.filename
        }
      }

      console.log(`✅ Loaded ${musicTracks.value.length} music tracks`)
    } catch (e: any) {
      console.error('Failed to load music tracks:', e)
      // Not critical, continue without music
    }
  }

  const generateJingle = async () => {
    if (!canGenerate.value) return

    isGenerating.value = true
    isProcessing.value = true
    error.value = null
    setStatus('Procesando mensaje...')

    try {
      const request: AutomaticGenerateRequest = {
        text: transcript.value.trim(),
        voice_id: selectedVoiceId.value!,
        music_file: selectedMusicFile.value,
        target_duration: targetDuration.value,
        improve_text: improveTextEnabled.value,
      }

      setStatus(improveTextEnabled.value ? 'Mejorando texto con IA...' : 'Generando audio...')

      const response = await apiClient.post<AutomaticGenerateResponse>(
        '/api/v1/settings/automatic/generate',
        request
      )

      if (response.success) {
        generatedAudio.value = response
        successMessage.value = 'Audio generado exitosamente'
        setStatus(`Audio listo (${response.duration?.toFixed(1)}s)`)
        console.log('✅ Jingle generated:', response.filename)
      } else {
        error.value = response.error || 'Error al generar audio'
        setStatus('Error en la generación')
      }

      clearMessages()

    } catch (e: any) {
      console.error('Failed to generate jingle:', e)
      error.value = e.message || 'Error al generar el jingle'
      setStatus('Error en la generación')
      clearMessages()
    } finally {
      isGenerating.value = false
      isProcessing.value = false
    }
  }

  // ==================== LIFECYCLE ====================

  const initialize = async () => {
    setStatus('Cargando...')
    await Promise.all([
      loadConfig(),
      loadVoices(),
      loadMusicTracks(),
    ])
    setStatus('Listo para grabar')
  }

  // Cleanup on unmount
  onUnmounted(() => {
    if (recognition) {
      try {
        recognition.stop()
      } catch (e) {
        // Ignore
      }
      recognition = null
    }
  })

  // ==================== RETURN ====================

  return {
    // Recording state
    isRecording,
    isListening,
    transcript,
    interimTranscript,

    // Processing state
    isProcessing,
    isGenerating,

    // Config
    config,
    voices,
    musicTracks,

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
    selectedVoice,
    selectedMusic,
    canGenerate,
    wordLimits,

    // Actions
    initialize,
    startRecording,
    stopRecording,
    clearTranscript,
    generateJingle,
    loadConfig,
    loadVoices,
    loadMusicTracks,
  }
}
