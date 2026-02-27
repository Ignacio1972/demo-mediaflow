# Chat Assistant - Fase 2: Frontend

**Objetivo**: Interfaz de chat conversacional en Vue 3 que consume el backend SSE de la Fase 1.

**Prerequisito**: Fase 1 (Backend) completada y funcional.

**Resultado**: Página dedicada `/chat` con streaming real de texto, audio inline y acciones del sistema.

---

## Arquitectura

> **Decisión de diseño**: Ruta dedicada `/chat` en vez de widget flotante.
> El chat es un workflow core (generar texto, elegir opciones, previsualizar audio, programar),
> no un soporte secundario. Necesita espacio completo para mostrar sugerencias, players y acciones.
> Los componentes internos son reutilizables — si en el futuro se quiere un widget flotante o panel
> lateral, solo cambia el contenedor.

```
App.vue
├── AppHeader / AppSidebar
├── <router-view />
│   ├── /campaigns → CampaignsPage
│   ├── /library   → Library
│   ├── /chat      → ChatPage       ← NUEVO (ruta dedicada)
│   └── ...
│
ChatPage.vue
├── ChatHeader
├── ChatMessages
│   ├── UserMessage
│   ├── AssistantMessage
│   ├── AudioMessage (player inline)
│   └── ToolStatus
└── ChatInput
```

```
frontend/src/
├── components/chat/
│   ├── ChatPage.vue              # Página principal (reemplaza ChatWidget + ChatPanel)
│   ├── ChatHeader.vue
│   ├── ChatMessages.vue
│   ├── ChatInput.vue
│   └── messages/
│       ├── UserMessage.vue
│       ├── AssistantMessage.vue
│       ├── AudioMessage.vue
│       └── ToolStatus.vue
├── composables/
│   └── useChat.ts
└── types/
    └── chat.ts
```

---

## Paso 1: Tipos TypeScript

### Archivo: `frontend/src/types/chat.ts`

```typescript
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
  list_music_tracks: 'Consultando pistas de música',
  save_to_library: 'Guardando en biblioteca',
  create_schedule: 'Creando programación',
  list_schedules: 'Consultando programaciones',
  list_categories: 'Consultando categorías',
  search_library: 'Buscando en biblioteca',
  send_to_radio: 'Enviando a la radio',
}
```

---

## Paso 2: Composable useChat

### Archivo: `frontend/src/composables/useChat.ts`

Maneja estado, envío de mensajes, parsing SSE y persistencia. Usa fetch nativo + ReadableStream para SSE.

```typescript
/**
 * useChat - Chat assistant composable
 * Handles message state, SSE streaming, conversation persistence
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
export function useChat() {
  const hasMessages = computed(() => messages.value.length > 0)

  async function sendMessage(text: string) {
    if (!text.trim() || isSending.value) return

    error.value = null
    isSending.value = true
    currentToolName.value = null

    // Optimistic user message
    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: text.trim(),
      created_at: new Date().toISOString(),
    }
    messages.value.push(userMsg)

    // Placeholder for assistant
    const assistantMsg: ChatMessage = {
      id: `assistant_${Date.now()}`,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
      isStreaming: true,
      tool_calls: [],
    }
    messages.value.push(assistantMsg)

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || ''}/api/v1/chat/send`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: text.trim(),
            conversation_id: conversationId.value,
          }),
        }
      )

      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`)

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // Parse SSE: split on double newline
        const events = buffer.split('\n\n')
        buffer = events.pop() || ''

        for (const eventBlock of events) {
          if (!eventBlock.trim()) continue
          let eventData = ''
          for (const line of eventBlock.split('\n')) {
            if (line.startsWith('data: ')) eventData = line.slice(6)
          }
          if (eventData) {
            try {
              handleSSEEvent(JSON.parse(eventData) as SSEEvent, assistantMsg)
            } catch (e) {
              console.warn('Failed to parse SSE:', eventData)
            }
          }
        }
      }

      assistantMsg.isStreaming = false
    } catch (e: any) {
      error.value = e.message || 'Error de conexión'
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
          assistantMsg.tool_calls.push({ tool: event.tool, input: event.input || {}, result: event.result })
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
      error.value = 'Error cargando conversación'
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
    conversationId.value = null
    messages.value = []
    error.value = null
    currentToolName.value = null
  }

  function clearError() { error.value = null }

  return {
    messages, conversationId, conversations, isLoading, isSending,
    error, currentToolName, hasMessages,
    sendMessage, loadConversations, loadConversation, deleteConversation,
    startNewConversation, clearError,
  }
}
```

