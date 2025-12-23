<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Campaign } from '@/types/campaign'
import DynamicIcon from '@/components/shared/ui/DynamicIcon.vue'

interface Props {
  campaign: Campaign
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: [campaign: Campaign]
  dragStart: [event: DragEvent]
  dragOver: [event: DragEvent]
  drop: [event: DragEvent]
  dragEnd: [event: DragEvent]
}>()

const isDragging = ref(false)
const isHovered = ref(false)

// Generate a subtle background gradient based on campaign name
const gradientColor = computed(() => {
  const colors = [
    'from-rose-500/10 to-orange-500/5',
    'from-violet-500/10 to-purple-500/5',
    'from-blue-500/10 to-cyan-500/5',
    'from-emerald-500/10 to-teal-500/5',
    'from-amber-500/10 to-yellow-500/5',
    'from-pink-500/10 to-rose-500/5',
    'from-indigo-500/10 to-blue-500/5',
    'from-lime-500/10 to-green-500/5',
  ]
  const hash = props.campaign.name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return colors[hash % colors.length]
})

function handleClick() {
  emit('click', props.campaign)
}

function onDragStart(event: DragEvent) {
  isDragging.value = true
  emit('dragStart', event)
}

function onDragOver(event: DragEvent) {
  emit('dragOver', event)
}

function onDrop(event: DragEvent) {
  emit('drop', event)
}

function onDragEnd(event: DragEvent) {
  isDragging.value = false
  emit('dragEnd', event)
}
</script>

<template>
  <div
    class="group relative bg-base-100 border-2 rounded-2xl cursor-pointer transition-all duration-300 overflow-hidden"
    :class="[
      isDragging
        ? 'opacity-50 scale-95 border-primary'
        : 'border-base-300 hover:border-primary/50 hover:shadow-xl hover:-translate-y-1'
    ]"
    draggable="true"
    @click="handleClick"
    @dragstart="onDragStart"
    @dragover="onDragOver"
    @drop="onDrop"
    @dragend="onDragEnd"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <!-- Gradient Background -->
    <div
      class="absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity duration-300"
      :class="gradientColor"
    ></div>

    <!-- Content -->
    <div class="relative p-6 flex flex-col items-center text-center">
      <!-- Icon Container -->
      <div class="relative mb-4">
        <!-- Icon background -->
        <div
          class="flex items-center justify-center w-16 h-16 bg-base-200 group-hover:bg-base-100 rounded-2xl transition-all duration-300 group-hover:scale-110 group-hover:shadow-lg"
        >
          <DynamicIcon
            :name="campaign.icon"
            fallback="Folder"
            class="w-8 h-8 text-4xl transition-transform duration-300 group-hover:scale-110"
          />
        </div>
      </div>

      <!-- Name -->
      <h3 class="font-semibold text-base leading-tight mb-1 line-clamp-2">
        {{ campaign.name }}
      </h3>

      <!-- Subtitle / Meta -->
      <p class="text-xs text-base-content/50">
        {{ campaign.audio_count === 0 ? 'Sin audios' : `${campaign.audio_count} audio${campaign.audio_count !== 1 ? 's' : ''}` }}
      </p>
    </div>

    <!-- Hover indicator line -->
    <div
      class="absolute bottom-0 left-1/2 -translate-x-1/2 h-1 bg-primary rounded-t-full transition-all duration-300"
      :class="isHovered ? 'w-12 opacity-100' : 'w-0 opacity-0'"
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
