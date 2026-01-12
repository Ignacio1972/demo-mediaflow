<script setup lang="ts">
import { ref, computed } from 'vue'
import DynamicIcon from '@/components/shared/ui/DynamicIcon.vue'

export interface Operation {
  id: string
  name: string
  description: string
  icon: string
  path: string
  available: boolean
}

interface Props {
  operation: Operation
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: [operation: Operation]
}>()

const isHovered = ref(false)

// Generate a subtle background gradient based on operation id
const gradientColor = computed(() => {
  const colors: Record<string, string> = {
    'vehicles': 'from-blue-500/10 to-cyan-500/5',
    'schedules': 'from-amber-500/10 to-orange-500/5',
    'lost-child': 'from-rose-500/10 to-pink-500/5',
    'employee-call': 'from-emerald-500/10 to-teal-500/5',
  }
  return colors[props.operation.id] || 'from-primary/10 to-primary/5'
})

function handleClick() {
  if (props.operation.available) {
    emit('click', props.operation)
  }
}
</script>

<template>
  <div
    class="group relative bg-base-100 border-2 rounded-2xl transition-all duration-300 overflow-hidden"
    :class="[
      operation.available
        ? 'cursor-pointer border-base-300 hover:border-primary/50 hover:shadow-xl hover:-translate-y-1'
        : 'cursor-not-allowed border-base-300/50 opacity-60'
    ]"
    @click="handleClick"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <!-- Gradient Background -->
    <div
      v-if="operation.available"
      class="absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity duration-300"
      :class="gradientColor"
    ></div>

    <!-- Coming Soon Badge -->
    <div
      v-if="!operation.available"
      class="absolute top-3 right-3 px-2 py-0.5 bg-base-300 text-base-content/50 text-xs rounded-full"
    >
      Próximamente
    </div>

    <!-- Content -->
    <div class="relative p-8 flex flex-col items-center text-center">
      <!-- Icon Container -->
      <div class="relative mb-5">
        <div
          class="flex items-center justify-center w-20 h-20 rounded-2xl transition-all duration-300"
          :class="[
            operation.available
              ? 'bg-base-200 group-hover:bg-base-100 group-hover:scale-110 group-hover:shadow-lg'
              : 'bg-base-200/50'
          ]"
        >
          <DynamicIcon
            :name="operation.icon"
            fallback="Cog"
            class="w-10 h-10 transition-transform duration-300"
            :class="operation.available ? 'group-hover:scale-110' : 'opacity-50'"
          />
        </div>
      </div>

      <!-- Name -->
      <h3 class="font-semibold text-lg leading-tight mb-2 whitespace-pre-line">
        {{ operation.name }}
      </h3>

      <!-- Description -->
      <p class="text-sm text-base-content/50 line-clamp-2">
        {{ operation.description }}
      </p>
    </div>

    <!-- Hover indicator line -->
    <div
      v-if="operation.available"
      class="absolute bottom-0 left-1/2 -translate-x-1/2 h-1 bg-primary rounded-t-full transition-all duration-300"
      :class="isHovered ? 'w-16 opacity-100' : 'w-0 opacity-0'"
    ></div>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
