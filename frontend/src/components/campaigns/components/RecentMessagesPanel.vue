<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { CollapsiblePanel } from '@/components/shared/ui'
import type { CampaignAudio, CampaignAudiosResponse } from '@/types/campaign'
import { apiClient } from '@/api/client'

interface Props {
  campaignId: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  select: [message: CampaignAudio]
}>()

// State
const messages = ref<CampaignAudio[]>([])
const isLoading = ref(false)
const previewText = ref('')

// Load recent messages
async function loadMessages() {
  isLoading.value = true
  try {
    // apiClient returns data directly, NOT response.data
    const response = await apiClient.get<CampaignAudiosResponse>(
      `/api/v1/campaigns/${props.campaignId}/audios`,
      { params: { limit: 5 } }
    )
    messages.value = response.audios
    previewText.value = messages.value.length > 0
      ? `${messages.value.length} mensajes`
      : 'Sin mensajes'
  } catch (error) {
    console.error('Error loading recent messages:', error)
    previewText.value = 'Error al cargar'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadMessages()
})

// Audio player state
const currentlyPlaying = ref<number | null>(null)
const audioElement = ref<HTMLAudioElement | null>(null)

function getAudioUrl(message: CampaignAudio): string {
  // Build audio URL from filename
  return `/api/v1/audio/file/${message.filename}`
}

function togglePlay(message: CampaignAudio) {
  if (currentlyPlaying.value === message.id) {
    audioElement.value?.pause()
    currentlyPlaying.value = null
  } else {
    if (audioElement.value) {
      audioElement.value.pause()
    }
    audioElement.value = new Audio(getAudioUrl(message))
    audioElement.value.play()
    audioElement.value.onended = () => {
      currentlyPlaying.value = null
    }
    currentlyPlaying.value = message.id
  }
}

function selectMessage(message: CampaignAudio) {
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
