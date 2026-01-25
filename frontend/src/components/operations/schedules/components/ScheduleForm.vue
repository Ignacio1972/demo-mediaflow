<script setup lang="ts">
import { computed } from 'vue'
import { ClockIcon } from '@heroicons/vue/24/outline'
import type {
  ScheduleVariant,
  ScheduleVariantOption,
  MinutesOption,
  Voice
} from '../composables/useScheduleAnnouncement'

// Props
const props = defineProps<{
  variant: ScheduleVariant
  minutes: number
  voiceId: string
  useAnnouncementSound: boolean
  availableVariants: ScheduleVariantOption[]
  minutesOptions: MinutesOption[]
  voices: Voice[]
  showMinutes: boolean
  isFormValid: boolean
  loadingVoices: boolean
  loadingGenerate: boolean
}>()

// Emits
const emit = defineEmits<{
  'update:variant': [value: ScheduleVariant]
  'update:minutes': [value: number]
  'update:voiceId': [value: string]
  'update:useAnnouncementSound': [value: boolean]
  'generate': []
}>()

// v-model computed properties
const variantModel = computed({
  get: () => props.variant,
  set: (value) => emit('update:variant', value)
})

const minutesModel = computed({
  get: () => props.minutes,
  set: (value) => emit('update:minutes', value)
})

const voiceModel = computed({
  get: () => props.voiceId,
  set: (value) => emit('update:voiceId', value)
})

const useAnnouncementSoundModel = computed({
  get: () => props.useAnnouncementSound,
  set: (value) => emit('update:useAnnouncementSound', value)
})

function handleGenerate() {
  emit('generate')
}
</script>

<template>
  <div class="card bg-base-200/50 border-2 border-base-300/50 shadow-lg">
    <div class="card-body space-y-6">
      <!-- Header -->
      <div class="flex items-center gap-3">
        <div class="flex items-center justify-center w-10 h-10 bg-primary/10 rounded-xl">
          <ClockIcon class="w-5 h-5 text-primary" />
        </div>
        <div>
          <h2 class="text-lg font-semibold">Anuncio de Cierre</h2>
          <p class="text-sm text-base-content/50">Selecciona la variante del mensaje</p>
        </div>
      </div>

      <!-- Variant -->
      <div class="form-control">
        <label class="label">
          <span class="label-text font-medium">Variante del Mensaje</span>
        </label>
        <select
          v-model="variantModel"
          class="select select-bordered w-full bg-base-100"
        >
          <option
            v-for="v in availableVariants"
            :key="v.id"
            :value="v.id"
          >
            {{ v.name }} - {{ v.description }}
          </option>
        </select>
      </div>

      <!-- Minutes (conditional) -->
      <div v-if="showMinutes" class="form-control">
        <label class="label">
          <span class="label-text font-medium">Minutos antes del cierre</span>
        </label>
        <select
          v-model.number="minutesModel"
          class="select select-bordered w-full bg-base-100"
        >
          <option
            v-for="option in minutesOptions"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
      </div>

      <!-- Voice Selector (hidden on mobile) -->
      <div class="form-control hidden md:block">
        <label class="label">
          <span class="label-text font-medium">Voz</span>
        </label>
        <select
          v-model="voiceModel"
          class="select select-bordered w-full bg-base-100"
          :disabled="loadingVoices"
        >
          <option value="" disabled>
            {{ loadingVoices ? 'Cargando voces...' : 'Selecciona una voz' }}
          </option>
          <option
            v-for="voice in voices"
            :key="voice.id"
            :value="voice.id"
          >
            {{ voice.name }}
          </option>
        </select>
      </div>

      <!-- Announcement Sound Toggle (Desktop) -->
      <div class="form-control hidden md:block">
        <label class="label cursor-pointer justify-start gap-4 py-3 px-4 bg-base-100 rounded-xl border border-base-300 hover:border-warning/30 transition-all">
          <input
            type="checkbox"
            v-model="useAnnouncementSoundModel"
            class="toggle toggle-warning"
          />
          <div>
            <span class="label-text font-medium">Sonido de anuncio</span>
            <p class="text-xs text-base-content/50 mt-0.5">
              Agrega sonido de intro y outro al mensaje
            </p>
          </div>
        </label>
      </div>

      <!-- Generate Button -->
      <button
        type="button"
        class="btn btn-primary btn-lg w-full gap-2"
        :class="{ 'btn-disabled': !isFormValid || loadingGenerate }"
        :disabled="!isFormValid || loadingGenerate"
        @click="handleGenerate"
      >
        <span v-if="loadingGenerate" class="loading loading-spinner loading-sm"></span>
        <template v-else>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
          </svg>
          Generar Audio
        </template>
      </button>

      <!-- Announcement Sound Toggle (Mobile) -->
      <label class="label cursor-pointer justify-start gap-4 py-3 px-4 mt-4 bg-base-100 rounded-xl border border-base-300 md:hidden">
        <input
          type="checkbox"
          v-model="useAnnouncementSoundModel"
          class="toggle toggle-warning"
        />
        <div>
          <span class="label-text font-medium">Sonido de anuncio</span>
          <p class="text-xs text-base-content/50 mt-0.5">
            Agrega sonido de intro y outro
          </p>
        </div>
      </label>
    </div>
  </div>
</template>
