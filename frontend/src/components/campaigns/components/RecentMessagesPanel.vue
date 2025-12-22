<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { CollapsiblePanel } from '@/components/shared/ui'
import { useAudioStore } from '@/stores/audio'
import type { AudioMessage } from '@/types/audio'

const props = defineProps<{
  campaignId: string
}>()

const emit = defineEmits<{
  select: [message: AudioMessage]
}>()

// Use global audio store (same as Dashboard)
const audioStore = useAudioStore()
const { recentMessages, isLoading } = storeToRefs(audioStore)

// Load messages on mount if empty
onMounted(async () => {
  if (recentMessages.value.length === 0) {
    await audioStore.loadRecentMessages()
  }
})

// Filter by campaign and limit to 5 messages for the panel
const messages = computed(() =>
  recentMessages.value
    .filter(m => m.category_id === props.campaignId)
    .slice(0, 5)
)

// Preview text for collapsed state
const previewText = computed(() =>
  messages.value.length > 0
    ? `${messages.value.length} mensajes`
    : 'Sin mensajes'
)

// Audio player state
const currentlyPlaying = ref<number | null>(null)
const audioElement = ref<HTMLAudioElement | null>(null)

function togglePlay(message: AudioMessage) {
  if (currentlyPlaying.value === message.id) {
    audioElement.value?.pause()
    currentlyPlaying.value = null
  } else {
    if (audioElement.value) {
      audioElement.value.pause()
    }
    const url = message.audio_url || `/api/v1/audio/file/${message.filename}`
    audioElement.value = new Audio(url)
    audioElement.value.play()
    audioElement.value.onended = () => {
      currentlyPlaying.value = null
    }
    currentlyPlaying.value = message.id
  }
}

function selectMessage(message: AudioMessage) {
  emit('select', message)
}

// Cleanup on unmount
onUnmounted(() => {
  if (audioElement.value) {
    audioElement.value.pause()
    audioElement.value = null
  }
})
</script>

<template>
  <CollapsiblePanel
    title="Mensajes Recientes"
    icon="📋"
    :preview="previewText"
    :default-expanded="false"
  >
    <div class="space-y-2">
      <!-- Loading -->
      <div v-if="isLoading" class="flex justify-center py-4">
        <span class="loading loading-spinner loading-sm"></span>
      </div>

      <!-- Empty -->
      <div v-else-if="messages.length === 0" class="text-center py-4 opacity-50">
        Sin mensajes aun
      </div>

      <!-- List -->
      <div
        v-else
        v-for="message in messages"
        :key="message.id"
        class="card card-compact bg-base-300 cursor-pointer hover:bg-base-200 transition-colors"
        @click="selectMessage(message)"
      >
        <div class="card-body flex-row items-center gap-2">
          <!-- Play button -->
          <button
            class="btn btn-circle btn-xs btn-ghost"
            @click.stop="togglePlay(message)"
          >
            <span v-if="currentlyPlaying === message.id">⏸</span>
            <span v-else>▶</span>
          </button>

          <!-- Info -->
          <div class="flex-1 min-w-0">
            <p class="font-medium truncate text-sm">
              {{ message.display_name }}
            </p>
            <p class="text-xs opacity-50 truncate">
              {{ message.original_text?.slice(0, 40) }}{{ message.original_text && message.original_text.length > 40 ? '...' : '' }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </CollapsiblePanel>
</template>