---

## Paso 3: Componentes

### 3.1 ChatPage.vue

Página dedicada que ocupa todo el espacio del content area (dentro del layout existente con AppHeader + AppSidebar).

```vue
<script setup lang="ts">
import { onMounted } from 'vue'
import { useChat } from '@/composables/useChat'
import ChatHeader from './ChatHeader.vue'
import ChatMessages from './ChatMessages.vue'
import ChatInput from './ChatInput.vue'

const { messages, isSending, error, currentToolName, loadConversations, clearError } = useChat()

onMounted(() => {
  loadConversations()
})
</script>

<template>
  <div class="flex flex-col h-[calc(100vh-7rem)] max-w-4xl mx-auto">
    <ChatHeader />

    <div v-if="error" class="px-4 py-2 bg-error/10 text-error text-sm flex items-center gap-2 rounded-lg mx-4">
      <span class="flex-1">{{ error }}</span>
      <button @click="clearError" class="btn btn-ghost btn-xs">✕</button>
    </div>

    <ChatMessages :messages="messages" :is-sending="isSending"
                  :current-tool="currentToolName" class="flex-1 overflow-y-auto" />

    <ChatInput :disabled="isSending" />
  </div>
</template>
```

### 3.2 ChatHeader.vue

```vue
<script setup lang="ts">
import { useChat } from '@/composables/useChat'

const { startNewConversation, conversationId, conversations, loadConversation } = useChat()
</script>

<template>
  <div class="flex items-center gap-3 px-4 py-3 border-b border-base-300">
    <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
           stroke-width="1.5" stroke="currentColor" class="w-4 h-4 text-primary">
        <path stroke-linecap="round" stroke-linejoin="round"
              d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
      </svg>
    </div>
    <div class="flex-1">
      <h3 class="text-sm font-semibold">Asistente MediaFlow</h3>
      <p class="text-xs text-base-content/50">IA conversacional</p>
    </div>

    <!-- Conversaciones recientes (dropdown) -->
    <div v-if="conversations.length" class="dropdown dropdown-end">
      <label tabindex="0" class="btn btn-ghost btn-xs" title="Conversaciones">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
             stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round"
                d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
        </svg>
      </label>
      <ul tabindex="0" class="dropdown-content z-10 menu p-2 shadow-lg bg-base-100
                              border border-base-300 rounded-box w-64 max-h-60 overflow-y-auto">
        <li v-for="conv in conversations" :key="conv.id">
          <a @click="loadConversation(conv.id)"
             :class="{ 'active': conv.id === conversationId }"
             class="text-xs truncate">
            {{ conv.title || 'Sin título' }}
          </a>
        </li>
      </ul>
    </div>

    <button v-if="conversationId" @click="startNewConversation"
            class="btn btn-ghost btn-xs" title="Nueva conversación">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
           stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
      </svg>
    </button>
  </div>
</template>
```

### 3.3 ChatMessages.vue

```vue
<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { ChatMessage } from '@/types/chat'
import UserMessage from './messages/UserMessage.vue'
import AssistantMessage from './messages/AssistantMessage.vue'
import AudioMessage from './messages/AudioMessage.vue'
import ToolStatus from './messages/ToolStatus.vue'

const props = defineProps<{
  messages: ChatMessage[]
  isSending: boolean
  currentTool: string | null
}>()

const scrollContainer = ref<HTMLElement | null>(null)

watch(
  () => [props.messages.length, props.messages[props.messages.length - 1]?.content],
  async () => {
    await nextTick()
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  },
  { deep: true }
)
</script>

<template>
  <div ref="scrollContainer" class="px-4 py-3 space-y-3">
    <!-- Welcome -->
    <div v-if="!messages.length" class="flex flex-col items-center justify-center h-full text-center py-12">
      <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
             stroke-width="1.5" stroke="currentColor" class="w-8 h-8 text-primary">
          <path stroke-linecap="round" stroke-linejoin="round"
                d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
        </svg>
      </div>
      <h3 class="text-base font-semibold mb-1">Asistente MediaFlow</h3>
      <p class="text-sm text-base-content/50 max-w-[260px]">
        Describe lo que necesitas y te ayudo a crear anuncios de audio, programarlos y más.
      </p>
    </div>

    <!-- Messages -->
    <template v-for="msg in messages" :key="msg.id">
      <UserMessage v-if="msg.role === 'user'" :message="msg" />
      <template v-else>
        <AssistantMessage :message="msg" />
        <AudioMessage v-if="msg.audio_url" :audio-url="msg.audio_url"
                      :duration="msg.audio_duration" :audio-id="msg.audio_id" />
      </template>
    </template>

    <ToolStatus v-if="currentTool" :tool-name="currentTool" />

    <!-- Typing indicator -->
    <div v-if="isSending && messages[messages.length - 1]?.isStreaming && !messages[messages.length - 1]?.content && !currentTool"
         class="flex items-center gap-2 px-3 py-2">
      <span class="loading loading-dots loading-sm text-primary"></span>
      <span class="text-xs text-base-content/40">Pensando...</span>
    </div>
  </div>
</template>
```

