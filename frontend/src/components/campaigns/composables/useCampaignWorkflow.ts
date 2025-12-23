import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'
import { useAudioStore } from '@/stores/audio'

// Estados del workflow
export type WorkflowStep = 'input' | 'suggestions' | 'generate' | 'preview'

// Interfaces
export interface Suggestion {
  id: string
  text: string
  char_count: number
  word_count: number
}

export interface GeneratedAudio {
  audio_id: number
  audio_url: string
  filename: string
  duration: number
  voice_name: string
}

// Response types from API
interface AIGenerateResponse {
  success: boolean
  suggestions: Array<{
    id: string
    text: string
    char_count: number
    word_count: number
    created_at: string
  }>
  model: string
  active_client_id: string | null
}

export function useCampaignWorkflow(campaignId: string) {
  const audioStore = useAudioStore()

  // Current step
  const currentStep = ref<WorkflowStep>('input')

  // Step 1: Input
  const inputText = ref('')

  // Step 2: Suggestions
  const suggestions = ref<Suggestion[]>([])
  const isGeneratingSuggestions = ref(false)
  const suggestionsError = ref<string | null>(null)

  // Step 3: Generate
  const selectedSuggestion = ref<Suggestion | null>(null)
  const editedText = ref('')
  const selectedVoiceId = ref('')
  const selectedMusicFile = ref<string | null>(null)
  const addMusic = ref(false)

  // Step 4: Preview
  const generatedAudio = ref<GeneratedAudio | null>(null)
  const isGeneratingAudio = ref(false)
  const audioError = ref<string | null>(null)

  // Step transitions
  function goToStep(step: WorkflowStep) {
    currentStep.value = step
  }

  function startOver() {
    currentStep.value = 'input'
    inputText.value = ''
    suggestions.value = []
    selectedSuggestion.value = null
    editedText.value = ''
    generatedAudio.value = null
    suggestionsError.value = null
    audioError.value = null
  }

  // STEP 1 → STEP 2: Request suggestions from AI
  async function requestSuggestions() {
    if (inputText.value.trim().length < 3) return

    isGeneratingSuggestions.value = true
    suggestionsError.value = null

    try {
      const response = await apiClient.post<AIGenerateResponse>('/api/v1/ai/generate', {
        context: inputText.value,
        tone: 'profesional',
        campaign_id: campaignId
      })

      // Map response to our Suggestion interface
      suggestions.value = response.suggestions.map(s => ({
        id: s.id,
        text: s.text,
        char_count: s.char_count,
        word_count: s.word_count
      }))

      goToStep('suggestions')
    } catch (error: any) {
      suggestionsError.value = error.response?.data?.detail || 'Error al generar sugerencias'
      console.error('Suggestions error:', error)
    } finally {
      isGeneratingSuggestions.value = false
    }
  }

  // STEP 2 → STEP 3: Use a suggestion
  function useSuggestion(suggestion: Suggestion) {
    selectedSuggestion.value = suggestion
    editedText.value = suggestion.text
    goToStep('generate')
  }

  // STEP 3 → STEP 4: Generate audio with TTS
  async function generateAudio() {
    if (editedText.value.trim().length < 10) return
    if (!selectedVoiceId.value) return

    isGeneratingAudio.value = true
    audioError.value = null

    try {
      const response = await audioStore.generateAudio({
        text: editedText.value,
        voice_id: selectedVoiceId.value,
        add_jingles: addMusic.value,
        music_file: addMusic.value && selectedMusicFile.value ? selectedMusicFile.value : undefined,
        category_id: campaignId  // Assign to campaign on generation
      })

      // Get voice name for display
      const voice = audioStore.voices.find(v => v.id === selectedVoiceId.value)

      generatedAudio.value = {
        audio_id: response.audio_id,
        audio_url: response.audio_url,
        filename: response.filename,
        duration: response.duration,
        voice_name: voice?.name || selectedVoiceId.value
      }

      goToStep('preview')
    } catch (error: any) {
      audioError.value = error.response?.data?.detail || 'Error al generar audio'
      console.error('Audio generation error:', error)
    } finally {
      isGeneratingAudio.value = false
    }
  }

  // Save audio to campaign (mark as favorite - category_id already assigned on generation)
  async function saveAudioToCampaign(): Promise<boolean> {
    if (!generatedAudio.value) return false

    try {
      await apiClient.patch(`/api/v1/library/${generatedAudio.value.audio_id}`, {
        is_favorite: true
      })
      return true
    } catch (error) {
      console.error('Save to campaign error:', error)
      return false
    }
  }

  // Computed helpers
  const canRequestSuggestions = computed(() => !isGeneratingSuggestions.value)

  const canGenerateAudio = computed(() =>
    editedText.value.trim().length >= 10 &&
    selectedVoiceId.value &&
    !isGeneratingAudio.value
  )

  const isOnStep = computed(() => ({
    input: currentStep.value === 'input',
    suggestions: currentStep.value === 'suggestions',
    generate: currentStep.value === 'generate',
    preview: currentStep.value === 'preview'
  }))

  return {
    // Step state
    currentStep,
    isOnStep,

    // Step 1
    inputText,

    // Step 2
    suggestions,
    isGeneratingSuggestions,
    suggestionsError,

    // Step 3
    selectedSuggestion,
    editedText,
    selectedVoiceId,
    selectedMusicFile,
    addMusic,

    // Step 4
    generatedAudio,
    isGeneratingAudio,
    audioError,

    // Computed
    canRequestSuggestions,
    canGenerateAudio,

    // Actions
    goToStep,
    startOver,
    requestSuggestions,
    useSuggestion,
    generateAudio,
    saveAudioToCampaign
  }
}

// Export type for provide/inject with TypeScript
export type CampaignWorkflow = ReturnType<typeof useCampaignWorkflow>
