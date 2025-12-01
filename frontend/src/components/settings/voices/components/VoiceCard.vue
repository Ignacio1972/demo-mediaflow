<template>
  <div
    class="card bg-base-200 hover:bg-base-300 transition-all cursor-pointer border-2"
    :class="{
      'border-primary shadow-lg': isSelected,
      'border-transparent': !isSelected,
      'opacity-50': !voice.active
    }"
    @click="$emit('select', voice)"
  >
    <div class="card-body p-4">
      <div class="flex items-center gap-3">
        <!-- Drag Handle -->
        <div class="cursor-grab text-base-content/40 hover:text-base-content/70" @mousedown.stop>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
          </svg>
        </div>

        <!-- Avatar/Gender Icon -->
        <div class="avatar placeholder">
          <div class="bg-primary text-primary-content rounded-full w-10">
            <span class="text-lg">{{ genderIcon }}</span>
          </div>
        </div>

        <!-- Voice Info -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <h3 class="font-semibold truncate">{{ voice.name }}</h3>
            <div v-if="voice.is_default" class="badge badge-warning badge-sm">Default</div>
            <div v-if="!voice.active" class="badge badge-ghost badge-sm">Inactiva</div>
          </div>
          <p class="text-xs text-base-content/60 truncate">
            ID: {{ voice.id }}
          </p>
        </div>

        <!-- Volume Badge -->
        <div class="text-right">
          <div
            class="badge badge-sm"
            :class="volumeBadgeClass"
          >
            {{ volumeDisplay }}
          </div>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="flex gap-4 mt-2 text-xs text-base-content/50">
        <span>Style: {{ voice.style }}%</span>
        <span>Stability: {{ voice.stability }}%</span>
        <span>Similarity: {{ voice.similarity_boost }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { VoiceSettings } from '../composables/useVoiceManager'

const props = defineProps<{
  voice: VoiceSettings
  isSelected: boolean
}>()

defineEmits<{
  select: [voice: VoiceSettings]
}>()

const genderIcon = computed(() => {
  switch (props.voice.gender) {
    case 'M': return '👨'
    case 'F': return '👩'
    default: return '🎙️'
  }
})

const volumeDisplay = computed(() => {
  const vol = props.voice.volume_adjustment || 0
  if (vol === 0) return '0 dB'
  return vol > 0 ? `+${vol} dB` : `${vol} dB`
})

const volumeBadgeClass = computed(() => {
  const vol = props.voice.volume_adjustment || 0
  if (vol > 0) return 'badge-success'
  if (vol < 0) return 'badge-error'
  return 'badge-ghost'
})
</script>
