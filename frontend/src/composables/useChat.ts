/**
 * useChat - Chat assistant composable
 * Handles message state, SSE streaming, conversation persistence
 * Module-level singleton pattern (same as useLayout.ts)
 */
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'
import type { ChatMessage, ChatConversation, SSEEvent } from '@/types/chat'

// ─── Shared state (module-level singleton) ───
const messages = ref<ChatMessage[]>([])
const conversationId = ref<number | null>(null)
const conversations = ref<ChatConversation[]>([])
const isLoading = ref(false)
const isSending = ref(false)
const error = ref<string | null>(null)
const currentToolName = ref<string | null>(null)
let abortController: AbortController | null = null

export function useChat() {
  const hasMessages = computed(() => messages.value.length > 0)

  async function sendMessage(text: string) {
    if (!text.trim() || isSending.value) return

    error.value = null
    isSending.value = true
    currentToolName.value = null

    // Create new AbortController for this request
    abortController?.abort()
    abortController = new AbortController()
    const signal = abortController.signal

    // Optimistic user message
    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: text.trim(),
      created_at: new Date().toISOString(),
    }
    messages.value.push(userMsg)

    // Placeholder for assistant (use reactive reference from array)
    messages.value.push({
      id: `assistant_${Date.now()}`,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
      isStreaming: true,
      tool_calls: [],
    })
    const assistantMsg = messages.value[messages.value.length - 1]

    try {
      const response = await fetch('/api/v1/chat/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text.trim(),
          conversation_id: conversationId.value,
        }),
        signal,
      })

      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`)

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''
      let eventCount = 0

      const parseAndHandle = (buf: string) => {
        for (const eventBlock of buf.split('\n\n')) {
          if (!eventBlock.trim()) continue
          let eventData = ''
          for (const line of eventBlock.split('\n')) {
            if (line.startsWith('data: ')) eventData = line.slice(6)
          }
          if (eventData) {
            try {
              const parsed = JSON.parse(eventData) as SSEEvent
              eventCount++
              console.log(`[SSE #${eventCount}] ${parsed.type}`, parsed.type === 'text_delta' ? `"${(parsed as any).text?.slice(0, 30)}"` : '')
              handleSSEEvent(parsed, assistantMsg)
            } catch (e) {
              console.warn('Failed to parse SSE:', eventData)
            }
          }
        }
      }

      console.log('[Chat] Starting stream read...')
      while (true) {
        const { done, value } = await reader.read()
        if (done) {
          console.log(`[Chat] Stream done. Buffer remaining: ${buffer.length} chars, content length: ${assistantMsg.content.length}`)
          if (buffer.trim()) parseAndHandle(buffer)
          break
        }

        const chunk = decoder.decode(value, { stream: true })
        buffer += chunk

        // Parse SSE: split on double newline
        const events = buffer.split('\n\n')
        buffer = events.pop() || ''
        for (const eventBlock of events) {
          if (!eventBlock.trim()) continue
          parseAndHandle(eventBlock)
        }
      }

      console.log(`[Chat] Final content length: ${assistantMsg.content.length}, events: ${eventCount}`)
      assistantMsg.isStreaming = false
    } catch (e: any) {
      console.error('[Chat] Error:', e)
      if (e.name === 'AbortError') return
      error.value = e.message || 'Error de conexion'
      if (!assistantMsg.content) messages.value.pop()
      else assistantMsg.isStreaming = false
    } finally {
      isSending.value = false
      currentToolName.value = null
    }
  }

  function handleSSEEvent(event: SSEEvent, assistantMsg: ChatMessage) {
    switch (event.type) {
      case 'message_start':
        if (event.conversation_id) conversationId.value = event.conversation_id
        break
      case 'text_delta':
        if (event.text) assistantMsg.content += event.text
        break
      case 'tool_start':
        currentToolName.value = event.tool || null
        break
      case 'tool_result':
        currentToolName.value = null
        if (event.tool && event.result) {
          if (!assistantMsg.tool_calls) assistantMsg.tool_calls = []
          assistantMsg.tool_calls.push({
            tool: event.tool,
            input: event.input || {},
            result: event.result,
          })
        }
        break
      case 'audio_generated':
        if (event.audio_id && event.audio_url) {
          assistantMsg.audio_id = event.audio_id
          assistantMsg.audio_url = event.audio_url
          assistantMsg.audio_duration = event.duration
        }
        break
      case 'message_end':
        assistantMsg.isStreaming = false
        break
      case 'error':
        error.value = event.message || 'Error del asistente'
        assistantMsg.isStreaming = false
        break
    }
  }

  async function loadConversations() {
    try {
      isLoading.value = true
      conversations.value = await apiClient.get<ChatConversation[]>('/api/v1/chat/conversations')
    } catch (e) {
      console.error('Failed to load conversations:', e)
    } finally {
      isLoading.value = false
    }
  }

  async function loadConversation(id: number) {
    try {
      isLoading.value = true
      const data = await apiClient.get<any>(`/api/v1/chat/conversations/${id}`)
      conversationId.value = id
      messages.value = (data.messages || []).map((m: any) => ({ ...m, isStreaming: false }))
    } catch (e) {
      error.value = 'Error cargando conversacion'
    } finally {
      isLoading.value = false
    }
  }

  async function deleteConversation(id: number) {
    try {
      await apiClient.delete(`/api/v1/chat/conversations/${id}`)
      conversations.value = conversations.value.filter(c => c.id !== id)
      if (conversationId.value === id) startNewConversation()
    } catch (e) {
      console.error('Failed to delete conversation:', e)
    }
  }

  function startNewConversation() {
    abortController?.abort()
    abortController = null
    conversationId.value = null
    messages.value = []
    error.value = null
    currentToolName.value = null
    isSending.value = false
  }

  function abortCurrentRequest() {
    abortController?.abort()
    abortController = null
  }

  function clearError() {
    error.value = null
  }

  return {
    messages,
    conversationId,
    conversations,
    isLoading,
    isSending,
    error,
    currentToolName,
    hasMessages,
    sendMessage,
    loadConversations,
    loadConversation,
    deleteConversation,
    startNewConversation,
    abortCurrentRequest,
    clearError,
  }
}
