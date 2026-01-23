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
  // ElevenLabs 2025 recommended: style=0, stability=50, similarity=75
  style: number  // 0-100
  stability: number  // 0-100
  similarity_boost: number  // 0-100
  use_speaker_boost: boolean
  speed: number  // 0.7-1.2 (ElevenLabs 2025 API)

  // Volume adjustment
  volume_adjustment: number  // dB

  // Jingle settings
  jingle_settings?: JingleSettings

  // TTS settings (for plain TTS without music)
  tts_settings?: TTSSettings
}

export interface JingleSettings {
  music_volume: number
  voice_volume: number
  duck_level: number
  intro_silence: number
  outro_silence: number
}

export interface TTSSettings {
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
  audio_url?: string  // URL for audio playback (provided by API)
}

export interface Category {
  id: string
  name: string
  icon?: string
  color?: string
  order: number
  active: boolean
}

// Voice settings override for advanced users (Dashboard)
export interface VoiceSettingsOverride {
  style?: number           // 0-100
  stability?: number       // 0-100
  similarity_boost?: number // 0-100
  speed?: number           // 0.7-1.2
  volume_adjustment?: number // dB (-20 to +20)
}

// Request para generar audio (v2.1)
export interface AudioGenerateRequest {
  text: string
  voice_id: string
  add_jingles?: boolean
  music_file?: string
  priority?: number  // 1-5 (1=critical, 5=low)
  category_id?: string  // Campaign/category context (assigned on generation)
  voice_settings?: VoiceSettingsOverride  // Optional override for this generation only
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
    speed: number
    volume_adjustment: number
  }
  created_at: string
}

// AI Suggestions - Claude API (Legacy endpoint /suggest)
export interface AISuggestionsRequest {
  prompt: string  // Required field
  tone?: 'professional' | 'casual' | 'urgent' | 'friendly'
  max_words?: number
  context?: string
}

export interface AISuggestionsResponse {
  suggestions: string[]
}

// AI Announcements - Claude API with client context (New endpoint /generate)
export interface AIAnnouncementSuggestion {
  id: string
  text: string
  char_count: number
  word_count: number
  created_at: string
}

export interface AIGenerateRequest {
  context: string
  category?: string
  tone?: 'profesional' | 'entusiasta' | 'amigable' | 'urgente' | 'informativo'
  duration?: number
  keywords?: string[]
  temperature?: number
  mode?: 'normal' | 'automatic'
  word_limit?: [number, number]
}

export interface AIGenerateResponse {
  success: boolean
  suggestions: AIAnnouncementSuggestion[]
  model: string
  active_client_id: string | null
}

// Music Track for jingles
export interface MusicTrack {
  id: number
  filename: string
  display_name: string
  file_size?: number
  duration?: number
  bitrate?: string
  is_default: boolean
  active: boolean
  order: number
  artist?: string
  genre?: string
  mood?: string
  audio_url: string
  created_at?: string
  updated_at?: string
}
