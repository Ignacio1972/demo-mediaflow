<template>
  <div class="recent-messages h-full flex flex-col">
    <div class="card bg-base-200 shadow-xl h-full flex flex-col overflow-hidden">
      <div class="card-body p-4 sm:p-6 flex flex-col overflow-hidden">
        <div class="flex items-center justify-between flex-shrink-0">
          <h3 class="card-title text-lg sm:text-xl">Mensajes Recientes</h3>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading && messages.length === 0" class="flex justify-center py-8">
          <span class="loading loading-spinner loading-lg text-primary"></span>
        </div>

        <!-- Empty State -->
        <div v-else-if="messages.length === 0" class="text-center py-8 opacity-70">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
          <p>No hay mensajes recientes</p>
          <p class="text-sm mt-2">Genera tu primer mensaje arriba</p>
        </div>

        <!-- Messages List with Scroll -->
        <div v-else class="messages-container flex-1 min-w-0 overflow-y-auto overflow-x-hidden pr-1">
          <div class="space-y-3">
            <div
              v-for="message in messages"
              :key="message.id"
              :ref="el => setMessageRef(message.id, el)"
              class="message-card card bg-base-300 hover:bg-base-100 transition-all"
            >
              <div class="card-body p-4">
                <!-- Title -->
                <h4 class="font-semibold text-sm truncate">
                  {{ message.display_name }}
                </h4>

                <!-- Text Preview -->
                <p class="text-sm opacity-80 line-clamp-4 leading-relaxed">
                  {{ message.original_text }}
                </p>

                <!-- Metadata -->
                <div class="flex items-center gap-2 text-xs opacity-60 mt-1">
                  <span class="truncate max-w-[80px] sm:max-w-[100px]">{{ message.voice_id }}</span>
                  <span>·</span>
                  <span>{{ formatDuration(message.duration) }}</span>
                  <span>·</span>
                  <span>{{ formatTimeAgo(message.created_at) }}</span>
                </div>

                <!-- Action Buttons -->
                <div class="flex items-center justify-end gap-3 mt-3 pt-3 border-t border-base-content/10">
                  <!-- Play Button -->
                  <button
                    @click="playAudio(message)"
                    class="btn btn-sm"
                    :class="currentPlayingId === message.id ? 'btn-primary' : 'btn-ghost'"
                    title="Reproducir"
                  >
                    <svg v-if="currentPlayingId === message.id" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </button>

                  <!-- Save Button -->
                  <button
                    @click="saveToLibrary(message)"
                    class="btn btn-sm btn-ghost"
                    :class="{ 'btn-disabled text-success': message.is_favorite }"
                    :disabled="message.is_favorite"
                    :title="message.is_favorite ? 'Ya guardado' : 'Guardar en biblioteca'"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </button>

                  <!-- Delete Button -->
                  <button
                    @click="deleteMessage(message)"
                    class="btn btn-sm btn-ghost hover:btn-error"
                    title="Eliminar"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Hidden Audio Player -->
        <audio
          ref="audioPlayer"
          @ended="currentPlayingId = null"
          @pause="currentPlayingId = null"
        ></audio>
      </div>
    </div>

    <!-- Toast Notification -->
    <div class="toast toast-end toast-bottom z-50">
      <Transition name="toast">
        <div v-if="showToast" class="alert alert-success">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Mensaje guardado exitosamente</span>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAudioStore } from '@/stores/audio'
import { storeToRefs } from 'pinia'
import type { AudioMessage } from '@/types/audio'

// Store
const audioStore = useAudioStore()
const { recentMessages: messages, isLoading } = storeToRefs(audioStore)

// State
const audioPlayer = ref<HTMLAudioElement | null>(null)
const currentPlayingId = ref<number | null>(null)
const messageRefs = ref<Map<number, HTMLElement>>(new Map())
const showToast = ref(false)

// Set message element reference
const setMessageRef = (id: number, el: any) => {
  if (el) {
    messageRefs.value.set(id, el as HTMLElement)
  }
}

