<template>
  <div
    v-if="shortcut"
    class="group relative bg-base-100 border-2 rounded-xl md:rounded-2xl cursor-pointer transition-all duration-300 overflow-hidden border-base-300 hover:border-primary/50 hover:shadow-xl hover:-translate-y-1"
    @click="$emit('click')"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <!-- Gradient Background -->
    <div
      class="absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity duration-300"
      :class="gradientColor"
    ></div>

    <!-- Content -->
    <div class="relative p-4 md:p-8 flex flex-col items-center text-center">
      <!-- Icon Container -->
      <div class="relative mb-2 md:mb-5">
        <div
          class="flex items-center justify-center w-12 h-12 md:w-20 md:h-20 rounded-xl md:rounded-2xl transition-all duration-300 group-hover:scale-110 group-hover:shadow-lg"
          style="background-color: #0171dc15;"
        >
          <DynamicIcon
            :name="shortcut.custom_icon || null"
            fallback="Megaphone"
            class="w-6 h-6 md:w-10 md:h-10 transition-transform duration-300 group-hover:scale-110"
          />
        </div>
      </div>

      <!-- Name -->
      <h3 class="font-semibold text-xs md:text-base leading-tight mb-0.5 md:mb-1 line-clamp-2">
        {{ shortcut.custom_name }}
      </h3>
    </div>

    <!-- Hover indicator line -->
    <div
      class="absolute bottom-0 left-1/2 -translate-x-1/2 h-1 bg-primary rounded-t-full transition-all duration-300"
      :class="isHovered ? 'w-12 opacity-100' : 'w-0 opacity-0'"
    ></div>
  </div>

  <!-- Empty Slot -->
  <div
    v-else
    class="flex flex-col items-center justify-center min-h-[100px] md:min-h-[180px] border-2 border-dashed border-base-300 rounded-xl md:rounded-2xl opacity-40"
  >
    <span class="text-2xl md:text-3xl opacity-30">{{ position }}</span>
    <span class="text-xs opacity-40 mt-1">Vacío</span>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ShortcutPublic } from '@/types/shortcut'
import DynamicIcon from '@/components/shared/ui/DynamicIcon.vue'

const props = defineProps<{
  shortcut?: ShortcutPublic
  position: number
}>()

defineEmits<{
  click: []
}>()

const isHovered = ref(false)

const gradientColor = computed(() => {
  const colors = [
    'from-blue-500/10 to-cyan-500/5',
    'from-blue-500/10 to-cyan-500/5',
  ]
  if (!props.shortcut) return colors[0]
  const hash = props.shortcut.custom_name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return colors[hash % colors.length]
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
