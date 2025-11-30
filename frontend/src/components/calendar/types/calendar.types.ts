// Calendar module types

export interface Schedule {
  id: number
  audio_message_id: number | null
  text_to_generate: string | null
  voice_id: string | null
  category_id: string | null
  schedule_type: 'interval' | 'specific' | 'once'
  start_date: string
  end_date: string | null
  interval_minutes: number | null
  specific_times: string[] | null  // ["09:00", "12:00"]
  days_of_week: number[] | null    // [0,1,2,3,4] = Mon-Fri
  active: boolean
  priority: number
  last_executed_at: string | null
  next_execution_at: string | null
  created_at: string
  updated_at: string
}

export interface ScheduleWithAudio extends Schedule {
  audio_message?: {
    id: number
    display_name: string
    filename: string
    duration: number | null
    voice_id: string
  }
}

export interface CalendarDay {
  date: Date
  dayOfMonth: number
  isCurrentMonth: boolean
  isToday: boolean
  schedules: ScheduleWithAudio[]
}

export interface CalendarWeek {
  days: CalendarDay[]
}

export interface CalendarFilters {
  active: boolean | null
  schedule_type: 'interval' | 'specific' | 'once' | null
}

export type CalendarViewMode = 'month' | 'week' | 'day'

export interface ScheduleFormData {
  audio_message_id: number
  schedule_type: 'interval' | 'specific' | 'once'
  interval_minutes?: number
  specific_times?: string[]
  days_of_week?: number[]
  start_date: string
  end_date?: string
  priority?: number
}
