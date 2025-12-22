<script setup lang="ts">
import { ref } from 'vue'
import type { Campaign } from '@/types/campaign'

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
    class="card bg-base-200 cursor-pointer transition-all duration-200 hover:scale-105 hover:shadow-lg"
    :class="{ 'dragging': isDragging }"
    draggable="true"
    @click="handleClick"
    @dragstart="onDragStart"
    @dragover="onDragOver"
    @drop="onDrop"
    @dragend="onDragEnd"
  >
    <div class="card-body items-center text-center p-6">
      <!-- Large icon (grayscale) -->
      <div class="text-5xl mb-2 grayscale">
        {{ campaign.icon || '📁' }}
      </div>

      <!-- Name -->
      <h3 class="card-title text-lg">
        {{ campaign.name }}
      </h3>

      <!-- Audio count -->
      <p class="text-sm opacity-70">
        {{ campaign.audio_count }} {{ campaign.audio_count === 1 ? 'audio' : 'audios' }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.card.dragging {
  opacity: 0.5;
  transform: scale(0.95);
}
</style>
