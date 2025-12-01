/**
 * Voice Manager Composable
 * Handles all voice CRUD operations and state management
 */
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'
import type { Voice } from '@/types/audio'

// Extended voice type for settings management
export interface VoiceSettings extends Voice {
  created_at?: string
  updated_at?: string
}

export interface VoiceTestResult {
  audio_url: string
  duration: number
  filename: string
}

export function useVoiceManager() {
  // State
  const voices = ref<VoiceSettings[]>([])
  const selectedVoice = ref<VoiceSettings | null>(null)
  const isLoading = ref(false)
  const isSaving = ref(false)
  const isTesting = ref(false)
  const error = ref<string | null>(null)
  const successMessage = ref<string | null>(null)

  // Computed
  const activeVoices = computed(() => voices.value.filter(v => v.active))
  const defaultVoice = computed(() => voices.value.find(v => v.is_default))
  const sortedVoices = computed(() => [...voices.value].sort((a, b) => a.order - b.order))

  // Clear messages after delay
  const clearMessages = () => {
    setTimeout(() => {
      error.value = null
      successMessage.value = null
    }, 3000)
  }

  // Load all voices
  const loadVoices = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.get<VoiceSettings[]>('/api/v1/settings/voices')
      voices.value = response
      console.log(`✅ Loaded ${voices.value.length} voices`)
    } catch (e: any) {
      error.value = e.message || 'Error al cargar voces'
      console.error('❌ Failed to load voices:', e)
    } finally {
      isLoading.value = false
    }
  }

  // Select a voice for editing
  const selectVoice = (voice: VoiceSettings | null) => {
    selectedVoice.value = voice ? { ...voice } : null
  }

  // Create new voice
  const createVoice = async (voiceData: Partial<VoiceSettings>): Promise<VoiceSettings | null> => {
    isSaving.value = true
    error.value = null

    try {
      const response = await apiClient.post<VoiceSettings>('/api/v1/settings/voices', voiceData)
      voices.value.push(response)
      successMessage.value = `Voz "${response.name}" creada exitosamente`
      clearMessages()
      return response
    } catch (e: any) {
      error.value = e.message || 'Error al crear voz'
      clearMessages()
      throw e
    } finally {
      isSaving.value = false
    }
  }

  // Update existing voice
  const updateVoice = async (voiceId: string, updates: Partial<VoiceSettings>): Promise<VoiceSettings | null> => {
    isSaving.value = true
    error.value = null

    try {
      const response = await apiClient.patch<VoiceSettings>(`/api/v1/settings/voices/${voiceId}`, updates)

      // Update in local array
      const index = voices.value.findIndex(v => v.id === voiceId)
      if (index !== -1) {
        voices.value[index] = response
      }

      // Update selected if it's the one being edited
      if (selectedVoice.value?.id === voiceId) {
        selectedVoice.value = response
      }

      successMessage.value = `Voz "${response.name}" actualizada`
      clearMessages()
      return response
    } catch (e: any) {
      error.value = e.message || 'Error al actualizar voz'
      clearMessages()
      throw e
    } finally {
      isSaving.value = false
    }
  }

  // Delete voice
  const deleteVoice = async (voiceId: string): Promise<boolean> => {
    isSaving.value = true
    error.value = null

    try {
      await apiClient.delete(`/api/v1/settings/voices/${voiceId}`)

      // Remove from local array
      const voice = voices.value.find(v => v.id === voiceId)
      voices.value = voices.value.filter(v => v.id !== voiceId)

      // Clear selection if deleted
      if (selectedVoice.value?.id === voiceId) {
        selectedVoice.value = null
      }

      successMessage.value = `Voz "${voice?.name}" eliminada`
      clearMessages()
      return true
    } catch (e: any) {
      error.value = e.message || 'Error al eliminar voz'
      clearMessages()
      throw e
    } finally {
      isSaving.value = false
    }
  }

  // Set voice as default
  const setDefaultVoice = async (voiceId: string): Promise<void> => {
    isSaving.value = true
    error.value = null

    try {
      await apiClient.patch(`/api/v1/settings/voices/${voiceId}/set-default`)

      // Update local state
      voices.value.forEach(v => {
        v.is_default = v.id === voiceId
      })

      if (selectedVoice.value?.id === voiceId) {
        selectedVoice.value.is_default = true
      }

      const voice = voices.value.find(v => v.id === voiceId)
      successMessage.value = `"${voice?.name}" es ahora la voz por defecto`
      clearMessages()
    } catch (e: any) {
      error.value = e.message || 'Error al establecer voz por defecto'
      clearMessages()
      throw e
    } finally {
      isSaving.value = false
    }
  }

  // Reorder voices
  const reorderVoices = async (newOrder: string[]): Promise<void> => {
    error.value = null

    try {
      await apiClient.put('/api/v1/settings/voices/reorder', { voice_ids: newOrder })

      // Update local order
      newOrder.forEach((id, index) => {
        const voice = voices.value.find(v => v.id === id)
        if (voice) {
          voice.order = index
        }
      })

      // Resort the array
      voices.value.sort((a, b) => a.order - b.order)
    } catch (e: any) {
      error.value = e.message || 'Error al reordenar voces'
      clearMessages()
      throw e
    }
  }

  // Test voice with ElevenLabs
  const testVoice = async (voiceId: string, text: string): Promise<VoiceTestResult | null> => {
    isTesting.value = true
    error.value = null

    try {
      const response = await apiClient.post<VoiceTestResult>(
        `/api/v1/settings/voices/${voiceId}/test`,
        { text }
      )
      return response
    } catch (e: any) {
      error.value = e.message || 'Error al probar voz'
      clearMessages()
      throw e
    } finally {
      isTesting.value = false
    }
  }

  // Toggle voice active status
  const toggleVoiceActive = async (voiceId: string): Promise<void> => {
    const voice = voices.value.find(v => v.id === voiceId)
    if (!voice) return

    await updateVoice(voiceId, { active: !voice.active })
  }

  return {
    // State
    voices,
    selectedVoice,
    isLoading,
    isSaving,
    isTesting,
    error,
    successMessage,

    // Computed
    activeVoices,
    defaultVoice,
    sortedVoices,

    // Actions
    loadVoices,
    selectVoice,
    createVoice,
    updateVoice,
    deleteVoice,
    setDefaultVoice,
    reorderVoices,
    testVoice,
    toggleVoiceActive,
  }
}
