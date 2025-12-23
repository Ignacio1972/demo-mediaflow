<template>
  <div class="vehicle-form">
    <div class="card bg-base-100 border-2 border-base-300 rounded-2xl shadow-sm">
      <div class="card-body p-6">
        <!-- Header -->
        <div class="mb-6">
          <h2 class="text-xl font-bold tracking-tight">Datos del Vehículo</h2>
          <p class="text-sm text-base-content/50 mt-1">Ingresa la información para generar el anuncio</p>
        </div>

        <!-- Marca -->
        <div class="space-y-2 mb-5">
          <label class="text-sm font-medium">Marca del vehículo</label>
          <select
            v-model="marca"
            class="select bg-base-200/50 border-2 border-base-300 focus:border-primary focus:bg-base-100 rounded-xl w-full transition-all duration-200"
          >
            <option value="" disabled>Seleccione una marca</option>
            <option v-for="brand in brands" :key="brand.id" :value="brand.name">
              {{ brand.name }}
            </option>
          </select>
        </div>

        <!-- Color -->
        <div class="space-y-2 mb-5">
          <label class="text-sm font-medium">Color</label>
          <div class="flex gap-3">
            <select
              v-model="color"
              class="select bg-base-200/50 border-2 border-base-300 focus:border-primary focus:bg-base-100 rounded-xl flex-1 transition-all duration-200"
            >
              <option value="" disabled>Seleccione un color</option>
              <option v-for="c in colors" :key="c.id" :value="c.name">
                {{ c.name }}
              </option>
            </select>
            <div
              v-if="selectedColorHex"
              class="w-11 h-11 rounded-xl border-2 border-base-300 shadow-sm transition-all duration-200"
              :style="{ backgroundColor: selectedColorHex }"
            ></div>
          </div>
        </div>

        <!-- Patente (3 inputs) -->
        <div class="space-y-2 mb-5">
          <div class="flex items-center justify-between">
            <label class="text-sm font-medium">Patente</label>
            <span class="text-xs text-base-content/40">Formato: XX.XX.XX</span>
          </div>
          <div class="flex items-center gap-3">
            <!-- Part 1 -->
            <input
              ref="plateInput1"
              v-model="platePart1"
              @input="handlePlateInput(1, ($event.target as HTMLInputElement).value)"
              type="text"
              placeholder="XX"
              class="input bg-base-200/50 border-2 border-base-300 focus:border-primary focus:bg-base-100 w-16 text-center uppercase font-mono text-lg tracking-wider rounded-xl transition-all duration-200"
              :class="{
                'border-error bg-error/5': plateValidation && !plateValidation.valid,
                'border-success bg-success/5': plateValidation && plateValidation.valid
              }"
              maxlength="2"
            />
            <span class="text-2xl font-bold text-base-content/30">·</span>
            <!-- Part 2 -->
            <input
              ref="plateInput2"
              v-model="platePart2"
              @input="handlePlateInput(2, ($event.target as HTMLInputElement).value)"
              @keydown="handlePlateKeydown(2, $event)"
              type="text"
              placeholder="XX"
              class="input bg-base-200/50 border-2 border-base-300 focus:border-primary focus:bg-base-100 w-16 text-center uppercase font-mono text-lg tracking-wider rounded-xl transition-all duration-200"
              :class="{
                'border-error bg-error/5': plateValidation && !plateValidation.valid,
                'border-success bg-success/5': plateValidation && plateValidation.valid
              }"
              maxlength="2"
            />
            <span class="text-2xl font-bold text-base-content/30">·</span>
            <!-- Part 3 -->
            <input
              ref="plateInput3"
              v-model="platePart3"
              @input="handlePlateInput(3, ($event.target as HTMLInputElement).value)"
              @keydown="handlePlateKeydown(3, $event)"
              type="text"
              placeholder="XX"
              class="input bg-base-200/50 border-2 border-base-300 focus:border-primary focus:bg-base-100 w-16 text-center uppercase font-mono text-lg tracking-wider rounded-xl transition-all duration-200"
              :class="{
                'border-error bg-error/5': plateValidation && !plateValidation.valid,
                'border-success bg-success/5': plateValidation && plateValidation.valid
              }"
              maxlength="2"
            />
          </div>
          <!-- Plate validation feedback -->
          <div v-if="plateValidation" class="pt-1">
            <p v-if="plateValidation.valid" class="text-xs text-success">
              {{ plateValidation.pronunciation }}
            </p>
            <p v-else class="text-xs text-error">
              {{ plateValidation.error }}
            </p>
          </div>
          <p v-if="plateValidation?.warning" class="text-xs text-warning">
            {{ plateValidation.warning }}
          </p>
        </div>

        <!-- Plantilla -->
        <div class="space-y-2 mb-5">
          <label class="text-sm font-medium">Estilo del mensaje</label>
          <select
            v-model="template"
            class="select bg-base-200/50 border-2 border-base-300 focus:border-primary focus:bg-base-100 rounded-xl w-full transition-all duration-200"
          >
            <option
              v-for="t in templates"
              :key="t.id"
              :value="t.id"
            >
              {{ t.name }} - {{ t.description }}
            </option>
          </select>
        </div>

        <!-- Voz -->
        <div class="space-y-2 mb-5">
          <label class="text-sm font-medium">Voz</label>
          <select
            v-model="voiceId"
            class="select bg-base-200/50 border-2 border-base-300 focus:border-primary focus:bg-base-100 rounded-xl w-full transition-all duration-200"
            :disabled="loadingVoices"
          >
            <option value="" disabled>Seleccione una voz</option>
            <option
              v-for="voice in voices"
              :key="voice.id"
              :value="voice.id"
            >
              {{ voice.name }}
            </option>
          </select>
        </div>

        <!-- Musica de fondo -->
        <div class="space-y-2 mb-5">
          <div class="flex items-center justify-between">
            <label class="text-sm font-medium">Música de fondo</label>
            <span class="text-xs text-base-content/40">Opcional</span>
          </div>
          <select
            v-model="musicFile"
            class="select bg-base-200/50 border-2 border-base-300 focus:border-primary focus:bg-base-100 rounded-xl w-full transition-all duration-200"
          >
            <option :value="null">Sin música</option>
            <option
              v-for="track in musicTracks"
              :key="track.id"
              :value="track.filename"
            >
              {{ track.display_name }}
              <template v-if="track.is_default"> (Por defecto)</template>
            </option>
          </select>
        </div>

        <!-- Modo de pronunciacion de numeros (comentado para uso futuro)
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text font-medium">Pronunciacion de patente</span>
          </label>
          <div class="flex gap-4">
            <label class="label cursor-pointer gap-2">
              <input
                type="radio"
                v-model="numberMode"
                value="words"
                class="radio radio-primary radio-sm"
              />
              <span class="label-text">Palabras (cuarenta y cinco)</span>
            </label>
            <label class="label cursor-pointer gap-2">
              <input
                type="radio"
                v-model="numberMode"
                value="digits"
                class="radio radio-primary radio-sm"
              />
              <span class="label-text">Digitos (cuatro cinco)</span>
            </label>
          </div>
        </div>
        -->

        <!-- Generate button -->
        <div class="pt-4 mt-2 border-t border-base-200">
          <button
            @click="$emit('generate')"
            class="btn btn-primary w-full h-12 rounded-xl font-semibold
                   shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30
                   transition-all duration-200"
            :disabled="!isFormValid || loadingGenerate"
          >
            <span
              v-if="loadingGenerate"
              class="loading loading-spinner loading-sm"
            ></span>
            <template v-else>
              <SpeakerWaveIcon class="w-5 h-5" />
              <span>Generar Audio</span>
            </template>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick } from 'vue'
