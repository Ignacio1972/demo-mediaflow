/**
 * Schedule Announcement Composable
 * Handles state and logic for the schedule announcement form
 */
import { ref, computed, watch } from 'vue'
import { apiClient } from '@/api/client'

// Types
export type ScheduleType = 'opening' | 'closing'
export type ScheduleVariant = 'normal' | 'in_minutes' | 'immediate'

export interface ScheduleTypeOption {
  id: ScheduleType
  name: string
}

export interface ScheduleVariantOption {
  id: ScheduleVariant
  name: string
  description: string
}

export interface MinutesOption {
  value: number
  label: string
}

export interface OptionsResponse {
  types: ScheduleTypeOption[]
  variants: ScheduleVariantOption[]
  minutes_options: MinutesOption[]
  default_voice_id: string | null
}

export interface PreviewResponse {
  text: string
  schedule_type: string
  variant: string
  minutes: number | null
  use_announcement_sound: boolean
}

export interface GenerateResponse {
  success: boolean
  text: string
  audio_url: string
  audio_id: number
  filename: string
  duration?: number
  voice_id: string
  voice_name: string
  schedule_type: string
  variant: string
  error?: string
}

export interface Voice {
  id: string
  name: string
  active: boolean
}

// Composable
export function useScheduleAnnouncement() {
  // Form state - Always closing, default to "in_minutes" variant
  const scheduleType = ref<ScheduleType>('closing')
  const variant = ref<ScheduleVariant>('in_minutes')
  const minutes = ref<number>(15)
  const voiceId = ref('')
  const useAnnouncementSound = ref(false) // Will sync with template default

  // Options data
  const types = ref<ScheduleTypeOption[]>([])
  const variants = ref<ScheduleVariantOption[]>([])
  const minutesOptions = ref<MinutesOption[]>([])
  const voices = ref<Voice[]>([])

  // Preview state
  const previewText = ref<PreviewResponse | null>(null)

  // Generation state
  const generatedAudio = ref<GenerateResponse | null>(null)

  // Loading states
  const loadingOptions = ref(false)
  const loadingPreview = ref(false)
  const loadingGenerate = ref(false)
  const loadingVoices = ref(false)

  // Error state
  const error = ref<string | null>(null)

  // Computed
  const isFormValid = computed(() => {
    // Voice must be selected
    if (!voiceId.value) return false

    // If variant is in_minutes, minutes must be selected
    if (variant.value === 'in_minutes' && !minutes.value) return false

    return true
  })

  const hasAudio = computed(() => generatedAudio.value !== null)

  // Check if minutes selector should be shown
  const showMinutes = computed(() => {
    return variant.value === 'in_minutes'
  })

  // Get available variants (only closing variants)
  const availableVariants = computed(() => {
    return variants.value
  })

  // Default voice from template configuration
  const configuredDefaultVoiceId = ref<string | null>(null)

  // Actions

  /**
   * Load form options (types, variants, minutes)
   */
  async function loadOptions() {
    loadingOptions.value = true
    error.value = null

    try {
      const response = await apiClient.get<OptionsResponse>(
        '/api/v1/operations/schedules/options'
      )
      types.value = response.types
      variants.value = response.variants
      minutesOptions.value = response.minutes_options
      // Store the configured default voice
      if (response.default_voice_id) {
        configuredDefaultVoiceId.value = response.default_voice_id
      }
    } catch (e: any) {
      console.error('Error loading options:', e)
      error.value = 'Error cargando opciones'
    } finally {
      loadingOptions.value = false
    }
  }

  /**
   * Load available voices
   */
  async function loadVoices() {
    loadingVoices.value = true

    try {
      const response = await apiClient.get<Voice[]>('/api/v1/audio/voices')
      voices.value = response.filter(v => v.active)

      // Set default voice: prefer configured template default, then is_default, then first voice
      if (voices.value.length > 0 && !voiceId.value) {
        const configuredVoice = configuredDefaultVoiceId.value
          ? voices.value.find((v: any) => v.id === configuredDefaultVoiceId.value)
          : null
        const defaultVoice = voices.value.find((v: any) => v.is_default)
        voiceId.value = configuredVoice?.id || defaultVoice?.id || voices.value[0].id
      }
    } catch (e: any) {
      console.error('Error loading voices:', e)
    } finally {
      loadingVoices.value = false
    }
  }

  /**
   * Preview announcement text
   */
  async function previewAnnouncementText() {
    loadingPreview.value = true
    error.value = null

    try {
      const payload: any = {
        schedule_type: scheduleType.value,
        variant: variant.value,
      }

      if (showMinutes.value) {
        payload.minutes = minutes.value
      }

      const response = await apiClient.post<PreviewResponse>(
        '/api/v1/operations/schedules/preview',
        payload
      )
      previewText.value = response
      // Sync announcement sound toggle with template default (only on first load)
      if (previewText.value && !generatedAudio.value) {
        useAnnouncementSound.value = response.use_announcement_sound
      }
    } catch (e: any) {
      console.error('Error generating preview:', e)
      error.value = 'Error generando vista previa'
    } finally {
      loadingPreview.value = false
    }
  }

  /**
   * Generate schedule announcement audio
   */
  async function generateAnnouncement() {
    if (!isFormValid.value) {
      error.value = 'Por favor complete todos los campos requeridos'
      return
    }

    loadingGenerate.value = true
    error.value = null
    generatedAudio.value = null

    try {
      const payload: any = {
        schedule_type: scheduleType.value,
        variant: variant.value,
        voice_id: voiceId.value,
        music_file: null,
        use_announcement_sound: useAnnouncementSound.value,
      }

      if (showMinutes.value) {
        payload.minutes = minutes.value
      }

      const response = await apiClient.post<GenerateResponse>(
        '/api/v1/operations/schedules/generate',
        payload
      )

      if (response.success) {
        generatedAudio.value = response
      } else {
        error.value = response.error || 'Error generando audio'
      }
    } catch (e: any) {
      console.error('Error generating announcement:', e)
      error.value = e.response?.data?.detail || 'Error generando anuncio'
    } finally {
      loadingGenerate.value = false
    }
  }

  /**
   * Reset form to initial state
   */
  function resetForm() {
    scheduleType.value = 'closing'
    variant.value = 'in_minutes'
    minutes.value = 15
    useAnnouncementSound.value = false
    previewText.value = null
    generatedAudio.value = null
    error.value = null
  }

  /**
   * Initialize: load all required data
   * loadOptions first to get default_voice_id, then loadVoices
   */
  async function initialize() {
    await loadOptions()
    await loadVoices()
    // Load initial preview
    await previewAnnouncementText()
  }

  // Watch form fields to update preview
  let previewTimeout: ReturnType<typeof setTimeout> | null = null
  watch(
    [variant, minutes],
    () => {
      if (previewTimeout) {
        clearTimeout(previewTimeout)
      }
      previewTimeout = setTimeout(() => {
        previewAnnouncementText()
      }, 300)
    }
  )

  return {
    // Form state
    scheduleType,
    variant,
    minutes,
    voiceId,
    useAnnouncementSound,

    // Options
    types,
    variants,
    availableVariants,
    minutesOptions,
    voices,

    // Computed
    showMinutes,
    isFormValid,
    hasAudio,

    // Preview
    previewText,

    // Generated audio
    generatedAudio,

    // Loading states
    loadingOptions,
    loadingPreview,
    loadingGenerate,
    loadingVoices,

    // Error
    error,

    // Actions
    initialize,
    loadOptions,
    loadVoices,
    previewAnnouncementText,
    generateAnnouncement,
    resetForm
  }
}
