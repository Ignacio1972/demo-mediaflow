/**
 * Music Manager Composable
 * Handles all music CRUD operations and state management
 */
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'
import type { MusicTrack } from '@/types/audio'

export function useMusicManager() {
  // State
  const tracks = ref<MusicTrack[]>([])
  const selectedTrack = ref<MusicTrack | null>(null)
  const isLoading = ref(false)
  const isUploading = ref(false)
  const uploadProgress = ref(0)
  const error = ref<string | null>(null)
  const successMessage = ref<string | null>(null)

  // Computed
  const activeTracks = computed(() => tracks.value.filter(t => t.active))
  const defaultTrack = computed(() => tracks.value.find(t => t.is_default))
  const sortedTracks = computed(() => [...tracks.value].sort((a, b) => a.order - b.order))

  // Clear messages after delay
  const clearMessages = () => {
    setTimeout(() => {
      error.value = null
      successMessage.value = null
    }, 3000)
  }

  // Load all tracks
  const loadTracks = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.get<MusicTrack[]>('/api/v1/settings/music')
      tracks.value = response
      console.log(`✅ Loaded ${tracks.value.length} music tracks`)
    } catch (e: any) {
      error.value = e.message || 'Error al cargar música'
      console.error('❌ Failed to load music:', e)
    } finally {
      isLoading.value = false
    }
  }

  // Select a track
  const selectTrack = (track: MusicTrack | null) => {
    selectedTrack.value = track ? { ...track } : null
  }

  // Upload new track
  const uploadTrack = async (
    file: File,
    metadata?: { display_name?: string; artist?: string; genre?: string; mood?: string }
  ): Promise<MusicTrack | null> => {
    isUploading.value = true
    uploadProgress.value = 0
    error.value = null

    try {
      const formData = new FormData()
      formData.append('file', file)

      if (metadata?.display_name) formData.append('display_name', metadata.display_name)
      if (metadata?.artist) formData.append('artist', metadata.artist)
      if (metadata?.genre) formData.append('genre', metadata.genre)
      if (metadata?.mood) formData.append('mood', metadata.mood)

      // Use XMLHttpRequest for progress tracking
      const response = await new Promise<MusicTrack>((resolve, reject) => {
        const xhr = new XMLHttpRequest()

        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            uploadProgress.value = Math.round((event.loaded / event.total) * 100)
          }
        })

        xhr.addEventListener('load', () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve(JSON.parse(xhr.responseText))
          } else {
            const errorData = JSON.parse(xhr.responseText)
            reject(new Error(errorData.detail || 'Upload failed'))
          }
        })

        xhr.addEventListener('error', () => {
          reject(new Error('Network error during upload'))
        })

        xhr.open('POST', '/api/v1/settings/music')
        xhr.send(formData)
      })

      tracks.value.push(response)
      successMessage.value = `"${response.display_name}" subido exitosamente`
      clearMessages()
      return response
    } catch (e: any) {
      error.value = e.message || 'Error al subir música'
      clearMessages()
      throw e
    } finally {
      isUploading.value = false
      uploadProgress.value = 0
    }
  }

  // Update track metadata
  const updateTrack = async (trackId: number, updates: Partial<MusicTrack>): Promise<MusicTrack | null> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.patch<MusicTrack>(`/api/v1/settings/music/${trackId}`, updates)

      // Update in local array
      const index = tracks.value.findIndex(t => t.id === trackId)
      if (index !== -1) {
        tracks.value[index] = response
      }

      // Update selected if it's the one being edited
      if (selectedTrack.value?.id === trackId) {
        selectedTrack.value = response
      }

      successMessage.value = `"${response.display_name}" actualizado`
      clearMessages()
      return response
    } catch (e: any) {
      error.value = e.message || 'Error al actualizar música'
      clearMessages()
      throw e
    } finally {
      isLoading.value = false
    }
  }

  // Delete track
  const deleteTrack = async (trackId: number): Promise<boolean> => {
    isLoading.value = true
    error.value = null

    try {
      await apiClient.delete(`/api/v1/settings/music/${trackId}`)

      // Remove from local array
      const track = tracks.value.find(t => t.id === trackId)
      tracks.value = tracks.value.filter(t => t.id !== trackId)

      // Clear selection if deleted
      if (selectedTrack.value?.id === trackId) {
        selectedTrack.value = null
      }

      successMessage.value = `"${track?.display_name}" eliminado`
      clearMessages()
      return true
    } catch (e: any) {
      error.value = e.message || 'Error al eliminar música'
      clearMessages()
      throw e
    } finally {
      isLoading.value = false
    }
  }

  // Set track as default
  const setDefaultTrack = async (trackId: number): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      await apiClient.patch(`/api/v1/settings/music/${trackId}/set-default`)

      // Update local state
      tracks.value.forEach(t => {
        t.is_default = t.id === trackId
      })

      if (selectedTrack.value?.id === trackId) {
        selectedTrack.value.is_default = true
      }

      const track = tracks.value.find(t => t.id === trackId)
      successMessage.value = `"${track?.display_name}" es ahora la música por defecto`
      clearMessages()
    } catch (e: any) {
      error.value = e.message || 'Error al establecer música por defecto'
      clearMessages()
      throw e
    } finally {
      isLoading.value = false
    }
  }

  // Reorder tracks
  const reorderTracks = async (newOrder: number[]): Promise<void> => {
    error.value = null

    try {
      await apiClient.put('/api/v1/settings/music/reorder', { track_ids: newOrder })

      // Update local order
      newOrder.forEach((id, index) => {
        const track = tracks.value.find(t => t.id === id)
        if (track) {
          track.order = index
        }
      })

      // Resort the array
      tracks.value.sort((a, b) => a.order - b.order)
    } catch (e: any) {
      error.value = e.message || 'Error al reordenar música'
      clearMessages()
      throw e
    }
  }

  // Toggle track active status
  const toggleTrackActive = async (trackId: number): Promise<void> => {
    const track = tracks.value.find(t => t.id === trackId)
    if (!track) return

    await updateTrack(trackId, { active: !track.active })
  }

  // Format duration for display
  const formatDuration = (seconds?: number): string => {
    if (!seconds) return '--:--'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  // Format file size for display
  const formatFileSize = (bytes?: number): string => {
    if (!bytes) return '--'
    const mb = bytes / (1024 * 1024)
    return `${mb.toFixed(1)} MB`
  }

  return {
    // State
    tracks,
    selectedTrack,
    isLoading,
    isUploading,
    uploadProgress,
    error,
    successMessage,

    // Computed
    activeTracks,
    defaultTrack,
    sortedTracks,

    // Actions
    loadTracks,
    selectTrack,
    uploadTrack,
    updateTrack,
    deleteTrack,
    setDefaultTrack,
    reorderTracks,
    toggleTrackActive,

    // Utils
    formatDuration,
    formatFileSize,
  }
}
