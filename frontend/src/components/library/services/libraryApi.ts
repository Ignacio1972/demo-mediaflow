import { apiClient } from '@/api/client'
import type { AudioMessage, Category } from '@/types/audio'
import type {
  LibraryFilters,
  LibraryPaginatedResponse,
  Schedule,
  CreateScheduleRequest
} from '../types/library.types'

const BASE_URL = '/api/v1'

export const libraryApi = {
  /**
   * Get paginated list of messages with filters
   */
  async getMessages(filters: Partial<LibraryFilters> = {}): Promise<LibraryPaginatedResponse> {
    const params = new URLSearchParams()

    if (filters.search) params.append('search', filters.search)
    if (filters.category_id) params.append('category_id', filters.category_id)
    if (filters.is_favorite !== null && filters.is_favorite !== undefined) {
      params.append('is_favorite', String(filters.is_favorite))
    }
    if (filters.sort_by) params.append('sort_by', filters.sort_by)
    if (filters.sort_order) params.append('sort_order', filters.sort_order)
    if (filters.page) params.append('page', String(filters.page))
    if (filters.per_page) params.append('per_page', String(filters.per_page))

    const queryString = params.toString()
    const url = `${BASE_URL}/library${queryString ? `?${queryString}` : ''}`

    return apiClient.get<LibraryPaginatedResponse>(url)
  },

  /**
   * Get single message by ID
   */
  async getMessage(id: number): Promise<AudioMessage> {
    return apiClient.get<AudioMessage>(`${BASE_URL}/library/${id}`)
  },

  /**
   * Update message fields (display_name, category_id, is_favorite)
   */
  async updateMessage(id: number, data: Partial<AudioMessage>): Promise<AudioMessage> {
    return apiClient.patch<AudioMessage>(`${BASE_URL}/library/${id}`, data)
  },

  /**
   * Delete single message (soft delete)
   */
  async deleteMessage(id: number): Promise<void> {
    return apiClient.delete(`${BASE_URL}/library/${id}`)
  },

  /**
   * Delete multiple messages
   */
  async deleteMessages(ids: number[]): Promise<{ deleted_count: number }> {
    return apiClient.post<{ deleted_count: number }>(`${BASE_URL}/library/batch-delete`, { ids })
  },

  /**
   * Upload external audio file
   */
  async uploadAudio(file: File, displayName?: string): Promise<AudioMessage> {
    const formData = new FormData()
    formData.append('audio', file)
    if (displayName) {
      formData.append('display_name', displayName)
    }

    const response = await fetch(`${BASE_URL}/library/upload`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Upload failed')
    }

    const result = await response.json()
    return result.data
  },

  /**
   * Get all active categories
   */
  async getCategories(): Promise<Category[]> {
    return apiClient.get<Category[]>(`${BASE_URL}/categories`)
  },

  /**
   * Send message to radio for immediate playback
   */
  async sendToRadio(id: number): Promise<{ success: boolean; message: string }> {
    return apiClient.post(`${BASE_URL}/library/${id}/send-to-radio`)
  },

  /**
   * Create a schedule for a message
   */
  async createSchedule(data: CreateScheduleRequest): Promise<Schedule> {
    return apiClient.post<Schedule>(`${BASE_URL}/schedules`, data)
  },

  /**
   * Get schedules for a message
   */
  async getSchedules(audioMessageId?: number): Promise<Schedule[]> {
    const url = audioMessageId
      ? `${BASE_URL}/schedules?audio_message_id=${audioMessageId}`
      : `${BASE_URL}/schedules`
    return apiClient.get<Schedule[]>(url)
  },

  /**
   * Delete a schedule
   */
  async deleteSchedule(id: number): Promise<void> {
    return apiClient.delete(`${BASE_URL}/schedules/${id}`)
  },

  /**
   * Get audio stream URL
   */
  getAudioUrl(filename: string): string {
    return `${BASE_URL}/audio/stream/${filename}`
  }
}
