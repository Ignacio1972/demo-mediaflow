<template>
  <div
    class="category-card cursor-pointer select-none transition-all duration-200"
    :class="{
      'ring-2 ring-primary shadow-lg': isSelected,
      'hover:shadow-md': !isSelected,
      'opacity-50': !category.active,
      'dragging': isDragging,
    }"
    @click="emit('click')"
  >
    <div class="flex items-center gap-3 p-3 rounded-lg bg-base-200 hover:bg-base-300">
      <!-- Drag Handle -->
      <div class="cursor-grab active:cursor-grabbing text-base-content/30 hover:text-base-content/60">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
        </svg>
      </div>

      <!-- Color & Icon -->
      <div
        class="w-10 h-10 rounded-lg flex items-center justify-center text-xl flex-shrink-0"
        :style="{ backgroundColor: category.color || '#6B7280' }"
      >
        {{ category.icon || '📁' }}
      </div>

      <!-- Info -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <h3 class="font-medium text-sm truncate">{{ category.name }}</h3>
          <span
            v-if="!category.active"
            class="badge badge-xs badge-ghost"
          >
            Inactiva
          </span>
        </div>
        <p class="text-xs text-base-content/50 mt-0.5">
          {{ category.message_count || 0 }} mensajes
        </p>
      </div>

      <!-- Selected Indicator -->
      <div v-if="isSelected" class="text-primary">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Category } from '../composables/useCategoryEditor'

defineProps<{
  category: Category
  isSelected: boolean
}>()

const emit = defineEmits<{
  click: []
}>()

const isDragging = ref(false)
</script>

<style scoped>
.category-card.dragging {
  opacity: 0.5;
  transform: scale(0.95);
}

.category-card:active {
  transform: scale(0.98);
}
</style>
