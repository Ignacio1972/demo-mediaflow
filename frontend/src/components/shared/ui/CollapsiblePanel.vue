<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  title: string
  icon?: string
  defaultExpanded?: boolean
  preview?: string
}

const props = withDefaults(defineProps<Props>(), {
  defaultExpanded: false
})

const isExpanded = ref(props.defaultExpanded)

function toggle() {
  isExpanded.value = !isExpanded.value
}

const displayTitle = computed(() => {
  return props.icon ? `${props.icon} ${props.title}` : props.title
})
</script>

<template>
  <div class="collapsible-panel bg-base-200 rounded-lg overflow-hidden">
    <!-- Header (always visible) -->
    <button
      class="w-full flex items-center justify-between p-4 hover:bg-base-300 transition-colors text-left"
      @click="toggle"
    >
      <div class="flex items-center gap-2">
        <!-- Expand/Collapse indicator -->
        <span class="transition-transform duration-200" :class="{ 'rotate-90': isExpanded }">
          ▶
        </span>
        <!-- Title -->
        <span class="font-medium">{{ displayTitle }}</span>
      </div>

      <!-- Preview text when collapsed -->
      <span
        v-if="!isExpanded && preview"
        class="text-sm opacity-60 truncate max-w-[200px]"
      >
        {{ preview }}
      </span>
    </button>

    <!-- Content (expandable) -->
    <div
      class="transition-all duration-300 ease-in-out overflow-hidden"
      :class="isExpanded ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'"
    >
      <div class="p-4 pt-0 border-t border-base-300">
        <slot />
      </div>
    </div>
  </div>
</template>

<style scoped>
.collapsible-panel {
  border: 1px solid hsl(var(--b3));
}
</style>
