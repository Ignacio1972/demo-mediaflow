/**
 * Shortcut Manager Composable
 * Handles all shortcut CRUD operations and state management
 */
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'
import type { Shortcut, ShortcutCreate, ShortcutUpdate } from '@/types/shortcut'
import type { AudioMessage } from '@/types/audio'

export function useShortcutManager() {
  // State
  const shortcuts = ref<Shortcut[]>([])
  const selectedShortcut = ref<Shortcut | null>(null)
  const availableAudios = ref<AudioMessage[]>([])
  const isLoading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)
  const successMessage = ref<string | null>(null)

  // Computed
  const activeShortcuts = computed(() =>
    shortcuts.value.filter(s => s.position !== null && s.active)
  )

  const sortedShortcuts = computed(() =>
    [...shortcuts.value].sort((a, b) => {
      // Shortcuts with position first, then by id
      if (a.position !== null && b.position === null) return -1
      if (a.position === null && b.position !== null) return 1
      if (a.position !== null && b.position !== null) return a.position - b.position
      return a.id - b.id
    })
  )

  const availablePositions = computed(() => {
    const usedPositions = shortcuts.value
      .filter(s => s.position !== null)
      .map(s => s.position)
    return [1, 2, 3, 4, 5, 6].filter(p => !usedPositions.includes(p))
  })

  // Clear messages after delay
  const clearMessages = () => {
    setTimeout(() => {
      error.value = null
      successMessage.value = null
    }, 3000)
  }

  // Load all shortcuts
  const loadShortcuts = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.get<Shortcut[]>('/api/v1/settings/shortcuts')
      shortcuts.value = response
      console.log(`✅ Loaded ${shortcuts.value.length} shortcuts`)
    } catch (e: any) {
      error.value = e.message || 'Error al cargar shortcuts'
      console.error('❌ Failed to load shortcuts:', e)
    } finally {
      isLoading.value = false
    }
  }

  // Load available audios (from shortcuts category)
  const loadAvailableAudios = async () => {
    try {
      const response = await apiClient.get<{ messages: AudioMessage[] }>(
        '/api/v1/library?category_id=shortcuts&limit=100'
      )
      availableAudios.value = response.messages || []
      console.log(`✅ Loaded ${availableAudios.value.length} available audios`)
    } catch (e: any) {
      console.error('❌ Failed to load available audios:', e)
    }
  }

  // Select a shortcut for editing
  const selectShortcut = (shortcut: Shortcut | null) => {
    selectedShortcut.value = shortcut ? { ...shortcut } : null
  }

  // Create new shortcut
  const createShortcut = async (shortcutData: ShortcutCreate): Promise<Shortcut | null> => {
    isSaving.value = true
    error.value = null

    try {
      const response = await apiClient.post<Shortcut>('/api/v1/settings/shortcuts', shortcutData)
      shortcuts.value.push(response)
      successMessage.value = `Shortcut "${response.custom_name}" creado exitosamente`
      clearMessages()
      return response
    } catch (e: any) {
      error.value = e.message || 'Error al crear shortcut'
      clearMessages()
      throw e
    } finally {
      isSaving.value = false
    }
  }

  // Update existing shortcut
  const updateShortcut = async (shortcutId: number, updates: ShortcutUpdate): Promise<Shortcut | null> => {
    isSaving.value = true
    error.value = null

    try {
      const response = await apiClient.patch<Shortcut>(`/api/v1/settings/shortcuts/${shortcutId}`, updates)

      // Update in local array
      const index = shortcuts.value.findIndex(s => s.id === shortcutId)
      if (index !== -1) {
        shortcuts.value[index] = response
      }

      // Update selected if it's the one being edited
      if (selectedShortcut.value?.id === shortcutId) {
        selectedShortcut.value = response
      }

      // Reload to get updated positions
      await loadShortcuts()

      successMessage.value = `Shortcut "${response.custom_name}" actualizado`
      clearMessages()
      return response
    } catch (e: any) {
      error.value = e.message || 'Error al actualizar shortcut'
      clearMessages()
      throw e
    } finally {
      isSaving.value = false
    }
  }

  // Update shortcut position
  const updatePosition = async (shortcutId: number, position: number | null): Promise<void> => {
    isSaving.value = true
    error.value = null

    try {
      await apiClient.patch(`/api/v1/settings/shortcuts/${shortcutId}/position`, { position })

      // Reload to get updated positions
      await loadShortcuts()

      successMessage.value = position
        ? `Shortcut asignado a posición ${position}`
        : 'Shortcut removido del grid'
      clearMessages()
    } catch (e: any) {
      error.value = e.message || 'Error al actualizar posición'
      clearMessages()
      throw e
    } finally {
      isSaving.value = false
    }
  }

  // Delete shortcut
  const deleteShortcut = async (shortcutId: number): Promise<boolean> => {
    isSaving.value = true
    error.value = null

    try {
      const shortcut = shortcuts.value.find(s => s.id === shortcutId)
      await apiClient.delete(`/api/v1/settings/shortcuts/${shortcutId}`)

      // Remove from local array
      shortcuts.value = shortcuts.value.filter(s => s.id !== shortcutId)

      // Clear selection if deleted
      if (selectedShortcut.value?.id === shortcutId) {
        selectedShortcut.value = null
      }

      successMessage.value = `Shortcut "${shortcut?.custom_name}" eliminado`
      clearMessages()
      return true
    } catch (e: any) {
      error.value = e.message || 'Error al eliminar shortcut'
      clearMessages()
      throw e
    } finally {
      isSaving.value = false
    }
  }

  // Check if audio already has a shortcut
  const hasShortcut = (audioId: number): boolean => {
    return shortcuts.value.some(s => s.audio_message_id === audioId)
  }

  // Get shortcut by position
  const getShortcutByPosition = (position: number): Shortcut | undefined => {
    return shortcuts.value.find(s => s.position === position)
  }

  return {
    // State
    shortcuts,
    selectedShortcut,
    availableAudios,
    isLoading,
    isSaving,
    error,
    successMessage,

    // Computed
    activeShortcuts,
    sortedShortcuts,
    availablePositions,

    // Actions
    loadShortcuts,
    loadAvailableAudios,
    selectShortcut,
    createShortcut,
    updateShortcut,
    updatePosition,
    deleteShortcut,

    // Helpers
    hasShortcut,
    getShortcutByPosition,
  }
}
