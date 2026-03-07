<script setup lang="ts">
import type { ChatMessage } from '@/types/chat'

defineProps<{ message: ChatMessage }>()
</script>

<template>
  <div class="flex justify-end">
    <div class="bg-primary text-primary-content rounded-2xl rounded-br-md
                px-4 py-2 max-w-[85%] whitespace-pre-wrap">
      {{ message.content }}
    </div>
  </div>
</template>
