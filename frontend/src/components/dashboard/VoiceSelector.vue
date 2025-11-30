<template>
  <div class="voice-selector">
    <div class="form-control">
      <div class="flex items-center justify-between gap-4">
        <label class="label-text font-medium">Seleccionar Voz</label>

        <!-- Voice Dropdown -->
        <select
          v-if="!isLoading && !error && voices.length > 0"
          v-model="selectedVoiceId"
          @change="handleVoiceChange"
          class="select select-bordered w-64"
        >
          <option
            v-for="voice in voices"
            :key="voice.id"
            :value="voice.id"
          >
            {{ getGenderIcon(voice.gender) }} {{ voice.name }}
            {{ voice.is_default ? '★' : '' }}
          </option>
        </select>

        <!-- Loading State -->
        <span v-else-if="isLoading" class="loading loading-spinner loading-md"></span>

        <!-- Error State -->
        <span v-else-if="error" class="text-error text-sm flex items-center gap-1">
          <XCircleIcon class="w-4 h-4" />
          Error cargando voces
        </span>

        <!-- Empty State -->
        <span v-else class="text-warning text-sm flex items-center gap-1">
          <ExclamationTriangleIcon class="w-4 h-4" />
          No hay voces
        </span>
      </div>
    </div>

    <!-- Voice Settings Preview (Collapsed) -->
    <div v-if="selectedVoice" class="collapse collapse-arrow bg-base-200 mt-4">
      <input type="checkbox" />
      <div class="collapse-title text-sm font-medium">
        Ver configuración de {{ selectedVoice.name }}
      </div>
      <div class="collapse-content text-sm">
        <div class="grid grid-cols-2 gap-2 mt-2">
          <div>
            <span class="opacity-70">Estilo:</span>
            <span class="font-mono ml-2">{{ selectedVoice.style }}%</span>
          </div>
          <div>
            <span class="opacity-70">Estabilidad:</span>
            <span class="font-mono ml-2">{{ selectedVoice.stability }}%</span>
          </div>
          <div>
            <span class="opacity-70">Similitud:</span>
            <span class="font-mono ml-2">{{ selectedVoice.similarity_boost }}%</span>
          </div>
          <div>
            <span class="opacity-70">Volumen:</span>
            <span class="font-mono ml-2">{{ selectedVoice.volume_adjustment > 0 ? '+' : '' }}{{ selectedVoice.volume_adjustment }} dB</span>
          </div>
        </div>
        <p class="text-xs opacity-70 mt-3 flex items-center gap-1">
          <LightBulbIcon class="w-4 h-4" />
          Estos settings se aplican automáticamente al generar
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref, watch } from 'vue'
import { useAudioStore } from '@/stores/audio'
import { storeToRefs } from 'pinia'
import { XCircleIcon, ExclamationTriangleIcon, LightBulbIcon } from '@heroicons/vue/24/outline'

// Store
const audioStore = useAudioStore()
const { voices, selectedVoice, isLoading, error } = storeToRefs(audioStore)

// Local state for v-model
const selectedVoiceId = ref<string>('')

// Watch for selectedVoice changes from store
watch(selectedVoice, (newVoice) => {
  if (newVoice) {
    selectedVoiceId.value = newVoice.id
  }
}, { immediate: true })

// Methods
const handleVoiceChange = () => {
  const voice = voices.value.find(v => v.id === selectedVoiceId.value)
  if (voice) {
    audioStore.setSelectedVoice(voice)
  }
}

const getGenderIcon = (gender?: string) => {
  if (gender === 'M') return '♂'
  if (gender === 'F') return '♀'
  return '🎤'
}

// Load voices on mount
onMounted(async () => {
  if (voices.value.length === 0) {
    await audioStore.loadVoices()
  }
})
</script>

<style scoped>
.voice-selector {
  width: 100%;
}
</style>
