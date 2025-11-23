export interface Voice {
  id: string
  name: string
  elevenlabs_id: string
  active: boolean
  is_default: boolean
  order: number
  gender?: 'M' | 'F'
  accent?: string
  description?: string

  // Voice settings - v2.1
  style: number  // 0-100
  stability: number  // 0-100
  similarity_boost: number  // 0-100
  use_speaker_boost: boolean

  // Volume adjustment
  volume_adjustment: number  // dB

  // Jingle settings
  jingle_settings?: JingleSettings
}

export interface JingleSettings {
  music_volume: number
  voice_volume: number
  duck_level: number
  intro_silence: number
  outro_silence: number
}

export interface AudioMessage {
  id: number
  filename: string
  display_name: string
  file_path: string
  file_size?: number
  duration?: number
  sample_rate?: number
  bitrate?: string
  format: string
  original_text: string
  voice_id: string
  category_id?: string
  is_favorite: boolean  // v2.1
  voice_settings_snapshot?: string
  volume_adjustment: number
  has_jingle: boolean
  music_file?: string
  status: string
  sent_to_player: boolean
  delivered_at?: string
  priority: number
  created_at: string
  updated_at: string
}

export interface Category {
  id: string
  name: string
  icon?: string
  color?: string
  order: number
  active: boolean
}

// Request para generar audio (v2.1 - sin category)
export interface AudioGenerateRequest {
  text: string
  voice_id: string
  add_jingles?: boolean
  music_file?: string
  priority?: number  // 1-5 (1=critical, 5=low)
}

// Response de generación de audio
export interface AudioGenerateResponse {
  audio_id: number
  filename: string
  display_name: string
  audio_url: string
  file_size: number
  duration: number
  status: string
  voice_id: string
  voice_name: string
  settings_applied: {
    style: number
    stability: number
    similarity_boost: number
    volume_adjustment: number
  }
  created_at: string
}

// AI Suggestions - Claude API
export interface AISuggestionsRequest {
  prompt: string  // Required field
  tone?: 'professional' | 'casual' | 'urgent' | 'friendly'
  max_words?: number
  context?: string
}

export interface AISuggestionsResponse {
  suggestions: string[]
}
