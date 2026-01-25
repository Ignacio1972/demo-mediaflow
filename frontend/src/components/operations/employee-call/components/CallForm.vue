<template>
  <div class="call-form">
    <div class="card bg-base-100 border-2 border-base-300 rounded-2xl shadow-sm">
      <div class="card-body p-6">
        <!-- Header (hidden on mobile) -->
        <div class="hidden md:block mb-6">
          <h2 class="text-xl font-bold tracking-tight">Datos del Llamado</h2>
          <p class="text-sm text-base-content/50 mt-1">Ingresa la información para generar el anuncio</p>
        </div>

        <!-- Call Type Toggle -->
        <div class="space-y-2 mb-5">
          <label class="text-sm font-medium">Tipo de llamado</label>
          <div class="flex gap-2">
            <button
              @click="callType = 'empleado'"
              class="btn flex-1 rounded-xl transition-all duration-200"
              :class="callType === 'empleado'
                ? 'btn-primary'
                : 'btn-ghost bg-base-200/50 border-2 border-base-300'"
            >
              <UserIcon class="w-5 h-5" />
              Empleado
            </button>
            <button
              @click="callType = 'cliente'"
              class="btn flex-1 rounded-xl transition-all duration-200"
              :class="callType === 'cliente'
                ? 'btn-primary'
                : 'btn-ghost bg-base-200/50 border-2 border-base-300'"
            >
              <UserGroupIcon class="w-5 h-5" />
              Cliente
            </button>
          </div>
        </div>

        <!-- Nombre -->
        <div class="space-y-2 mb-5">
          <label class="text-sm font-medium">
            Nombre {{ callType === 'empleado' ? 'del empleado' : 'del cliente' }}
          </label>
          <input
            v-model="nombre"
            type="text"
            :placeholder="callType === 'empleado' ? 'Ej: Juan Pérez' : 'Ej: María González'"
            class="input bg-base-200/50 border-2 border-base-300 focus:border-primary focus:bg-base-100 rounded-xl w-full transition-all duration-200"
          />
        </div>

        <!-- Ubicación -->
        <div class="space-y-2 mb-5">
          <label class="text-sm font-medium">Ubicación</label>
          <div class="dropdown w-full">
            <input
              v-model="ubicacion"
              type="text"
              placeholder="Seleccione o escriba una ubicación"
              class="input bg-base-200/50 border-2 border-base-300 focus:border-primary focus:bg-base-100 rounded-xl w-full transition-all duration-200"
              @focus="showLocationDropdown = true"
              @blur="handleBlur"
            />
            <!-- Dropdown menu -->
            <ul
              v-if="showLocationDropdown && filteredLocations.length > 0"
              class="dropdown-content z-[1] menu p-2 shadow-lg bg-base-100 rounded-xl w-full mt-1 border-2 border-base-300 max-h-60 overflow-y-auto"
            >
              <li
                v-for="loc in filteredLocations"
                :key="loc.id"
                @mousedown.prevent="selectLocation(loc)"
              >
                <a class="rounded-lg">{{ loc.name }}</a>
              </li>
            </ul>
          </div>
        </div>

        <!-- Voz - hidden on mobile (uses default voice) -->
        <div class="space-y-2 mb-5 hidden md:block">
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

        <!-- Announcement Sound Toggle (Desktop) -->
        <div class="form-control mb-5 hidden md:block">
          <label class="label cursor-pointer justify-start gap-4 py-3 px-4 bg-base-200/50 rounded-xl border-2 border-base-300/50 hover:border-warning/30 transition-all">
            <input
              type="checkbox"
              v-model="useAnnouncementSound"
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

          <!-- Announcement Sound Toggle (Mobile) -->
          <label class="label cursor-pointer justify-start gap-4 py-3 px-4 mt-4 bg-base-200/50 rounded-xl border-2 border-base-300/50 md:hidden">
            <input
              type="checkbox"
              v-model="useAnnouncementSound"
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { SpeakerWaveIcon, UserIcon, UserGroupIcon } from '@heroicons/vue/24/outline'
import type { LocationOption, Voice, CallType } from '../composables/useEmployeeCallAnnouncement'

// Props
interface Props {
  callType: CallType
  nombre: string
  ubicacion: string
  voiceId: string
  useAnnouncementSound: boolean
  locations: LocationOption[]
  voices: Voice[]
  isFormValid: boolean
  loadingVoices: boolean
  loadingGenerate: boolean
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  (e: 'update:callType', value: CallType): void
  (e: 'update:nombre', value: string): void
  (e: 'update:ubicacion', value: string): void
  (e: 'update:voiceId', value: string): void
  (e: 'update:useAnnouncementSound', value: boolean): void
  (e: 'generate'): void
}>()

// Local state for dropdown
const showLocationDropdown = ref(false)

// v-model bindings
const callType = computed({
  get: () => props.callType,
  set: (v) => emit('update:callType', v)
})

const nombre = computed({
  get: () => props.nombre,
  set: (v) => emit('update:nombre', v)
})

const ubicacion = computed({
  get: () => props.ubicacion,
  set: (v) => emit('update:ubicacion', v)
})

const voiceId = computed({
  get: () => props.voiceId,
  set: (v) => emit('update:voiceId', v)
})

const useAnnouncementSound = computed({
  get: () => props.useAnnouncementSound,
  set: (v) => emit('update:useAnnouncementSound', v)
})

// Filtered locations based on input
const filteredLocations = computed(() => {
  const query = props.ubicacion.toLowerCase()
  if (!query) return props.locations
  return props.locations.filter(loc =>
    loc.name.toLowerCase().includes(query)
  )
})

// Select location from dropdown
function selectLocation(loc: LocationOption) {
  emit('update:ubicacion', loc.name)
  showLocationDropdown.value = false
}

// Handle blur with delay to allow click
function handleBlur() {
  setTimeout(() => {
    showLocationDropdown.value = false
  }, 200)
}
</script>
