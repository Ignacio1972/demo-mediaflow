<template>
  <dialog class="modal" :class="{ 'modal-open': open }">
    <div class="modal-box max-w-lg">
      <h3 class="font-bold text-lg flex items-center gap-2">
        <CalendarIcon class="h-5 w-5" />
        Programar: {{ message?.display_name }}
      </h3>

      <!-- Schedule Type Tabs -->
      <div class="tabs tabs-boxed mt-4">
        <button
          v-for="type in scheduleTypes"
          :key="type.id"
          class="tab"
          :class="{ 'tab-active': scheduleType === type.id }"
          @click="scheduleType = type.id"
        >
          {{ type.icon }} {{ type.label }}
        </button>
      </div>

      <!-- Interval Config -->
      <div v-if="scheduleType === 'interval'" class="mt-4 space-y-4">
        <div>
          <label class="label"><span class="label-text">Repetir cada:</span></label>
          <div class="flex items-center gap-2">
            <input
              v-model.number="intervalHours"
              type="number"
              class="input input-bordered input-sm w-20"
              min="0"
              max="23"
            />
            <span>horas</span>
            <input
              v-model.number="intervalMinutes"
              type="number"
              class="input input-bordered input-sm w-20"
              min="0"
              max="59"
            />
            <span>minutos</span>
          </div>
        </div>

        <div>
          <label class="label"><span class="label-text">En horario:</span></label>
          <div class="flex items-center gap-2">
            <input v-model="startTime" type="time" class="input input-bordered input-sm" />
            <span>a</span>
            <input v-model="endTime" type="time" class="input input-bordered input-sm" />
          </div>
        </div>

        <DaySelector v-model="selectedDays" />
      </div>

      <!-- Specific Config -->
      <div v-if="scheduleType === 'specific'" class="mt-4 space-y-4">
        <DaySelector v-model="selectedDays" />

        <div>
          <label class="label"><span class="label-text">Horarios:</span></label>
          <div class="space-y-2">
            <div
              v-for="(time, index) in specificTimes"
              :key="index"
              class="flex items-center gap-2"
            >
              <input
                v-model="specificTimes[index]"
                type="time"
                class="input input-bordered input-sm"
              />
              <button
                v-if="specificTimes.length > 1"
                class="btn btn-ghost btn-xs btn-square"
                @click="removeTime(index)"
              >
                <XMarkIcon class="h-4 w-4" />
              </button>
            </div>
          </div>
          <button
            class="btn btn-ghost btn-sm mt-2"
            @click="addTime"
          >
            <PlusIcon class="h-4 w-4" />
            Agregar horario
          </button>
        </div>
      </div>

      <!-- Once Config -->
      <div v-if="scheduleType === 'once'" class="mt-4">
        <label class="label"><span class="label-text">Fecha y hora:</span></label>
        <input
          v-model="onceDatetime"
          type="datetime-local"
          class="input input-bordered w-full"
        />
      </div>

      <!-- Date Range (for interval and specific) -->
      <div v-if="scheduleType !== 'once'" class="grid grid-cols-2 gap-4 mt-4">
        <div>
          <label class="label"><span class="label-text">Fecha inicio:</span></label>
          <input
            v-model="startDate"
            type="date"
            class="input input-bordered input-sm w-full"
            required
          />
        </div>
        <div>
          <label class="label"><span class="label-text">Fecha fin (opcional):</span></label>
          <input
            v-model="endDate"
            type="date"
            class="input input-bordered input-sm w-full"
          />
        </div>
      </div>

      <!-- Notes -->
      <div class="form-control mt-4">
        <label class="label"><span class="label-text">Notas (opcional):</span></label>
        <textarea
          v-model="notes"
          class="textarea textarea-bordered textarea-sm"
          rows="2"
          placeholder="Notas sobre esta programacion..."
        ></textarea>
      </div>

      <!-- Actions -->
      <div class="modal-action">
        <button class="btn btn-ghost" @click="close">
          Cancelar
        </button>
        <button
          class="btn btn-primary"
          :disabled="!isValid || isSaving"
          @click="save"
        >
          <span v-if="isSaving" class="loading loading-spinner loading-sm"></span>
          Guardar
        </button>
      </div>
    </div>

    <form method="dialog" class="modal-backdrop">
      <button @click="close">close</button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { CalendarIcon, XMarkIcon, PlusIcon } from '@heroicons/vue/24/outline'
import type { AudioMessage } from '@/types/audio'
import { libraryApi } from '../services/libraryApi'
import DaySelector from './DaySelector.vue'

const props = defineProps<{
  open: boolean
  message: AudioMessage | null
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'scheduled': [schedule: any]
}>()

const scheduleTypes = [
  { id: 'interval' as const, icon: '🔄', label: 'Intervalo' },
  { id: 'specific' as const, icon: '🕐', label: 'Especifico' },
  { id: 'once' as const, icon: '📅', label: 'Una vez' }
]

// Form state
const scheduleType = ref<'interval' | 'specific' | 'once'>('interval')
const intervalHours = ref(4)
const intervalMinutes = ref(0)
const startTime = ref('09:00')
const endTime = ref('18:00')
const selectedDays = ref([1, 2, 3, 4, 5]) // Mon-Fri
const specificTimes = ref(['09:00', '12:00', '18:00'])
const onceDatetime = ref('')
const startDate = ref('')
const endDate = ref('')
const notes = ref('')
const isSaving = ref(false)

// Set default start date
watch(() => props.open, (isOpen) => {
  if (isOpen) {
    const today = new Date().toISOString().split('T')[0]
    startDate.value = today
  }
})

const isValid = computed(() => {
  if (scheduleType.value === 'interval') {
    return (intervalHours.value > 0 || intervalMinutes.value > 0) &&
           selectedDays.value.length > 0 &&
           startDate.value
  }
  if (scheduleType.value === 'specific') {
    return selectedDays.value.length > 0 &&
           specificTimes.value.length > 0 &&
           startDate.value
  }
  if (scheduleType.value === 'once') {
    return !!onceDatetime.value
  }
  return false
})

function addTime() {
  specificTimes.value.push('12:00')
}

function removeTime(index: number) {
  specificTimes.value.splice(index, 1)
}

async function save() {
  if (!props.message || !isValid.value) return

  isSaving.value = true

  try {
    const data: any = {
      audio_message_id: props.message.id,
      schedule_type: scheduleType.value,
      start_date: scheduleType.value === 'once' ? onceDatetime.value.split('T')[0] : startDate.value,
      end_date: endDate.value || undefined,
      notes: notes.value || undefined
    }

    if (scheduleType.value === 'interval') {
      data.interval_hours = intervalHours.value
      data.interval_minutes = intervalMinutes.value
      data.schedule_days = selectedDays.value
      data.schedule_times = [startTime.value, endTime.value]
    } else if (scheduleType.value === 'specific') {
      data.schedule_days = selectedDays.value
      data.schedule_times = specificTimes.value
    } else if (scheduleType.value === 'once') {
      data.once_datetime = onceDatetime.value
    }

    const schedule = await libraryApi.createSchedule(data)
    emit('scheduled', schedule)
    close()
  } catch (err: any) {
    console.error('Error creating schedule:', err)
  } finally {
    isSaving.value = false
  }
}

function close() {
  emit('update:open', false)
}
</script>