// Show toast notification
const showSuccessToast = () => {
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// Methods
const formatDuration = (seconds?: number): string => {
  if (!seconds) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatTimeAgo = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'Ahora'
  if (diffMins < 60) return `Hace ${diffMins}m`

  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `Hace ${diffHours}h`

  const diffDays = Math.floor(diffHours / 24)
  return `Hace ${diffDays}d`
}

const playAudio = (message: AudioMessage) => {
  if (!audioPlayer.value) return

  // If same message, toggle play/pause
  if (currentPlayingId.value === message.id) {
    if (audioPlayer.value.paused) {
      audioPlayer.value.play()
      currentPlayingId.value = message.id
    } else {
      audioPlayer.value.pause()
      currentPlayingId.value = null
    }
    return
  }

  // Play new message
  audioPlayer.value.src = message.audio_url
  audioPlayer.value.play()
  currentPlayingId.value = message.id
}

const saveToLibrary = async (message: AudioMessage) => {
  const messageEl = messageRefs.value.get(message.id)

  try {
    await audioStore.saveToLibrary(message.id)

    // Slide-out animation to the right
    if (messageEl) {
      messageEl.style.transition = 'transform 0.4s ease, opacity 0.4s ease'
      messageEl.style.transform = 'translateX(100%)'
      messageEl.style.opacity = '0'

      // After animation, remove from list and show toast
      setTimeout(() => {
        // Remove message from local list (it's now in library)
        const index = messages.value.findIndex(m => m.id === message.id)
        if (index !== -1) {
          messages.value.splice(index, 1)
        }
        messageRefs.value.delete(message.id)
        // Show success toast
        showSuccessToast()
      }, 400)
    } else {
      // Fallback if no element ref
      const index = messages.value.findIndex(m => m.id === message.id)
      if (index !== -1) {
        messages.value.splice(index, 1)
      }
      showSuccessToast()
    }
  } catch (e: any) {
    console.error('Error al guardar en biblioteca:', e)
    // Reset styles on error
    if (messageEl) {
      messageEl.style.transition = ''
      messageEl.style.transform = ''
      messageEl.style.opacity = ''
    }
  }
}

const deleteMessage = async (message: AudioMessage) => {
  const messageEl = messageRefs.value.get(message.id)

  try {
    // Delete from store FIRST (API call)
    await audioStore.deleteMessage(message.id)

    // Only animate if API call succeeded
    if (messageEl) {
      messageEl.style.transition = 'transform 0.3s ease, opacity 0.3s ease'
      messageEl.style.transform = 'translateX(-100%)'
      messageEl.style.opacity = '0'

      // After animation, clean up refs
      setTimeout(() => {
        messageRefs.value.delete(message.id)
      }, 300)
    } else {
      messageRefs.value.delete(message.id)
    }
  } catch (e: any) {
    console.error('Error al eliminar mensaje:', e)
    // Reset styles on error (in case animation started somehow)
    if (messageEl) {
      messageEl.style.transition = ''
      messageEl.style.transform = ''
      messageEl.style.opacity = ''
    }
  }
}

// Load recent messages on mount
onMounted(async () => {
  if (messages.value.length === 0) {
    await audioStore.loadRecentMessages()
  }
})
</script>

<style scoped>
.recent-messages {
  width: 100%;
  min-height: auto;
}

@media (min-width: 1024px) {
  .recent-messages {
    min-height: 600px;
  }
}

.messages-container {
  max-height: calc(100vh - 250px);
  min-height: 300px;
  scrollbar-width: thin;
  scrollbar-color: oklch(var(--bc) / 0.2) transparent;
}

.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: transparent;
}

.messages-container::-webkit-scrollbar-thumb {
  background-color: oklch(var(--bc) / 0.2);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background-color: oklch(var(--bc) / 0.3);
}

.message-card {
  transform: translateX(0);
  opacity: 1;
}

/* Toast animation */
.toast-enter-active {
  animation: toast-in 0.3s ease-out;
}

.toast-leave-active {
  animation: toast-out 0.3s ease-in;
}

@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes toast-out {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(100%);
  }
}
</style>
