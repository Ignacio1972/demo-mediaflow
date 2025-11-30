// Library module specific types
// Base types (AudioMessage, Category) are in @/types/audio.ts

export interface LibraryFilters {
  search: string
  category_id: string | null
  is_favorite: boolean | null
  sort_by: 'created_at' | 'display_name' | 'duration'
  sort_order: 'asc' | 'desc'
  page: number
  per_page: number
}

export interface LibraryPaginatedResponse {
  messages: import('@/types/audio').AudioMessage[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface Schedule {
  id: number
  audio_message_id: number
  schedule_type: 'interval' | 'specific' | 'once'

  // For interval type
  interval_hours?: number
  interval_minutes?: number

  // For specific/interval
  schedule_days?: number[]  // 0=Sun, 1=Mon, ..., 6=Sat
  schedule_times?: string[] // ["09:00", "12:00", "18:00"]

  // For once type
  once_datetime?: string    // ISO 8601

  // Common
  start_date: string
  end_date?: string
  notes?: string
  is_active: boolean

  created_at: string
  updated_at?: string
}

export interface CreateScheduleRequest {
  audio_message_id: number
  schedule_type: 'interval' | 'specific' | 'once'
  interval_hours?: number
  interval_minutes?: number
  schedule_days?: number[]
  schedule_times?: string[]
  once_datetime?: string
  start_date: string
  end_date?: string
  notes?: string
}

export interface UploadAudioResponse {
  success: boolean
  data: import('@/types/audio').AudioMessage
}

export type ViewMode = 'grid' | 'list'

export type MessageAction =
  | 'play'
  | 'schedule'
  | 'send-to-radio'
  | 'edit-in-dashboard'
  | 'delete'