### 3.4 ChatInput.vue

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useChat } from '@/composables/useChat'

const props = defineProps<{ disabled: boolean }>()
const { sendMessage } = useChat()
const inputText = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

async function handleSend() {
  if (!inputText.value.trim() || props.disabled) return
  const text = inputText.value
  inputText.value = ''
  if (textareaRef.value) textareaRef.value.style.height = 'auto'
  await sendMessage(text)
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

function autoResize(e: Event) {
  const target = e.target as HTMLTextAreaElement
  target.style.height = 'auto'
  target.style.height = Math.min(target.scrollHeight, 120) + 'px'
}
</script>

<template>
  <div class="border-t border-base-300 px-4 py-3">
    <div class="flex items-end gap-2">
      <textarea ref="textareaRef" v-model="inputText"
        @keydown="handleKeydown" @input="autoResize" :disabled="disabled"
        placeholder="Escribe un mensaje..." rows="1"
        class="textarea textarea-bordered flex-1 resize-none text-sm leading-5
               min-h-[40px] max-h-[120px] focus:outline-none focus:border-primary" />
      <button @click="handleSend" :disabled="!inputText.trim() || disabled"
              class="btn btn-primary btn-sm h-10 w-10 p-0 flex-shrink-0">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
             stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round"
                d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
        </svg>
      </button>
    </div>
    <p class="text-[10px] text-base-content/30 mt-1 text-center">
      Enter para enviar, Shift+Enter para nueva línea
    </p>
  </div>
</template>
```

### 3.5 Message Components

#### `messages/UserMessage.vue`

```vue
<script setup lang="ts">
import type { ChatMessage } from '@/types/chat'
defineProps<{ message: ChatMessage }>()
</script>

<template>
  <div class="flex justify-end">
    <div class="bg-primary text-primary-content rounded-2xl rounded-br-md
                px-4 py-2 max-w-[85%] text-sm whitespace-pre-wrap">
      {{ message.content }}
    </div>
  </div>
</template>
```

#### `messages/AssistantMessage.vue`

```vue
<script setup lang="ts">
import type { ChatMessage } from '@/types/chat'
defineProps<{ message: ChatMessage }>()
</script>

<template>
  <div class="flex justify-start">
    <div class="bg-base-200 rounded-2xl rounded-bl-md
                px-4 py-2 max-w-[85%] text-sm whitespace-pre-wrap">
      <span v-if="message.content">{{ message.content }}</span>
      <span v-if="message.isStreaming && !message.content" class="loading loading-dots loading-xs"></span>
    </div>
  </div>
</template>
```

#### `messages/AudioMessage.vue`

```vue
<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ audioUrl: string; duration?: number; audioId?: number }>()

const audioRef = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const progress = ref(0)

function togglePlay() {
  if (!audioRef.value) return
  if (isPlaying.value) audioRef.value.pause()
  else audioRef.value.play()
  isPlaying.value = !isPlaying.value
}

function onTimeUpdate() {
  if (audioRef.value && audioRef.value.duration)
    progress.value = (audioRef.value.currentTime / audioRef.value.duration) * 100
}

function onEnded() { isPlaying.value = false; progress.value = 0 }

function formatDuration(s?: number): string {
  if (!s) return '0:00'
  return `${Math.floor(s / 60)}:${Math.floor(s % 60).toString().padStart(2, '0')}`
}
</script>

