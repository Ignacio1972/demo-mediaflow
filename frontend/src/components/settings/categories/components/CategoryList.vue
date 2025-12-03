<template>
  <div class="category-list">
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body p-4">
        <h2 class="card-title text-lg mb-4">
          Categorías
          <span class="badge badge-neutral">{{ categories.length }}</span>
        </h2>

        <!-- Loading State -->
        <div v-if="isLoading" class="flex justify-center py-8">
          <span class="loading loading-spinner loading-lg text-primary"></span>
        </div>

        <!-- Empty State -->
        <div v-else-if="categories.length === 0" class="text-center py-8">
          <div class="text-4xl mb-2">📁</div>
          <p class="text-base-content/50">No hay categorías</p>
          <p class="text-sm text-base-content/40">Crea una nueva para comenzar</p>
        </div>

        <!-- Category List -->
        <div v-else class="space-y-2">
          <TransitionGroup name="list">
            <CategoryCard
              v-for="category in categories"
              :key="category.id"
              :category="category"
              :is-selected="selectedCategory?.id === category.id"
              @click="emit('select', category)"
              @drag-start="handleDragStart(category, $event)"
              @drag-over="handleDragOver"
              @drop="handleDrop(category)"
              @drag-end="handleDragEnd"
              draggable="true"
            />
          </TransitionGroup>
        </div>

        <!-- Drag hint -->
        <p v-if="categories.length > 1" class="text-xs text-base-content/40 mt-4 text-center">
          Arrastra para reordenar
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Category } from '../composables/useCategoryEditor'
import CategoryCard from './CategoryCard.vue'

const props = defineProps<{
  categories: Category[]
  selectedCategory: Category | null
  isLoading: boolean
}>()

const emit = defineEmits<{
  select: [category: Category]
  reorder: [newOrder: string[]]
}>()

// Drag and drop state
const draggedCategory = ref<Category | null>(null)
const dragOverCategory = ref<Category | null>(null)

const handleDragStart = (category: Category, event: DragEvent) => {
  draggedCategory.value = category
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', category.id)
  }
}

const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
}

const handleDrop = (targetCategory: Category) => {
  if (!draggedCategory.value || draggedCategory.value.id === targetCategory.id) {
    return
  }

  // Calculate new order
  const currentOrder = props.categories.map(c => c.id)
  const draggedIndex = currentOrder.indexOf(draggedCategory.value.id)
  const targetIndex = currentOrder.indexOf(targetCategory.id)

  // Remove dragged item and insert at target position
  currentOrder.splice(draggedIndex, 1)
  currentOrder.splice(targetIndex, 0, draggedCategory.value.id)

  emit('reorder', currentOrder)
}

const handleDragEnd = () => {
  draggedCategory.value = null
  dragOverCategory.value = null
}
</script>

<style scoped>
.list-move {
  transition: transform 0.3s ease;
}

.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
