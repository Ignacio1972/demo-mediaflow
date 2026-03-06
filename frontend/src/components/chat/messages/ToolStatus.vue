<script setup lang="ts">
import { computed } from 'vue'
import { TOOL_DISPLAY_NAMES } from '@/types/chat'

const props = defineProps<{ toolName: string }>()

const displayName = computed(() => TOOL_DISPLAY_NAMES[props.toolName] || props.toolName)
</script>

<template>
  <div class="flex items-center gap-2 px-3 py-1.5 text-xs text-base-content/50">
    <span class="loading loading-spinner loading-xs text-primary"></span>
    <span>{{ displayName }}...</span>
  </div>
</template>
