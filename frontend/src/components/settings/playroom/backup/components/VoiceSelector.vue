<template>
  <div class="form-control">
    <label class="label">
      <span class="label-text font-medium">Voz</span>
    </label>
    <select
      class="select select-bordered w-full"
      :value="selectedVoiceId"
      @change="handleChange"
    >
      <option value="" disabled>Selecciona una voz</option>
      <option
        v-for="voice in sortedVoices"
        :key="voice.id"
        :value="voice.id"
      >
        {{ voice.name }}
        {{ voice.is_default ? '(Default)' : '' }}
        {{ voice.gender === 'M' ? '♂' : voice.gender === 'F' ? '♀' : '' }}
      </option>
    </select>
    <label class="label">
      <span class="label-text-alt text-base-content/50">
        {{ selectedVoice ? `ID: ${selectedVoice.elevenlabs_id.substring(0, 8)}...` : 'Selecciona una voz para continuar' }}
      </span>
    </label>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Voice } from '@/types/audio'

const props = defineProps<{
  voices: Voice[]
  selectedVoiceId: string | null
}>()

const emit = defineEmits<{
  (e: 'update:selected-voice-id', value: string): void
}>()

const sortedVoices = computed(() =>
  [...props.voices].sort((a, b) => {
    // Default voice first, then by order
    if (a.is_default && !b.is_default) return -1
    if (!a.is_default && b.is_default) return 1
    return a.order - b.order
  })
)

const selectedVoice = computed(() =>
  props.voices.find(v => v.id === props.selectedVoiceId)
)

const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  emit('update:selected-voice-id', target.value)
}
</script>
