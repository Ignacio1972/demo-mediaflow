<script setup lang="ts">
import { computed } from 'vue'
import { ClockIcon } from '@heroicons/vue/24/outline'
import type {
  ScheduleType,
  ScheduleVariant,
  ScheduleTypeOption,
  ScheduleVariantOption,
  MinutesOption,
  Voice
} from '../composables/useScheduleAnnouncement'

// Props
const props = defineProps<{
  scheduleType: ScheduleType
  variant: ScheduleVariant
  minutes: number
  voiceId: string
  types: ScheduleTypeOption[]
  variants: ScheduleVariantOption[]
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
  'update:scheduleType': [value: ScheduleType]
  'update:variant': [value: ScheduleVariant]
  'update:minutes': [value: number]
  'update:voiceId': [value: string]
  'generate': []
}>()

// v-model computed properties
const scheduleTypeModel = computed({
  get: () => props.scheduleType,
  set: (value) => emit('update:scheduleType', value)
})

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
          <h2 class="text-lg font-semibold">Configuración</h2>
          <p class="text-sm text-base-content/50">Selecciona el tipo de anuncio</p>
        </div>
      </div>

      <!-- Schedule Type -->
      <div class="form-control">
        <label class="label">
          <span class="label-text font-medium">Tipo de Anuncio</span>
        </label>
        <div class="grid grid-cols-2 gap-3">
          <button
            v-for="type in types"
            :key="type.id"
            type="button"
            class="btn h-auto py-4 flex flex-col gap-1"
            :class="[
              scheduleTypeModel === type.id
                ? 'btn-primary'
                : 'btn-ghost bg-base-100 border-2 border-base-300 hover:border-primary/50'
            ]"
            @click="scheduleTypeModel = type.id"
          >
            <span class="text-2xl">{{ type.id === 'opening' ? '🌅' : '🌙' }}</span>
            <span class="font-medium">{{ type.name }}</span>
          </button>
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
    </div>
  </div>
</template>
