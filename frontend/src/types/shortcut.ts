/**
 * Shortcut types for quick audio playback
 */

export interface AudioMessageInfo {
  id: number
  filename: string
  display_name: string
  duration?: number
  audio_url: string
}

export interface Shortcut {
  id: number
  audio_message_id: number
  custom_name: string
  custom_icon?: string
  custom_color?: string
  position?: number | null
  active: boolean
  created_at?: string
  updated_at?: string
  audio_message?: AudioMessageInfo
}

export interface ShortcutCreate {
  audio_message_id: number
  custom_name: string
  custom_icon?: string
  custom_color?: string
  position?: number | null
}

export interface ShortcutUpdate {
  custom_name?: string
  custom_icon?: string
  custom_color?: string
  position?: number | null
  active?: boolean
}

export interface ShortcutPublic {
  id: number
  audio_message_id: number
  custom_name: string
  custom_icon?: string
  custom_color?: string
  position: number
  audio_url: string
  duration?: number
}
