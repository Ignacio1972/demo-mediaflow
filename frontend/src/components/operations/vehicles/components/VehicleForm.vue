<template>
  <div class="vehicle-form">
    <div class="card bg-base-200 shadow-lg">
      <div class="card-body">
        <h2 class="card-title text-lg mb-4">Datos del Vehiculo</h2>

        <!-- Marca -->
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text font-medium">Marca del vehiculo</span>
          </label>
          <select
            v-model="marca"
            class="select select-bordered w-full"
          >
            <option value="" disabled>Seleccione una marca</option>
            <option v-for="brand in brands" :key="brand.id" :value="brand.name">
              {{ brand.name }}
            </option>
          </select>
        </div>

        <!-- Color -->
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text font-medium">Color</span>
          </label>
          <div class="flex gap-2">
            <select
              v-model="color"
              class="select select-bordered flex-1"
            >
              <option value="" disabled>Seleccione un color</option>
              <option v-for="c in colors" :key="c.id" :value="c.name">
                {{ c.name }}
              </option>
            </select>
            <div
              v-if="selectedColorHex"
              class="w-10 h-10 rounded-lg border border-base-300"
              :style="{ backgroundColor: selectedColorHex }"
            ></div>
          </div>
        </div>

        <!-- Patente (3 inputs) -->
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text font-medium">Patente</span>
            <span class="label-text-alt text-base-content/60">Formato: XX.XX.XX</span>
          </label>
          <div class="flex items-center gap-2">
            <!-- Part 1 -->
            <input
              ref="plateInput1"
              v-model="platePart1"
              @input="handlePlateInput(1, ($event.target as HTMLInputElement).value)"
              type="text"
              placeholder="XX"
              class="input input-bordered w-16 text-center uppercase font-mono text-lg tracking-wider"
              :class="{
                'input-error': plateValidation && !plateValidation.valid,
                'input-success': plateValidation && plateValidation.valid
              }"
              maxlength="2"
            />
            <span class="text-2xl font-bold text-base-content/40">.</span>
            <!-- Part 2 -->
            <input
              ref="plateInput2"
              v-model="platePart2"
              @input="handlePlateInput(2, ($event.target as HTMLInputElement).value)"
              @keydown="handlePlateKeydown(2, $event)"
              type="text"
              placeholder="XX"
              class="input input-bordered w-16 text-center uppercase font-mono text-lg tracking-wider"
              :class="{
                'input-error': plateValidation && !plateValidation.valid,
                'input-success': plateValidation && plateValidation.valid
              }"
              maxlength="2"
            />
            <span class="text-2xl font-bold text-base-content/40">.</span>
            <!-- Part 3 -->
            <input
              ref="plateInput3"
              v-model="platePart3"
              @input="handlePlateInput(3, ($event.target as HTMLInputElement).value)"
              @keydown="handlePlateKeydown(3, $event)"
              type="text"
              placeholder="XX"
              class="input input-bordered w-16 text-center uppercase font-mono text-lg tracking-wider"
              :class="{
                'input-error': plateValidation && !plateValidation.valid,
                'input-success': plateValidation && plateValidation.valid
              }"
              maxlength="2"
            />
          </div>
          <!-- Plate validation feedback -->
          <label v-if="plateValidation" class="label">
            <span
              v-if="plateValidation.valid"
              class="label-text-alt text-success"
            >
              {{ plateValidation.pronunciation }}
            </span>
            <span v-else class="label-text-alt text-error">
              {{ plateValidation.error }}
            </span>
          </label>
          <label v-if="plateValidation?.warning" class="label pt-0">
            <span class="label-text-alt text-warning">
              {{ plateValidation.warning }}
            </span>
          </label>
        </div>

        <!-- Plantilla -->
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text font-medium">Estilo del mensaje</span>
          </label>
          <select v-model="template" class="select select-bordered w-full">
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
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text font-medium">Voz</span>
          </label>
          <select
            v-model="voiceId"
            class="select select-bordered w-full"
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
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text font-medium">Musica de fondo</span>
            <span class="label-text-alt text-base-content/60">Opcional</span>
          </label>
          <select v-model="musicFile" class="select select-bordered w-full">
            <option :value="null">Sin musica</option>
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

        <!-- Modo de pronunciacion de numeros -->
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

        <!-- Generate button -->
        <div class="card-actions justify-end mt-4">
          <button
            @click="$emit('generate')"
            class="btn btn-primary"
            :disabled="!isFormValid || loadingGenerate"
          >
            <span
              v-if="loadingGenerate"
              class="loading loading-spinner loading-sm"
            ></span>
            <span v-else>Generar Audio</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick } from 'vue'
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
