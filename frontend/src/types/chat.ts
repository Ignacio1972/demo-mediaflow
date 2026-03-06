/**
 * Chat Assistant Types
 */

export interface ChatConversation {
  id: number
  title: string | null
  is_active: boolean
  message_count: number
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: string | number
  role: 'user' | 'assistant'
  content: string
  tool_calls?: ToolCall[]
  audio_id?: number
  audio_url?: string
  audio_duration?: number
  created_at: string
  isStreaming?: boolean
}

export interface ToolCall {
  tool: string
  input: Record<string, any>
  result: ToolResult
}

export interface ToolResult {
  success: boolean
  data?: any
  message: string
}

export type SSEEventType =
  | 'message_start'
  | 'text_delta'
  | 'tool_start'
  | 'tool_result'
  | 'audio_generated'
  | 'message_end'
  | 'error'

export interface SSEEvent {
  type: SSEEventType
  conversation_id?: number
  text?: string
  tool?: string
  input?: Record<string, any>
  result?: ToolResult
  audio_id?: number
  audio_url?: string
  duration?: number
  message?: string
}

export const TOOL_DISPLAY_NAMES: Record<string, string> = {
  generate_text_suggestions: 'Generando sugerencias de texto',
  generate_audio: 'Generando audio',
  list_voices: 'Consultando voces disponibles',
  list_music_tracks: 'Consultando pistas de musica',
  save_to_library: 'Guardando en biblioteca',
  create_schedule: 'Creando programacion',
  list_schedules: 'Consultando programaciones',
  list_categories: 'Consultando categorias',
  search_library: 'Buscando en biblioteca',
  send_to_radio: 'Enviando a la radio',
}
