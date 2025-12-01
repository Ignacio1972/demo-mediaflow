<template>
  <div class="voice-list">
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body p-4">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
          <h2 class="card-title text-lg">
            Voces ({{ voices.length }})
          </h2>
          <div class="text-xs text-base-content/50">
            Arrastra para reordenar
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="flex justify-center py-8">
          <span class="loading loading-spinner loading-lg text-primary"></span>
        </div>

        <!-- Empty State -->
        <div v-else-if="voices.length === 0" class="text-center py-8">
          <div class="text-5xl mb-4">🎙️</div>
          <p class="text-base-content/60">No hay voces configuradas</p>
          <p class="text-sm text-base-content/40 mt-1">Agrega una voz para comenzar</p>
        </div>

        <!-- Voice List -->
        <div v-else class="space-y-2" ref="listContainer">
          <TransitionGroup name="list">
            <VoiceCard
              v-for="voice in sortedVoices"
              :key="voice.id"
              :voice="voice"
              :is-selected="selectedVoice?.id === voice.id"
              @select="handleSelect"
              draggable="true"
              @dragstart="handleDragStart($event, voice)"
              @dragover.prevent="handleDragOver($event, voice)"
              @drop="handleDrop($event, voice)"
              @dragend="handleDragEnd"
              :class="{ 'opacity-50 scale-95': draggedVoice?.id === voice.id }"
            />
          </TransitionGroup>
        </div>

        <!-- Summary -->
        <div v-if="voices.length > 0" class="mt-4 pt-4 border-t border-base-300">
          <div class="flex justify-between text-xs text-base-content/50">
            <span>{{ activeCount }} activas</span>
            <span v-if="defaultVoice">Default: {{ defaultVoice.name }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import VoiceCard from './VoiceCard.vue'
import type { VoiceSettings } from '../composables/useVoiceManager'

const props = defineProps<{
  voices: VoiceSettings[]
  selectedVoice: VoiceSettings | null
  isLoading: boolean
}>()

const emit = defineEmits<{
  select: [voice: VoiceSettings]
  reorder: [voiceIds: string[]]
}>()

// Drag state
const draggedVoice = ref<VoiceSettings | null>(null)
const dragOverVoice = ref<VoiceSettings | null>(null)

// Computed
const sortedVoices = computed(() => {
  return [...props.voices].sort((a, b) => a.order - b.order)
})

const activeCount = computed(() => {
  return props.voices.filter(v => v.active).length
})

const defaultVoice = computed(() => {
  return props.voices.find(v => v.is_default)
})

// Handlers
const handleSelect = (voice: VoiceSettings) => {
  emit('select', voice)
}

const handleDragStart = (event: DragEvent, voice: VoiceSettings) => {
  draggedVoice.value = voice
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', voice.id)
  }
}

const handleDragOver = (event: DragEvent, voice: VoiceSettings) => {
  event.preventDefault()
  if (draggedVoice.value && draggedVoice.value.id !== voice.id) {
    dragOverVoice.value = voice
  }
}

const handleDrop = (event: DragEvent, targetVoice: VoiceSettings) => {
  event.preventDefault()

  if (!draggedVoice.value || draggedVoice.value.id === targetVoice.id) {
    return
  }

  // Calculate new order
  const currentOrder = sortedVoices.value.map(v => v.id)
  const draggedIndex = currentOrder.indexOf(draggedVoice.value.id)
  const targetIndex = currentOrder.indexOf(targetVoice.id)

  // Remove dragged item and insert at new position
  currentOrder.splice(draggedIndex, 1)
  currentOrder.splice(targetIndex, 0, draggedVoice.value.id)

  // Emit new order
  emit('reorder', currentOrder)
}

const handleDragEnd = () => {
  draggedVoice.value = null
  dragOverVoice.value = null
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
  transform: translateX(-30px);
}
</style>
