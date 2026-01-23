<template>
  <div
    class="p-3 rounded-lg cursor-pointer transition-all border-2"
    :class="cardClass"
    :style="cardStyle"
  >
    <div class="flex items-center gap-3">
      <!-- Icon -->
      <div
        class="w-10 h-10 rounded-lg flex items-center justify-center text-xl"
        :style="iconStyle"
      >
        {{ shortcut.custom_icon || '⚡' }}
      </div>

      <!-- Info -->
      <div class="flex-1 min-w-0">
        <div class="font-medium truncate">{{ shortcut.custom_name }}</div>
        <div class="text-xs text-base-content/50 truncate">
          {{ shortcut.audio_message?.display_name || 'Sin audio' }}
        </div>
      </div>

      <!-- Position Badge -->
      <div v-if="shortcut.position" class="badge badge-primary badge-sm">
        {{ shortcut.position }}
      </div>
      <div v-else class="badge badge-ghost badge-sm">
        —
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Shortcut } from '@/types/shortcut'

const props = defineProps<{
  shortcut: Shortcut
  isSelected: boolean
}>()

const cardClass = computed(() => ({
  'border-primary bg-primary/5': props.isSelected,
  'border-transparent hover:border-base-300 hover:bg-base-200': !props.isSelected,
}))

const cardStyle = computed(() => {
  if (props.isSelected && props.shortcut.custom_color) {
    return {
      borderColor: props.shortcut.custom_color,
      backgroundColor: `${props.shortcut.custom_color}10`,
    }
  }
  return {}
})

const iconStyle = computed(() => {
  const color = props.shortcut.custom_color || '#10B981'
  return {
    backgroundColor: `${color}20`,
  }
})
</script>
