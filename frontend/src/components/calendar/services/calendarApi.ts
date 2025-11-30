import { apiClient } from '@/api/client'
import type { Schedule, CalendarFilters } from '../types/calendar.types'

const BASE_URL = '/api/v1'

export const calendarApi = {
  /**
   * Get all schedules with optional filters
   */
  async getSchedules(filters: Partial<CalendarFilters> = {}): Promise<{ success: boolean; data: Schedule[]; total: number }> {
    const params = new URLSearchParams()

    if (filters.active !== null && filters.active !== undefined) {
      params.append('active', String(filters.active))
    }
    if (filters.schedule_type) {
      params.append('schedule_type', filters.schedule_type)
    }

    const queryString = params.toString()
    const url = `${BASE_URL}/schedules${queryString ? `?${queryString}` : ''}`

    return apiClient.get(url)
  },

  /**
   * Get single schedule by ID
   */
  async getSchedule(id: number): Promise<{ success: boolean; data: Schedule }> {
    return apiClient.get(`${BASE_URL}/schedules/${id}`)
  },

  /**
   * Create new schedule
   */
  async createSchedule(data: Partial<Schedule>): Promise<{ success: boolean; data: Schedule }> {
    return apiClient.post(`${BASE_URL}/schedules`, data)
  },

  /**
   * Update schedule (activate/deactivate, change priority, etc.)
   */
  async updateSchedule(id: number, data: Partial<Schedule>): Promise<{ success: boolean; data: Schedule }> {
    return apiClient.patch(`${BASE_URL}/schedules/${id}`, data)
  },

  /**
   * Delete schedule
   */
  async deleteSchedule(id: number): Promise<void> {
    return apiClient.delete(`${BASE_URL}/schedules/${id}`)
  },

  /**
   * Get schedules for a specific audio message
   */
  async getSchedulesForAudio(audioMessageId: number): Promise<{ success: boolean; data: Schedule[]; total: number }> {
    return apiClient.get(`${BASE_URL}/schedules?audio_message_id=${audioMessageId}`)
  },

  /**
   * Toggle schedule active status
   */
  async toggleActive(id: number, active: boolean): Promise<{ success: boolean; data: Schedule }> {
    return apiClient.patch(`${BASE_URL}/schedules/${id}`, { active })
  }
}
