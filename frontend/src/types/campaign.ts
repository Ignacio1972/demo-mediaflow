/**
 * Types for Campaign Manager module
 * Matches backend schemas in app/schemas/campaign.py
 */

export interface Campaign {
  id: string
  name: string
  icon: string | null
  color: string | null
  order: number
  active: boolean
  ai_instructions: string | null
  audio_count: number
  has_ai_training: boolean
  created_at: string | null
  updated_at: string | null
}

export interface CampaignCreate {
  id: string
  name: string
  icon?: string
  color?: string
  order?: number
  active?: boolean
  ai_instructions?: string
}

export interface CampaignUpdate {
  name?: string
  icon?: string
  color?: string
  order?: number
  active?: boolean
  ai_instructions?: string
}

export interface CampaignListResponse {
  campaigns: Campaign[]
  total: number
}

export interface CampaignAudio {
  id: number
  filename: string
  display_name: string
  original_text: string
  voice_id: string
  duration: number | null
  has_jingle: boolean
  music_file: string | null
  is_favorite: boolean
  status: string
  audio_url: string
  created_at: string | null
}

export interface CampaignAudiosResponse {
  audios: CampaignAudio[]
  total: number
  limit: number
  offset: number
}
