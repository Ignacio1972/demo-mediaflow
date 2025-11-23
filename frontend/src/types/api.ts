export interface APIResponse<T = any> {
  status: 'ok' | 'error'
  data?: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface WebSocketMessage {
  type: string
  data: any
  timestamp?: string
}