<template>
  <div class="flex justify-start">
    <div class="bg-base-200 rounded-2xl px-4 py-3 max-w-[85%] flex items-center gap-3">
      <button @click="togglePlay" class="btn btn-circle btn-sm btn-primary">
        <svg v-if="!isPlaying" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="currentColor" class="w-4 h-4">
          <path fill-rule="evenodd"
                d="M4.5 5.653c0-1.427 1.529-2.33 2.779-1.643l11.54 6.347c1.295.712 1.295 2.573 0 3.286L7.28 19.99c-1.25.687-2.779-.217-2.779-1.643V5.653Z"
                clip-rule="evenodd" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="currentColor" class="w-4 h-4">
          <path fill-rule="evenodd"
                d="M6.75 5.25a.75.75 0 0 1 .75-.75H9a.75.75 0 0 1 .75.75v13.5a.75.75 0 0 1-.75.75H7.5a.75.75 0 0 1-.75-.75V5.25Zm7.5 0A.75.75 0 0 1 15 4.5h1.5a.75.75 0 0 1 .75.75v13.5a.75.75 0 0 1-.75.75H15a.75.75 0 0 1-.75-.75V5.25Z"
                clip-rule="evenodd" />
        </svg>
      </button>
      <div class="flex-1">
        <div class="w-full bg-base-300 rounded-full h-1.5">
          <div class="bg-primary h-1.5 rounded-full transition-all duration-100"
               :style="{ width: `${progress}%` }" />
        </div>
        <p class="text-[10px] text-base-content/40 mt-1">{{ formatDuration(duration) }}</p>
      </div>
      <audio ref="audioRef" :src="audioUrl" @timeupdate="onTimeUpdate"
             @ended="onEnded" preload="metadata" />
    </div>
  </div>
</template>
```

#### `messages/ToolStatus.vue`

```vue
<script setup lang="ts">
import { TOOL_DISPLAY_NAMES } from '@/types/chat'
const props = defineProps<{ toolName: string }>()
const displayName = TOOL_DISPLAY_NAMES[props.toolName] || props.toolName
</script>

<template>
  <div class="flex items-center gap-2 px-3 py-1.5 text-xs text-base-content/50">
    <span class="loading loading-spinner loading-xs text-primary"></span>
    <span>{{ displayName }}...</span>
  </div>
