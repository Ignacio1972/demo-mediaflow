/**
 * Audio API Client
 * Handles all audio-related API calls
 */
import apiClient from './client'
import type {
  Voice,
  AudioMessage,
  AudioGenerateRequest,
  AudioGenerateResponse,
  AISuggestionsRequest,
  AISuggestionsResponse
} from '@/types/audio'

export const audioApi = {
  /**
   * Get all active voices
   */
  async getVoices(): Promise<Voice[]> {
    const response = await apiClient.get<Voice[]>('/api/v1/audio/voices')
    return response.data
  },

  /**
   * Get specific voice by ID
   */
  async getVoice(voiceId: string): Promise<Voice> {
    const response = await apiClient.get<Voice>(`/api/v1/audio/voices/${voiceId}`)
    return response.data
  },

  /**
   * Generate TTS audio with automatic voice settings
   */
  async generateAudio(request: AudioGenerateRequest): Promise<AudioGenerateResponse> {
    const response = await apiClient.post<AudioGenerateResponse>(
      '/api/v1/audio/generate',
      request
    )
    return response.data
  },

  /**
   * Get recent messages for Dashboard display
   */
  async getRecentMessages(limit: number = 10): Promise<AudioMessage[]> {
    const response = await apiClient.get<AudioMessage[]>('/api/v1/audio/recent', {
      params: { limit }
    })
    return response.data
  },

  /**
   * Generate AI text suggestions using Claude
   */
  async generateAISuggestions(params: AISuggestionsRequest): Promise<AISuggestionsResponse> {
    const response = await apiClient.post<AISuggestionsResponse>(
      '/api/v1/ai/suggest',
      params
    )
    return response.data
  },
}

export default audioApi
