/**
 * Vehicle Announcement Composable
 * Handles state and logic for the vehicle announcement form
 */
import { ref, computed, watch } from 'vue'
import { apiClient } from '@/api/client'

// Types
export interface VehicleBrand {
  id: string
  name: string
}

export interface VehicleColor {
  id: string
  name: string
  hex_color?: string
}

export interface TemplateInfo {
  id: string
  name: string
  description: string
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

export interface MusicTrack {
  id: number
  filename: string
  display_name: string
  is_default: boolean
  active: boolean
}

export interface OptionsResponse {
  brands: VehicleBrand[]
  colors: VehicleColor[]
  templates: TemplateInfo[]
}

// Composable
export function useVehicleAnnouncement() {
  // Form state
  const marca = ref('')
  const color = ref('')
  const patente = ref('')
  const voiceId = ref('')
  const musicFile = ref<string | null>(null)
  const template = ref('default')
  const numberMode = ref<'words' | 'digits'>('words')

  // Options data
  const brands = ref<VehicleBrand[]>([])
  const colors = ref<VehicleColor[]>([])
  const templates = ref<TemplateInfo[]>([])
  const voices = ref<Voice[]>([])
  const musicTracks = ref<MusicTrack[]>([])

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
  const loadingMusic = ref(false)

  // Error state
  const error = ref<string | null>(null)

  // Computed
  const isFormValid = computed(() => {
    return (
      marca.value.trim().length >= 2 &&
      color.value.trim().length >= 2 &&
      patente.value.trim().length >= 4 &&
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
      templates.value = response.templates
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

      // Set default voice if available
      if (voices.value.length > 0 && !voiceId.value) {
        const defaultVoice = voices.value.find((v: any) => v.is_default)
        voiceId.value = defaultVoice?.id || voices.value[0].id
      }
    } catch (e: any) {
      console.error('Error loading voices:', e)
    } finally {
      loadingVoices.value = false
    }
  }

  /**
   * Load available music tracks
   */
  async function loadMusicTracks() {
    loadingMusic.value = true

    try {
      const response = await apiClient.get<MusicTrack[]>('/api/v1/settings/music')
      musicTracks.value = response.filter(m => m.active)

      // Set default music if available
      if (musicTracks.value.length > 0 && !musicFile.value) {
        const defaultTrack = musicTracks.value.find(m => m.is_default)
        if (defaultTrack) {
          musicFile.value = defaultTrack.filename
        }
      }
    } catch (e: any) {
      console.error('Error loading music:', e)
    } finally {
      loadingMusic.value = false
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
          template: template.value,
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
          music_file: musicFile.value,
          template: template.value,
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
    patente.value = ''
    template.value = 'default'
    numberMode.value = 'words'
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
      loadVoices(),
      loadMusicTracks()
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
    [marca, color, patente, template, numberMode],
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
    patente,
    voiceId,
    musicFile,
    template,
    numberMode,

    // Options
    brands,
    colors,
    templates,
    voices,
    musicTracks,

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
    loadingMusic,

    // Error
    error,

    // Computed
    isFormValid,
    hasAudio,

    // Actions
    initialize,
    loadOptions,
    loadVoices,
    loadMusicTracks,
    validatePlate,
    previewNormalizedText,
    generateAnnouncement,
    resetForm
  }
}
