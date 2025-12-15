/**
 * Audio API Client
 * Handles all audio-related API calls
 */
import { apiClient } from './client'
import type {
  Voice,
  AudioMessage,
  AudioGenerateRequest,
  AudioGenerateResponse,
  AISuggestionsRequest,
  AISuggestionsResponse,
  AIGenerateRequest,
  AIGenerateResponse,
  MusicTrack
} from '@/types/audio'

export const audioApi = {
  /**
   * Get all active voices
   */
  async getVoices(): Promise<Voice[]> {
    return apiClient.get<Voice[]>('/api/v1/audio/voices')
  },

  /**
   * Get specific voice by ID
   */
  async getVoice(voiceId: string): Promise<Voice> {
    return apiClient.get<Voice>(`/api/v1/audio/voices/${voiceId}`)
  },

  /**
   * Generate TTS audio with automatic voice settings
   */
  async generateAudio(request: AudioGenerateRequest): Promise<AudioGenerateResponse> {
    return apiClient.post<AudioGenerateResponse>(
      '/api/v1/audio/generate',
      request
    )
  },

  /**
   * Get recent messages for Dashboard display
   */
  async getRecentMessages(limit: number = 10): Promise<AudioMessage[]> {
    return apiClient.get<AudioMessage[]>('/api/v1/audio/recent', {
      params: { limit }
    })
  },

  /**
   * Generate AI text suggestions using Claude (legacy endpoint)
   */
  async generateAISuggestions(params: AISuggestionsRequest): Promise<AISuggestionsResponse> {
    return apiClient.post<AISuggestionsResponse>(
      '/api/v1/ai/suggest',
      params
    )
  },

  /**
   * Generate AI announcements with client context
   * Uses the active AI client's context for generation
   */
  async generateAnnouncements(params: AIGenerateRequest): Promise<AIGenerateResponse> {
    return apiClient.post<AIGenerateResponse>(
      '/api/v1/ai/generate',
      params
    )
  },

  /**
   * Save audio to library (mark as favorite)
   */
  async saveToLibrary(audioId: number): Promise<{ success: boolean; message: string; data: any }> {
    return apiClient.patch<{ success: boolean; message: string; data: any }>(
      `/api/v1/audio/${audioId}/save-to-library`
    )
  },

  /**
   * Get all active music tracks for jingle selection
   */
  async getMusicTracks(): Promise<MusicTrack[]> {
    return apiClient.get<MusicTrack[]>('/api/v1/settings/music', {
      params: { active_only: true }
    })
  },

  /**
   * Delete an audio message
   */
  async deleteMessage(audioId: number): Promise<{ success: boolean; message: string; data: any }> {
    return apiClient.delete<{ success: boolean; message: string; data: any }>(
      `/api/v1/audio/${audioId}`
    )
  },
}

export default audioApi
