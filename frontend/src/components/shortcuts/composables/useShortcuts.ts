/**
 * Shortcuts Composable for Mobile Page
 * Handles fetching active shortcuts and broadcast functionality
 */
import { ref } from 'vue'
import { apiClient } from '@/api/client'
import type { ShortcutPublic } from '@/types/shortcut'

export function useShortcuts() {
  // State
  const shortcuts = ref<ShortcutPublic[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Load active shortcuts (only those with positions 1-6)
  const loadShortcuts = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.get<ShortcutPublic[]>('/api/v1/shortcuts')
      shortcuts.value = response
      console.log(`✅ Loaded ${shortcuts.value.length} active shortcuts`)
    } catch (e: any) {
      error.value = e.message || 'Error al cargar shortcuts'
      console.error('❌ Failed to load shortcuts:', e)
    } finally {
      isLoading.value = false
    }
  }

  // Get shortcut by position
  const getShortcutByPosition = (position: number): ShortcutPublic | undefined => {
    return shortcuts.value.find(s => s.position === position)
  }

  // Send shortcut audio to speakers
  const sendToSpeakers = async (audioId: number): Promise<boolean> => {
    try {
      const response = await apiClient.post<{ success: boolean }>(
        `/api/v1/library/${audioId}/send-to-radio?interrupt=true`
      )
      return response.success
    } catch (e: any) {
      console.error('❌ Failed to send to speakers:', e)
      throw e
    }
  }

  return {
    // State
    shortcuts,
    isLoading,
    error,

    // Actions
    loadShortcuts,
    getShortcutByPosition,
    sendToSpeakers,
  }
}
