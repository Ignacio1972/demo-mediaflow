<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
    <MessageCard
      v-for="message in messages"
      :key="message.id"
      :message="message"
      :categories="categories"
      :selection-mode="selectionMode"
      :is-selected="isSelected(message.id)"
      :is-playing="isMessagePlaying(message.id)"
      @play="emit('play', $event)"
      @toggle-favorite="emit('toggle-favorite', $event)"
      @toggle-select="emit('toggle-select', $event)"
      @update-category="(id, catId) => emit('update-category', id, catId)"
      @action="(action, msg) => emit('action', action, msg)"
    />
  </div>
</template>

<script setup lang="ts">
import type { AudioMessage, Category } from '@/types/audio'
import type { MessageAction } from '../types/library.types'
import MessageCard from './MessageCard.vue'

defineProps<{
  messages: AudioMessage[]
  categories: Category[]
  selectionMode: boolean
  isSelected: (id: number) => boolean
  isMessagePlaying: (id: number) => boolean
}>()

const emit = defineEmits<{
  'play': [message: AudioMessage]
  'toggle-favorite': [id: number]
  'toggle-select': [id: number]
  'update-category': [id: number, categoryId: string | null]
  'action': [action: MessageAction, message: AudioMessage]
}>()
</script>
