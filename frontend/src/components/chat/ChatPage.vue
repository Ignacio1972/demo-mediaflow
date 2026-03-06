<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useChat } from '@/composables/useChat'
import ChatHeader from './ChatHeader.vue'
import ChatMessages from './ChatMessages.vue'
import ChatInput from './ChatInput.vue'

const { messages, isSending, error, currentToolName, loadConversations, abortCurrentRequest, clearError } = useChat()

onMounted(() => {
  loadConversations()
})

onUnmounted(() => {
  abortCurrentRequest()
})
</script>

<template>
  <div class="flex flex-col h-[calc(100vh-7rem)] max-w-4xl mx-auto">
    <ChatHeader />

    <div v-if="error" class="px-4 py-2 bg-error/10 text-error text-sm flex items-center gap-2 rounded-lg mx-4 mt-2">
      <span class="flex-1">{{ error }}</span>
      <button @click="clearError" class="btn btn-ghost btn-xs">✕</button>
    </div>

    <ChatMessages
      :messages="messages"
      :is-sending="isSending"
      :current-tool="currentToolName"
      class="flex-1 overflow-y-auto"
    />

    <ChatInput :disabled="isSending" />
  </div>
</template>