import { SpeakerWaveIcon } from '@heroicons/vue/24/outline'
import type {
  VehicleBrand,
  VehicleColor,
  TemplateInfo,
  Voice,
  MusicTrack,
  PlateInfo
} from '../composables/useVehicleAnnouncement'

// Props
interface Props {
  marca: string
  color: string
  platePart1: string
  platePart2: string
  platePart3: string
  voiceId: string
  musicFile: string | null
  template: string
  numberMode: 'words' | 'digits'
  brands: VehicleBrand[]
  colors: VehicleColor[]
  templates: TemplateInfo[]
  voices: Voice[]
  musicTracks: MusicTrack[]
  plateValidation: PlateInfo | null
  isFormValid: boolean
  loadingVoices: boolean
  loadingGenerate: boolean
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  (e: 'update:marca', value: string): void
  (e: 'update:color', value: string): void
  (e: 'update:platePart1', value: string): void
  (e: 'update:platePart2', value: string): void
  (e: 'update:platePart3', value: string): void
  (e: 'update:voiceId', value: string): void
  (e: 'update:musicFile', value: string | null): void
  (e: 'update:template', value: string): void
  (e: 'update:numberMode', value: 'words' | 'digits'): void
  (e: 'generate'): void
}>()

// v-model bindings
const marca = computed({
  get: () => props.marca,
  set: (v) => emit('update:marca', v)
})

const color = computed({
  get: () => props.color,
  set: (v) => emit('update:color', v)
})

const platePart1 = computed({
  get: () => props.platePart1,
  set: (v) => emit('update:platePart1', v.toUpperCase().slice(0, 2))
})

const platePart2 = computed({
  get: () => props.platePart2,
  set: (v) => emit('update:platePart2', v.toUpperCase().slice(0, 2))
})

const platePart3 = computed({
  get: () => props.platePart3,
  set: (v) => emit('update:platePart3', v.toUpperCase().slice(0, 2))
})

const voiceId = computed({
  get: () => props.voiceId,
  set: (v) => emit('update:voiceId', v)
})

const musicFile = computed({
  get: () => props.musicFile,
  set: (v) => emit('update:musicFile', v)
})

const template = computed({
  get: () => props.template,
  set: (v) => emit('update:template', v)
})

const numberMode = computed({
  get: () => props.numberMode,
  set: (v) => emit('update:numberMode', v)
})

// Selected color hex for preview
const selectedColorHex = computed(() => {
  const found = props.colors.find(
    c => c.name.toLowerCase() === props.color.toLowerCase()
  )
  return found?.hex_color || null
})

// Refs for plate inputs (for auto-focus)
const plateInput1 = ref<HTMLInputElement | null>(null)
const plateInput2 = ref<HTMLInputElement | null>(null)
const plateInput3 = ref<HTMLInputElement | null>(null)

// Auto-focus to next input when current is filled
function handlePlateInput(part: 1 | 2 | 3, value: string) {
  if (value.length === 2) {
    nextTick(() => {
      if (part === 1) {
        plateInput2.value?.focus()
      } else if (part === 2) {
        plateInput3.value?.focus()
      }
    })
  }
}

// Handle backspace to go to previous input
function handlePlateKeydown(part: 2 | 3, event: KeyboardEvent) {
  const target = event.target as HTMLInputElement
  if (event.key === 'Backspace' && target.value === '') {
    event.preventDefault()
    if (part === 2) {
      plateInput1.value?.focus()
    } else if (part === 3) {
      plateInput2.value?.focus()
    }
  }
}
</script>
