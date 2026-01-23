/**
 * Vehicle Announcement Composable
 * Handles state and logic for the vehicle announcement form
 */
import { ref, computed, watch, type Ref, type ComputedRef } from 'vue'
import { apiClient } from '@/api/client'

// Types
export interface VehicleBrand {
  id: string
  name: string
  tts_name?: string  // Accented version for TTS pronunciation
}

export interface VehicleColor {
  id: string
  name: string
  hex_color?: string
}

export interface PlateInfo {
  valid: boolean
  format?: string
  letters?: string
  numbers?: string
  normalized?: string
  pronunciation?: string
  warning?: string
  error?: string
}

export interface TextPreviewResponse {
  original: string
  normalized: string
  plate_info: PlateInfo
  components: {
    marca: string
    color: string
    patente_original: string
    patente_normalized: string
  }
}

export interface VehicleAnnouncementResponse {
  success: boolean
  original_text: string
  normalized_text: string
  audio_url: string
  audio_id: number
  filename: string
  duration?: number
  voice_id: string
  voice_name: string
  template_used: string
  plate_info: PlateInfo
  error?: string
}

export interface Voice {
  id: string
  name: string
  active: boolean
}

export interface TemplateInfo {
  id: string
  name: string
  description: string
  is_default: boolean
}

export interface OptionsResponse {
  brands: VehicleBrand[]
  colors: VehicleColor[]
  templates: TemplateInfo[]
  default_template_id: string | null
}

// Composable
export function useVehicleAnnouncement() {
  // Form state
  const marca = ref('')
  const color = ref('')
  // Plate parts (Chilean format: XX.XX.XX)
  const platePart1 = ref('')
  const platePart2 = ref('')
  const platePart3 = ref('')
  const voiceId = ref('')
  const numberMode = ref<'words' | 'digits'>('digits')
  const templateId = ref<string>('default') // Will be set from backend

  // Combined plate (computed from parts)
  // Format: XX,XXXX (comma after first 2 chars, then 4 chars together)
  const patente = computed(() => {
    const p1 = platePart1.value.trim().toUpperCase()
    const p2 = platePart2.value.trim().toUpperCase()
    const p3 = platePart3.value.trim().toUpperCase()

    if (!p1 && !p2 && !p3) return ''

    // Format: JK,KJ32
    return `${p1},${p2}${p3}`
  })

  // Options data
  const brands = ref<VehicleBrand[]>([])
  const colors = ref<VehicleColor[]>([])
  const voices = ref<Voice[]>([])

  // Preview state
  const previewText = ref<TextPreviewResponse | null>(null)
  const plateValidation = ref<PlateInfo | null>(null)

  // Generation state
  const generatedAudio = ref<VehicleAnnouncementResponse | null>(null)

  // Loading states
  const loadingOptions = ref(false)
  const loadingPreview = ref(false)
  const loadingGenerate = ref(false)
  const loadingVoices = ref(false)

  // Error state
  const error = ref<string | null>(null)

  // Computed
  const isFormValid = computed(() => {
    // Each plate part should have 2 characters
    const plateValid =
      platePart1.value.trim().length === 2 &&
      platePart2.value.trim().length === 2 &&
      platePart3.value.trim().length === 2

    return (
      marca.value.trim().length >= 2 &&
      color.value.trim().length >= 2 &&
      plateValid &&
      voiceId.value.length > 0
    )
  })

  const hasAudio = computed(() => generatedAudio.value !== null)

  // Actions

  /**
   * Load form options (brands, colors, templates)
   */
  async function loadOptions() {
    loadingOptions.value = true
    error.value = null

    try {
      const response = await apiClient.get<OptionsResponse>(
        '/api/v1/operations/vehicles/options'
      )
      brands.value = response.brands
      colors.value = response.colors
      // Set the default template from admin settings
      if (response.default_template_id) {
        templateId.value = response.default_template_id
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

      // Set default voice: prefer Francisca, then is_default, then first voice
      if (voices.value.length > 0 && !voiceId.value) {
        const franciscaVoice = voices.value.find((v: any) => v.id === 'veronica')
        const defaultVoice = voices.value.find((v: any) => v.is_default)
        voiceId.value = franciscaVoice?.id || defaultVoice?.id || voices.value[0].id
      }
    } catch (e: any) {
      console.error('Error loading voices:', e)
    } finally {
      loadingVoices.value = false
    }
  }

  /**
   * Validate license plate
   */
  async function validatePlate(plate: string): Promise<PlateInfo | null> {
    if (!plate || plate.length < 4) {
      plateValidation.value = null
      return null
    }

    try {
      const response = await apiClient.post<PlateInfo>(
        '/api/v1/operations/vehicles/validate-plate',
        { patente: plate }
      )
      plateValidation.value = response
      return response
    } catch (e: any) {
      console.error('Error validating plate:', e)
      return null
    }
  }

  /**
   * Preview normalized text
   */
  async function previewNormalizedText() {
    if (!marca.value || !color.value || !patente.value) {
      return
    }

    loadingPreview.value = true
    error.value = null

    try {
      const response = await apiClient.post<TextPreviewResponse>(
        '/api/v1/operations/vehicles/preview',
        {
          marca: marca.value,
          color: color.value,
          patente: patente.value,
          template: templateId.value,
          number_mode: numberMode.value
        }
      )
      previewText.value = response
    } catch (e: any) {
      console.error('Error generating preview:', e)
      error.value = 'Error generando vista previa'
    } finally {
      loadingPreview.value = false
    }
  }

  /**
   * Generate vehicle announcement audio
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
      const response = await apiClient.post<VehicleAnnouncementResponse>(
        '/api/v1/operations/vehicles/generate',
        {
          marca: marca.value,
          color: color.value,
          patente: patente.value,
          voice_id: voiceId.value,
          music_file: null,
          template: templateId.value,
          number_mode: numberMode.value
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
    marca.value = ''
    color.value = ''
    platePart1.value = ''
    platePart2.value = ''
    platePart3.value = ''
    numberMode.value = 'digits'
    previewText.value = null
    plateValidation.value = null
    generatedAudio.value = null
    error.value = null
  }

  /**
   * Initialize: load all required data
   */
  async function initialize() {
    await Promise.all([
      loadOptions(),
      loadVoices()
    ])
  }

  // Watch patente for real-time validation
  let validateTimeout: ReturnType<typeof setTimeout> | null = null
  watch(patente, (newValue) => {
    if (validateTimeout) {
      clearTimeout(validateTimeout)
    }
    validateTimeout = setTimeout(() => {
      validatePlate(newValue)
    }, 300)
  })

  // Watch form fields to update preview
  let previewTimeout: ReturnType<typeof setTimeout> | null = null
  watch(
    [marca, color, patente, numberMode],
    () => {
      if (previewTimeout) {
        clearTimeout(previewTimeout)
      }
      previewTimeout = setTimeout(() => {
        if (marca.value && color.value && patente.value) {
          previewNormalizedText()
        }
      }, 500)
    }
  )

  return {
    // Form state
    marca,
    color,
    // Plate parts
    platePart1,
    platePart2,
    platePart3,
    patente, // Combined (computed, read-only)
    voiceId,
    numberMode,

    // Options
    brands,
    colors,
    voices,

    // Preview
    previewText,
    plateValidation,

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
    validatePlate,
    previewNormalizedText,
    generateAnnouncement,
    resetForm
  }
}
