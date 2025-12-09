/**
 * AI Suggestions Composable
 * Manages AI-generated announcement suggestions
 */
import { ref, reactive, computed } from 'vue'
import { apiClient } from '@/api/client'

export interface Suggestion {
  id: string
  text: string
  char_count: number
  word_count: number
  created_at: string
  edited?: boolean
}

export interface GenerateParams {
  context: string
  category?: string
  tone?: string
  duration?: number
  keywords?: string[]
  temperature?: number
  mode?: 'normal' | 'automatic'
  word_limit?: [number, number]
}

interface GenerateResponse {
  success: boolean
  suggestions: Suggestion[]
  model: string
  active_client_id: string | null
}

export function useAISuggestions() {
  const suggestions = ref<Suggestion[]>([])
  const isGenerating = ref(false)
  const selectedSuggestion = ref<Suggestion | null>(null)
  const lastContext = ref<GenerateParams | null>(null)
  const error = ref<string | null>(null)

  const config = reactive({
    tone: 'profesional',
    duration: 10,
    temperature: 0.8,
    keywords: [] as string[],
    showAdvanced: false
  })

  const hasSuggestions = computed(() => suggestions.value.length > 0)

  async function generate(params: GenerateParams): Promise<Suggestion[]> {
    if (isGenerating.value) return []

    isGenerating.value = true
    error.value = null
    lastContext.value = params

    try {
      const response = await apiClient.post<GenerateResponse>('/api/v1/ai/generate', {
        context: params.context,
        category: params.category || 'general',
        tone: params.tone || config.tone,
        duration: params.duration || config.duration,
        keywords: params.keywords || config.keywords,
        temperature: params.temperature || config.temperature,
        mode: params.mode || 'normal',
        word_limit: params.word_limit
      })

      if (response.success) {
        suggestions.value = response.suggestions
        return suggestions.value
      } else {
        throw new Error('Error generating suggestions')
      }
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message || 'Error generating suggestions'
      console.error('[useAISuggestions] Error:', e)
      throw e
    } finally {
      isGenerating.value = false
    }
  }

  function selectSuggestion(id: string): Suggestion | null {
    const suggestion = suggestions.value.find(s => s.id === id)
    if (suggestion) {
      selectedSuggestion.value = suggestion
      return suggestion
    }
    return null
  }

  function updateSuggestion(id: string, newText: string) {
    const suggestion = suggestions.value.find(s => s.id === id)
    if (suggestion) {
      suggestion.text = newText
      suggestion.char_count = newText.length
      suggestion.word_count = newText.split(/\s+/).filter(w => w).length
      suggestion.edited = true
    }
  }

  function clearSuggestions() {
    suggestions.value = []
    selectedSuggestion.value = null
    lastContext.value = null
    error.value = null
  }

  async function regenerateSuggestion(id: string): Promise<Suggestion | null> {
    if (!lastContext.value) return null

    const suggestion = suggestions.value.find(s => s.id === id)
    if (!suggestion) return null

    try {
      const response = await apiClient.post<GenerateResponse>('/api/v1/ai/generate', {
        ...lastContext.value,
        context: `Genera UNA alternativa diferente para: "${suggestion.text.substring(0, 50)}..."`,
        temperature: 0.9,
        mode: 'automatic'
      })

      if (response.success && response.suggestions.length > 0) {
        const newSuggestion = response.suggestions[0]
        newSuggestion.id = id  // Keep original ID

        const index = suggestions.value.findIndex(s => s.id === id)
        if (index !== -1) {
          suggestions.value[index] = newSuggestion
        }

        return newSuggestion
      }
      return null
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message || 'Error regenerating suggestion'
      console.error('[useAISuggestions] Error regenerating:', e)
      throw e
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    suggestions,
    isGenerating,
    selectedSuggestion,
    config,
    hasSuggestions,
    error,

    // Actions
    generate,
    selectSuggestion,
    updateSuggestion,
    clearSuggestions,
    regenerateSuggestion,
    clearError
  }
}
