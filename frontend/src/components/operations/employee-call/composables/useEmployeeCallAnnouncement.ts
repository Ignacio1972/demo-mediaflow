/**
 * Employee Call Announcement Composable
 * Handles state and logic for the employee/client call announcement form
 */
import { ref, computed, watch } from 'vue'
import { apiClient } from '@/api/client'

// Types
export type CallType = 'empleado' | 'cliente'

export interface LocationOption {
  id: string
  name: string
}

export interface TemplateInfo {
  id: string
  name: string
  description: string
  is_default: boolean
}

export interface Voice {
  id: string
  name: string
  active: boolean
}

export interface EmployeeCallPreviewResponse {
  original: string
  call_type: string
  nombre: string
  ubicacion: string
  use_announcement_sound: boolean
}

export interface EmployeeCallResponse {
  success: boolean
  text: string
  audio_url: string
  audio_id: number
  filename: string
  duration?: number
  voice_id: string
  voice_name: string
  call_type: string
  error?: string
}

export interface OptionsResponse {
  call_types: { id: string; name: string }[]
  locations: LocationOption[]
  templates: TemplateInfo[]
  default_template_id: string | null
  default_voice_id: string | null
}

// Composable
export function useEmployeeCallAnnouncement() {
  // Form state
  const callType = ref<CallType>('empleado')
  const nombre = ref('')
  const ubicacion = ref('')
  const voiceId = ref('')
  const templateId = ref<string>('employee_call_default')
  const useAnnouncementSound = ref(false)

  // Options data
  const callTypes = ref<{ id: string; name: string }[]>([])
  const locations = ref<LocationOption[]>([])
  const voices = ref<Voice[]>([])

  // Preview state
  const previewText = ref<EmployeeCallPreviewResponse | null>(null)

  // Generation state
  const generatedAudio = ref<EmployeeCallResponse | null>(null)

  // Loading states
  const loadingOptions = ref(false)
  const loadingPreview = ref(false)
  const loadingGenerate = ref(false)
  const loadingVoices = ref(false)

  // Error state
  const error = ref<string | null>(null)

  // Computed
  const isFormValid = computed(() => {
    return (
      nombre.value.trim().length >= 2 &&
      ubicacion.value.trim().length >= 2 &&
      voiceId.value.length > 0
    )
  })

  const hasAudio = computed(() => generatedAudio.value !== null)

  // Default voice from template configuration
  const configuredDefaultVoiceId = ref<string | null>(null)

  // Actions

  /**
   * Load form options (call types, locations, templates)
   */
  async function loadOptions() {
    loadingOptions.value = true
    error.value = null

    try {
      const response = await apiClient.get<OptionsResponse>(
        '/api/v1/operations/employee-call/options'
      )
      callTypes.value = response.call_types
      locations.value = response.locations

      // Set the default template from admin settings
      if (response.default_template_id) {
        templateId.value = response.default_template_id
      }
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
   * Preview text
   */
  async function previewNormalizedText() {
    if (!nombre.value || !ubicacion.value) {
      return
    }

    loadingPreview.value = true
    error.value = null

    try {
      const response = await apiClient.post<EmployeeCallPreviewResponse>(
        '/api/v1/operations/employee-call/preview',
        {
          call_type: callType.value,
          nombre: nombre.value,
          ubicacion: ubicacion.value,
          template: templateId.value
        }
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
   * Generate call announcement audio
   * @param customText Optional custom text to use instead of template
   */
  async function generateAnnouncement(customText?: string) {
    if (!isFormValid.value) {
      error.value = 'Por favor complete todos los campos requeridos'
      return
    }

    loadingGenerate.value = true
    error.value = null
    generatedAudio.value = null

    try {
      const response = await apiClient.post<EmployeeCallResponse>(
        '/api/v1/operations/employee-call/generate',
        {
          call_type: callType.value,
          nombre: nombre.value,
          ubicacion: ubicacion.value,
          voice_id: voiceId.value,
          template: templateId.value,
          use_announcement_sound: useAnnouncementSound.value,
          custom_text: customText || null
        }
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
    callType.value = 'empleado'
    nombre.value = ''
    ubicacion.value = ''
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
  }

  // Watch form fields to update preview
  let previewTimeout: ReturnType<typeof setTimeout> | null = null
  watch(
    [callType, nombre, ubicacion],
    () => {
      if (previewTimeout) {
        clearTimeout(previewTimeout)
      }
      previewTimeout = setTimeout(() => {
        if (nombre.value && ubicacion.value) {
          previewNormalizedText()
        }
      }, 500)
    }
  )

  return {
    // Form state
    callType,
    nombre,
    ubicacion,
    voiceId,
    useAnnouncementSound,

    // Options
    callTypes,
    locations,
    voices,

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

    // Computed
    isFormValid,
    hasAudio,

    // Actions
    initialize,
    loadOptions,
    loadVoices,
    previewNormalizedText,
    generateAnnouncement,
    resetForm
  }
}