</template>
```

---

## Paso 4: Registrar ruta y navegación

### 4.1 Agregar ruta en `frontend/src/router/index.ts`

```typescript
{
  path: '/chat',
  name: 'chat',
  component: () => import('@/components/chat/ChatPage.vue'),
},
```

### 4.2 Agregar item en AppSidebar

Agregar un link a `/chat` en el sidebar, junto a las demás secciones (Campaigns, Library, Calendar, etc.).

---

## Verificación

### Checklist

- [ ] `npm run build` compila sin errores TypeScript
- [ ] `/chat` carga correctamente como página dedicada
- [ ] Link en sidebar navega a `/chat`
- [ ] Texto aparece **palabra por palabra** (streaming real)
- [ ] Tools muestran spinner con nombre (y cambia entre tools)
- [ ] Audio generado se reproduce inline
- [ ] Shift+Enter = nueva línea, Enter = enviar
- [ ] Auto-scroll funciona sin jank
- [ ] "Nueva conversación" limpia mensajes
- [ ] Dropdown de conversaciones recientes funciona
- [ ] Audios previos se reproducen al recargar conversación

### Test E2E

1. Navegar a `/chat` desde el sidebar
2. Escribir: "Necesito un anuncio para una oferta de pizzas 2x1"
3. Verificar texto progresivo + sugerencias
4. Responder: "Me gusta la primera, genera el audio"
5. Verificar spinner "Generando audio..." → player inline
6. Responder: "Guárdalo en la biblioteca"
7. Click "Nueva conversación", verificar limpieza
8. Abrir dropdown de conversaciones, cargar la anterior → audios reproducibles

---

## Notas

1. **Vite proxy**: `/api` ya está proxeado a `localhost:3001` en `vite.config.ts`. Vite no bufferea por defecto.

2. **Markdown**: Si Claude responde con markdown, considerar `marked` (librería liviana) o dejar como texto plano.

3. **Historial de conversaciones**: `loadConversations()` y `loadConversation(id)` están listos. Un drawer lateral en ChatPanel es opcional para v1.

4. **@microsoft/fetch-event-source**: Alternativa opcional al parser manual. Instalar con `npm install @microsoft/fetch-event-source` y reemplazar el bloque fetch en useChat.ts:
   ```typescript
   import { fetchEventSource } from '@microsoft/fetch-event-source'
   await fetchEventSource('/api/v1/chat/send', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ message, conversation_id }),
     onmessage(ev) { handleSSEEvent(JSON.parse(ev.data), assistantMsg) },
     onerror(err) { error.value = 'Error de conexión'; throw err },
   })
   ```

---

## Anexo: Revisión contra codebase real (2026-02-27)

Revisión del documento contra el código frontend existente. Se verificaron App.vue, apiClient, Vite config, composables, tipos, componentes, Tailwind/DaisyUI, router, env vars y package.json.

### Lo que está correcto

- Estructura `components/chat/` con subdirectorio `messages/` sigue el patrón existente (`campaigns/components/`, `library/components/`).
- Composable singleton (refs fuera de la función) es el mismo patrón que `useLayout.ts`.
- `chat.ts` en `types/` sigue convención de los existentes (`audio.ts`, `campaign.ts`).
- `apiClient.get()` retorna data directamente — uso en `loadConversations`/`loadConversation` es correcto.
- Todas las clases DaisyUI usadas son válidas en v4.4 (versión del proyecto).
- Proxy Vite para `/api` → `localhost:3001` ya existe. SSE funciona sin config adicional.
- `isLandingPage` existe en App.vue como `computed(() => route.path === '/landing')`.

### Decisión de diseño: Ruta dedicada vs widget flotante

Se decidió usar **ruta dedicada `/chat`** en vez del widget flotante original. Razones:
- El chat es un workflow core, no soporte secundario — necesita espacio completo
- Más simple de implementar (componente en router, sin z-index/overlay)
- Se agrega como sección en el sidebar junto a Campaigns, Library, etc.
- Los componentes internos (`ChatMessages`, `ChatInput`, `messages/*`, `useChat.ts`) son reutilizables si se quiere un widget flotante en el futuro

Se eliminaron del composable: `isOpen`, `toggleChat`, `openChat`, `closeChat`.
Se eliminaron componentes: `ChatWidget.vue`, `ChatToggleButton.vue`, `ChatPanel.vue`.
Se agregó: `ChatPage.vue` (página completa), ruta en router, link en sidebar.

### Problemas a corregir

#### P1: `VITE_API_URL` en fetch — Simplificar
No existe archivo `.env` en el proyecto. `VITE_API_URL` nunca está definido. El fallback `|| ''` funciona, pero es innecesario. Usar directamente `'/api/v1/chat/send'` que funciona igual con proxy Vite y Nginx.

#### P2: ToolStatus.vue — Bug: `displayName` no es reactivo
```typescript
// ACTUAL (bug):
const displayName = TOOL_DISPLAY_NAMES[props.toolName] || props.toolName

// CORRECTO:
const displayName = computed(() => TOOL_DISPLAY_NAMES[props.toolName] || props.toolName)
```
Sin `computed`, cuando el assistant ejecuta múltiples tools secuenciales, el nombre queda congelado en el primer tool. **Este es un bug real.**

#### P3: Auto-scroll — `{ deep: true }` causa jank durante streaming
```typescript
watch(
  () => [props.messages.length, props.messages[props.messages.length - 1]?.content],
  ...
  { deep: true }  // ← Se ejecuta en CADA carácter de text_delta
)
```
El watch source ya es explícito (`.length` y `.content`), así que `deep` es redundante. Remover `{ deep: true }` o reemplazar por debounce/throttle. Sin esto, el scroll se ejecuta cientos de veces por segundo durante streaming.

#### P4: SVGs inline en vez de librerías instaladas
El proyecto tiene `lucide-vue-next` (v0.562) y `@heroicons/vue` (v2.2) instalados. Los componentes del documento usan SVGs hardcodeados. Funciona pero es inconsistente y hace componentes más largos. Usar:
```typescript
import { MessageSquare, Plus, X, Play, Pause, Send, Sparkles } from 'lucide-vue-next'
```

### Mejoras recomendadas

1. **Markdown rendering** — Claude responde frecuentemente con markdown (listas numeradas, negritas). `AssistantMessage.vue` usa `whitespace-pre-wrap` (texto plano). Considerar `marked` + `DOMPurify` como requisito, no opcional.

2. **AbortController** — Si el usuario navega fuera de `/chat` o inicia nueva conversación durante streaming, el fetch sigue corriendo. Agregar `AbortController` y cancelar en `startNewConversation()` y en `onUnmounted`.

3. **Reconciliación de IDs** — Mensajes optimistas usan `id: string` (`user_${Date.now()}`), los de DB son `number`. No hay reconciliación post-stream. Si se busca por ID con `===`, la comparación `string === number` falla.

4. **Sin reconexión SSE** — Si la red se corta durante streaming, el mensaje queda incompleto sin retry. Aceptable para v1, pero documentar como limitación.
