<template>
  <div class="relative" ref="containerRef">
    <button
      class="badge gap-1 cursor-pointer hover:opacity-80 transition-opacity"
      :style="badgeStyle"
      @click.stop="toggleDropdown"
    >
      <span>{{ category?.icon || '📁' }}</span>
      <span>{{ category?.name || 'Sin categoria' }}</span>
      <ChevronDownIcon class="h-3 w-3" />
    </button>

    <!-- Dropdown -->
    <Transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        class="absolute z-50 mt-1 w-48 bg-base-100 rounded-lg shadow-lg border border-base-300 py-1"
      >
        <button
          v-for="cat in categories"
          :key="cat.id"
          class="w-full px-3 py-2 text-left hover:bg-base-200 flex items-center gap-2 text-sm"
          :class="{ 'bg-base-200': cat.id === categoryId }"
          @click="selectCategory(cat.id)"
        >
          <span :style="{ color: cat.color }">{{ cat.icon }}</span>
          <span class="flex-1">{{ cat.name }}</span>
          <CheckIcon v-if="cat.id === categoryId" class="h-4 w-4 text-success" />
        </button>

        <div class="border-t border-base-300 my-1"></div>

        <button
          class="w-full px-3 py-2 text-left hover:bg-base-200 flex items-center gap-2 text-sm"
          :class="{ 'bg-base-200': !categoryId }"
          @click="selectCategory(null)"
        >
          <span>📁</span>
          <span class="flex-1">Sin categoria</span>
          <CheckIcon v-if="!categoryId" class="h-4 w-4 text-success" />
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { ChevronDownIcon, CheckIcon } from '@heroicons/vue/24/outline'
import type { Category } from '@/types/audio'

const props = defineProps<{
  categoryId: string | null | undefined
  categories: Category[]
}>()

const emit = defineEmits<{
  change: [categoryId: string | null]
}>()

const containerRef = ref<HTMLElement | null>(null)
const isOpen = ref(false)

const category = computed(() =>
  props.categories.find(c => c.id === props.categoryId)
)

const badgeStyle = computed(() => ({
  backgroundColor: category.value?.color
    ? `${category.value.color}20`
    : 'oklch(var(--b2))',
  color: category.value?.color || 'currentColor',
  borderColor: category.value?.color || 'transparent'
}))

function toggleDropdown() {
  isOpen.value = !isOpen.value
}

function selectCategory(id: string | null) {
  emit('change', id)
  isOpen.value = false
}

onClickOutside(containerRef, () => {
  isOpen.value = false
})
</script>
