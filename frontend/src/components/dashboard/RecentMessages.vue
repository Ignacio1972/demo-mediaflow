<template>
  <div class="recent-messages">
    <div class="card bg-base-200 shadow-xl">
      <div class="card-body">
        <div class="flex items-center justify-between">
          <h3 class="card-title text-xl">
            📋 Mensajes Recientes
          </h3>
          <button
            @click="refresh"
            class="btn btn-ghost btn-sm btn-circle"
            :disabled="isLoading"
          >
            <span v-if="isLoading" class="loading loading-spinner loading-sm"></span>
            <span v-else>🔄</span>
          </button>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading && messages.length === 0" class="flex justify-center py-8">
          <span class="loading loading-spinner loading-lg text-primary"></span>
        </div>

        <!-- Empty State -->
        <div v-else-if="messages.length === 0" class="text-center py-8 opacity-70">
          <div class="text-6xl mb-4">🎙️</div>
          <p>No hay mensajes recientes</p>
          <p class="text-sm mt-2">Genera tu primer mensaje arriba</p>
        </div>

        <!-- Messages List -->
        <div v-else class="space-y-3">
          <div
            v-for="message in messages"
            :key="message.id"
            class="card bg-base-300 hover:bg-base-100 transition-all"
          >
            <div class="card-body p-4">
              <div class="flex items-start gap-3">
                <!-- Play Button -->
                <button
                  @click="playAudio(message)"
                  class="btn btn-circle btn-sm btn-primary"
                  :class="{ 'btn-ghost': currentPlayingId !== message.id }"
                >
                  <span v-if="currentPlayingId === message.id">⏸️</span>
                  <span v-else>▶️</span>
                </button>

                <!-- Message Info -->
                <div class="flex-1 min-w-0">
                  <h4 class="font-semibold truncate text-sm">
                    {{ message.display_name }}
                  </h4>

                  <!-- Message Text Preview (2 lines) -->
                  <p class="text-sm mt-1 line-clamp-2 leading-relaxed">
                    {{ message.original_text }}
                  </p>

                  <div class="flex items-center gap-2 text-xs opacity-70 mt-2">
                    <span>🎙️ {{ message.voice_id }}</span>
                    <span>•</span>
                    <span>{{ formatDuration(message.duration) }}</span>
                    <span>•</span>
                    <span>{{ formatTimeAgo(message.created_at) }}</span>
                  </div>
                </div>

                <!-- Quick Actions -->
                <div class="dropdown dropdown-end">
                  <label tabindex="0" class="btn btn-ghost btn-sm btn-circle">
                    ⋮
                  </label>
                  <ul
                    tabindex="0"
                    class="dropdown-content z-[1] menu p-2 shadow bg-base-200 rounded-box w-52"
                  >
                    <li>
                      <a @click="downloadMessage(message)">
                        ⬇️ Descargar
                      </a>
                    </li>
                    <li>
                      <a @click="copyUrl(message)">
                        🔗 Copiar URL
                      </a>
                    </li>
                    <li>
                      <a @click="viewInLibrary(message)">
                        📚 Ver en Library
                      </a>
                    </li>
                  </ul>
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

// Methods
const refresh = async () => {
  await audioStore.loadRecentMessages()
}

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

const downloadMessage = (message: AudioMessage) => {
  const link = document.createElement('a')
  link.href = message.audio_url
  link.download = message.filename
  link.click()
}

const copyUrl = async (message: AudioMessage) => {
  try {
    await navigator.clipboard.writeText(message.audio_url)
    alert('✅ URL copiada al portapapeles')
  } catch (e) {
    console.error('Failed to copy URL:', e)
  }
}

const viewInLibrary = (message: AudioMessage) => {
  // TODO: Navigate to library with filter (Semana 3)
  console.log('View in library:', message.id)
  alert('🚧 Función disponible en Semana 3 (Library)')
}

// Load recent messages on mount
onMounted(async () => {
  if (messages.value.length === 0) {
    await refresh()
  }
})
</script>

<style scoped>
.recent-messages {
  width: 100%;
}
</style>
