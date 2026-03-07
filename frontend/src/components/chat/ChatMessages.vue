<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { Sparkles } from 'lucide-vue-next'
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

// P3 fix: no { deep: true } — explicit source is sufficient
watch(
  () => [props.messages.length, props.messages[props.messages.length - 1]?.content],
  async () => {
    await nextTick()
    if (scrollContainer.value) {
      scrollContainer.value.scrollTo({
        top: scrollContainer.value.scrollHeight,
        behavior: 'smooth',
      })
    }
  },
)
</script>

<template>
  <div ref="scrollContainer" class="px-2 sm:px-4 py-3 space-y-3">
    <!-- Welcome screen -->
    <div v-if="!messages.length" class="flex flex-col items-center justify-center h-full text-center py-12">
      <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
        <Sparkles class="w-8 h-8 text-primary" />
      </div>
      <h3 class="text-base font-semibold mb-1">Asistente MediaFlow</h3>
      <p class="text-sm text-base-content/50 max-w-[260px]">
        Describe lo que necesitas y te ayudo a crear anuncios de audio, programarlos y mas.
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

    <!-- Tool status -->
    <ToolStatus v-if="currentTool" :tool-name="currentTool" />

    <!-- Typing indicator -->
    <div v-if="isSending && messages[messages.length - 1]?.isStreaming && !messages[messages.length - 1]?.content && !currentTool"
         class="flex items-center gap-2 px-3 py-2">
      <span class="loading loading-dots loading-sm text-primary"></span>
      <span class="text-xs text-base-content/40">Pensando...</span>
    </div>
  </div>
</template>
