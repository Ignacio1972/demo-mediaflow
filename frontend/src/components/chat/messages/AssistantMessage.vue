<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import type { ChatMessage } from '@/types/chat'

const props = defineProps<{ message: ChatMessage }>()

// Configure marked for safe defaults
marked.setOptions({
  breaks: true,
  gfm: true,
})

const renderedContent = computed(() => {
  if (!props.message.content) return ''
  return marked.parse(props.message.content) as string
})
</script>

<template>
  <div class="flex justify-start">
    <div class="bg-base-200 rounded-2xl rounded-bl-md px-4 py-2 max-w-[85%]">
      <div v-if="message.content" class="chat-markdown" v-html="renderedContent" />
      <span v-if="message.isStreaming && !message.content"
            class="loading loading-dots loading-xs"></span>
    </div>
  </div>
</template>

<style scoped>
.chat-markdown :deep(p) {
  margin-bottom: 0.5em;
}
.chat-markdown :deep(p:last-child) {
  margin-bottom: 0;
}
.chat-markdown :deep(ol) {
  list-style: decimal;
  padding-left: 1.5em;
  margin-bottom: 0.5em;
}
.chat-markdown :deep(ul) {
  list-style: disc;
  padding-left: 1.5em;
  margin-bottom: 0.5em;
}
.chat-markdown :deep(li) {
  margin-bottom: 0.25em;
}
.chat-markdown :deep(strong) {
  font-weight: 600;
}
.chat-markdown :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 0.1em 0.3em;
  border-radius: 0.25em;
  font-size: 0.9em;
}
.chat-markdown :deep(pre) {
  background: rgba(0, 0, 0, 0.08);
  padding: 0.75em;
  border-radius: 0.5em;
  overflow-x: auto;
  margin-bottom: 0.5em;
}
.chat-markdown :deep(pre code) {
  background: none;
  padding: 0;
}
.chat-markdown :deep(blockquote) {
  border-left: 3px solid rgba(0, 0, 0, 0.2);
  padding-left: 0.75em;
  margin-left: 0;
  opacity: 0.8;
}
</style>
