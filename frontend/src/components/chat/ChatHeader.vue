<script setup lang="ts">
import { Sparkles, Clock, Plus } from 'lucide-vue-next'
import { useChat } from '@/composables/useChat'

const { startNewConversation, conversationId, conversations, loadConversation } = useChat()
</script>

<template>
  <div class="flex items-center gap-3 px-4 py-3 border-b border-base-300">
    <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
      <Sparkles class="w-4 h-4 text-primary" />
    </div>
    <div class="flex-1">
      <h3 class="text-sm font-semibold">Asistente MediaFlow</h3>
      <p class="text-xs text-base-content/50">IA conversacional</p>
    </div>

    <!-- Recent conversations dropdown -->
    <div v-if="conversations.length" class="dropdown dropdown-end">
      <label tabindex="0" class="btn btn-ghost btn-xs" title="Conversaciones">
        <Clock class="w-4 h-4" />
      </label>
      <ul tabindex="0" class="dropdown-content z-10 menu p-2 shadow-lg bg-base-100
                              border border-base-300 rounded-box w-64 max-h-60 overflow-y-auto">
        <li v-for="conv in conversations" :key="conv.id">
          <a @click="loadConversation(conv.id)"
             :class="{ 'active': conv.id === conversationId }"
             class="text-xs truncate">
            {{ conv.title || 'Sin titulo' }}
          </a>
        </li>
      </ul>
    </div>

    <button v-if="conversationId" @click="startNewConversation"
            class="btn btn-ghost btn-xs" title="Nueva conversacion">
      <Plus class="w-4 h-4" />
    </button>
  </div>
</template>
