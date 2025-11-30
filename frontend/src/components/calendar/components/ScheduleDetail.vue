<template>
  <div class="bg-base-100 rounded-lg border border-base-300">
    <div class="p-4 border-b border-base-300 flex items-center justify-between">
      <h3 class="font-semibold text-base-content">
        Detalle de Programacion
      </h3>
      <button
        class="btn btn-ghost btn-xs btn-square"
        @click="$emit('close')"
      >
        <XMarkIcon class="h-4 w-4" />
      </button>
    </div>

    <div v-if="!schedule" class="p-8 text-center text-base-content/60">
      <InformationCircleIcon class="h-12 w-12 mx-auto mb-2 opacity-40" />
      <p>Selecciona una programacion</p>
    </div>

    <div v-else class="p-4 space-y-4">
      <!-- Type Badge -->
      <div class="flex items-center gap-2">
        <span class="text-2xl">{{ getTypeIcon(schedule.schedule_type) }}</span>
        <div>
          <div class="font-medium">{{ getTypeName(schedule.schedule_type) }}</div>
          <span
            class="badge badge-sm"
            :class="schedule.active ? 'badge-success' : 'badge-ghost'"
          >
            {{ schedule.active ? 'Activo' : 'Inactivo' }}
          </span>
        </div>
      </div>

      <!-- Audio Info -->
      <div class="bg-base-200 rounded-lg p-3">
        <div class="text-sm text-base-content/60">Audio</div>
        <div class="font-medium">
          ID #{{ schedule.audio_message_id }}
        </div>
      </div>

      <!-- Schedule Details -->
      <div class="space-y-2">
        <!-- Interval -->
        <div v-if="schedule.schedule_type === 'interval'" class="text-sm">
          <div class="text-base-content/60">Intervalo</div>
          <div>{{ getIntervalText(schedule) }}</div>
        </div>

        <!-- Specific Times -->
        <div v-if="schedule.specific_times?.length" class="text-sm">
          <div class="text-base-content/60">Horarios</div>
          <div class="flex flex-wrap gap-1 mt-1">
            <span
              v-for="time in schedule.specific_times"
              :key="time"
              class="badge badge-outline badge-sm"
            >
              {{ time }}
            </span>
          </div>
        </div>

        <!-- Days of Week -->
        <div v-if="schedule.days_of_week?.length" class="text-sm">
          <div class="text-base-content/60">Dias</div>
          <div class="flex gap-1 mt-1">
            <span
              v-for="(day, idx) in weekDays"
              :key="idx"
              class="w-8 h-8 rounded-full flex items-center justify-center text-xs"
              :class="schedule.days_of_week.includes(idx)
                ? 'bg-primary text-primary-content'
                : 'bg-base-200 text-base-content/40'"
            >
              {{ day }}
            </span>
          </div>
        </div>

        <!-- Date Range -->
        <div class="text-sm">
          <div class="text-base-content/60">Periodo</div>
          <div>
            {{ formatDate(schedule.start_date) }}
            <template v-if="schedule.end_date">
              - {{ formatDate(schedule.end_date) }}
            </template>
            <template v-else>
              (sin fecha fin)
            </template>
          </div>
        </div>

        <!-- Priority -->
        <div class="text-sm">
          <div class="text-base-content/60">Prioridad</div>
          <div class="flex items-center gap-1">
            <span
              v-for="i in 5"
              :key="i"
              class="w-2 h-2 rounded-full"
              :class="i <= schedule.priority ? 'bg-warning' : 'bg-base-300'"
            ></span>
            <span class="ml-1">{{ schedule.priority }}/5</span>
          </div>
        </div>

        <!-- Last/Next Execution -->
        <div v-if="schedule.last_executed_at" class="text-sm">
          <div class="text-base-content/60">Ultima ejecucion</div>
          <div>{{ formatDateTime(schedule.last_executed_at) }}</div>
        </div>

        <div v-if="schedule.next_execution_at" class="text-sm">
          <div class="text-base-content/60">Proxima ejecucion</div>
          <div>{{ formatDateTime(schedule.next_execution_at) }}</div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex gap-2 pt-4 border-t border-base-300">
        <button
          class="btn btn-sm flex-1"
          :class="schedule.active ? 'btn-warning' : 'btn-success'"
          @click="$emit('toggle', schedule.id)"
        >
          {{ schedule.active ? 'Pausar' : 'Activar' }}
        </button>
        <button
          class="btn btn-sm btn-error btn-outline"
          @click="$emit('delete', schedule.id)"
        >
          <TrashIcon class="h-4 w-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  XMarkIcon,
  InformationCircleIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'
import type { Schedule } from '../types/calendar.types'

defineProps<{
  schedule: Schedule | null
}>()

defineEmits<{
  close: []
  toggle: [id: number]
  delete: [id: number]
}>()

const weekDays = ['L', 'M', 'X', 'J', 'V', 'S', 'D']

function getTypeIcon(type: string): string {
  return {
    interval: '\uD83D\uDD04',
    specific: '\uD83D\uDD50',
    once: '\uD83D\uDCC5'
  }[type] || '\uD83D\uDCC5'
}

function getTypeName(type: string): string {
  return {
    interval: 'Intervalo',
    specific: 'Horarios Especificos',
    once: 'Una Vez'
  }[type] || type
}

function getIntervalText(schedule: Schedule): string {
  const mins = schedule.interval_minutes || 0
  const hours = Math.floor(mins / 60)
  const remainingMins = mins % 60

  if (hours > 0 && remainingMins > 0) {
    return `Cada ${hours} hora${hours > 1 ? 's' : ''} y ${remainingMins} minutos`
  } else if (hours > 0) {
    return `Cada ${hours} hora${hours > 1 ? 's' : ''}`
  }
  return `Cada ${mins} minutos`
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('es-CL', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}

function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('es-CL', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
