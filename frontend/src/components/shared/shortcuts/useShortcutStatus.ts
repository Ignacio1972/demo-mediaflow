/**
 * Shared composable for shortcut status awareness
 * Used by Library and Campaign pages to show shortcut indicators
 */
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'
import type { Shortcut } from '@/types/shortcut'

export function useShortcutStatus() {
  const shortcuts = ref<Shortcut[]>([])

  const shortcutAudioIds = computed(() =>
    new Set(shortcuts.value.map(s => s.audio_message_id))
  )

  const shortcutCount = computed(() => shortcuts.value.length)

  const isFull = computed(() => shortcutCount.value >= 8)

  function hasShortcut(audioId: number): boolean {
    return shortcutAudioIds.value.has(audioId)
  }

  async function refresh(): Promise<void> {
    try {
      const response = await apiClient.get<Shortcut[]>('/api/v1/settings/shortcuts')
      shortcuts.value = response
    } catch (e) {
      console.error('Failed to load shortcut status:', e)
    }
  }

  return {
    shortcuts,
    shortcutAudioIds,
    shortcutCount,
    isFull,
    hasShortcut,
    refresh,
  }
}
