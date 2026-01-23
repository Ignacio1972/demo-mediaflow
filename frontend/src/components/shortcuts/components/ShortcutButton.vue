<template>
  <button
    v-if="shortcut"
    class="shortcut-button aspect-square rounded-2xl flex flex-col items-center justify-center text-center p-4 transition-all active:scale-95 hover:scale-[1.02] shadow-lg"
    :style="buttonStyle"
    @click="$emit('click')"
  >
    <span class="text-4xl md:text-5xl mb-2">{{ shortcut.custom_icon || '⚡' }}</span>
    <span class="text-sm md:text-base font-semibold truncate w-full px-2">
      {{ shortcut.custom_name }}
    </span>
  </button>

  <!-- Empty Slot -->
  <div
    v-else
    class="aspect-square rounded-2xl flex flex-col items-center justify-center text-center p-4 border-2 border-dashed border-base-300 bg-base-200/50 opacity-40"
  >
    <span class="text-2xl md:text-3xl opacity-30">{{ position }}</span>
    <span class="text-xs opacity-40 mt-1">Vacío</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ShortcutPublic } from '@/types/shortcut'

const props = defineProps<{
  shortcut?: ShortcutPublic
  position: number
}>()

defineEmits<{
  click: []
}>()

const buttonStyle = computed(() => {
  if (!props.shortcut) return {}

  const color = props.shortcut.custom_color || '#10B981'
  return {
    backgroundColor: `${color}20`,
    borderColor: `${color}50`,
    border: '2px solid',
    color: 'inherit',
  }
})
</script>

<style scoped>
.shortcut-button {
  min-height: 140px;
}

@media (min-width: 768px) {
  .shortcut-button {
    min-height: 160px;
  }
}
</style>
