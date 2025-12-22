<script setup lang="ts">
import { computed } from 'vue'
import type { Voice } from '@/types/audio'
import { voicePhotos } from '@/assets/Characters'

interface Props {
  voices: Voice[]
  selectedVoiceId?: string
  showAvatars?: boolean
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showAvatars: true,
  size: 'md',
  disabled: false
})

const emit = defineEmits<{
  select: [voiceId: string]
  'update:selectedVoiceId': [voiceId: string]
}>()

// Size classes for avatars
const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm': return 'w-8 h-8'
    case 'lg': return 'w-12 h-12'
    default: return 'w-9 h-9'
  }
})

// Get voice photo by name (lowercase match)
function getVoicePhoto(voice: Voice): string | null {
  const name = voice.name.toLowerCase()
  return voicePhotos[name] || null
}

// Get initials for fallback avatar
function getInitials(name: string): string {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

// Find selected voice for display
const selectedVoice = computed(() => {
  return props.voices.find(v => v.id === props.selectedVoiceId)
})

// Handle voice selection
function selectVoice(voiceId: string) {
  if (props.disabled) return
  emit('select', voiceId)
  emit('update:selectedVoiceId', voiceId)
}
</script>

<template>
  <div class="voice-selector-base flex items-center gap-2">
    <!-- Avatar buttons -->
    <div v-if="showAvatars" class="flex items-center gap-2">
      <button
        v-for="voice in voices"
        :key="voice.id"
        type="button"
        @click="selectVoice(voice.id)"
        class="voice-avatar relative rounded-full overflow-hidden transition-all duration-200"
        :class="[
          sizeClasses,
          {
            'ring-2 ring-primary ring-offset-2 ring-offset-base-200 scale-110': selectedVoiceId === voice.id,
            'opacity-60 hover:opacity-100': selectedVoiceId !== voice.id,
            'pointer-events-none opacity-40': disabled
          }
        ]"
        :title="voice.name"
        :disabled="disabled"
      >
        <img
          v-if="getVoicePhoto(voice)"
          :src="getVoicePhoto(voice)!"
          :alt="voice.name"
          class="w-full h-full object-cover"
        />
        <div
          v-else
          class="w-full h-full bg-primary text-primary-content flex items-center justify-center text-xs font-bold"
        >
          {{ getInitials(voice.name) }}
        </div>
      </button>
    </div>

    <!-- Selected voice name -->
    <span v-if="selectedVoice" class="text-sm font-medium ml-2">
      {{ selectedVoice.name }}
    </span>
  </div>
</template>

<style scoped>
.voice-avatar {
  cursor: pointer;
  flex-shrink: 0;
}

.voice-avatar:hover:not(:disabled) {
  transform: scale(1.05);
}

.voice-avatar:active:not(:disabled) {
  transform: scale(0.95);
}
</style>
