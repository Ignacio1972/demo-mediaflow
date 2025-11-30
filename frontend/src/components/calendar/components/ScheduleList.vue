<template>
  <div class="bg-base-100 rounded-lg border border-base-300">
    <div class="p-4 border-b border-base-300">
      <h3 class="font-semibold text-base-content">
        Todas las Programaciones ({{ schedules.length }})
      </h3>
    </div>

    <div v-if="schedules.length === 0" class="p-8 text-center text-base-content/60">
      <CalendarIcon class="h-12 w-12 mx-auto mb-2 opacity-40" />
      <p>No hay programaciones</p>
      <p class="text-sm">Crea una desde la Biblioteca</p>
    </div>

    <div v-else class="divide-y divide-base-300 max-h-[400px] overflow-y-auto">
      <div
        v-for="schedule in schedules"
        :key="schedule.id"
        class="p-3 hover:bg-base-200/50 transition-colors cursor-pointer"
        @click="$emit('select', schedule)"
      >
        <div class="flex items-start justify-between gap-2">
          <!-- Left: Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="text-lg">{{ getTypeIcon(schedule.schedule_type) }}</span>
              <span class="font-medium truncate">
                Audio #{{ schedule.audio_message_id }}
              </span>
              <span
                class="badge badge-xs"
                :class="schedule.active ? 'badge-success' : 'badge-ghost'"
              >
                {{ schedule.active ? 'Activo' : 'Inactivo' }}
              </span>
            </div>

            <div class="text-sm text-base-content/60 mt-1">
              {{ getScheduleDescription(schedule) }}
            </div>

            <div class="text-xs text-base-content/40 mt-1">
              Desde {{ formatDate(schedule.start_date) }}
              <template v-if="schedule.end_date">
                hasta {{ formatDate(schedule.end_date) }}
              </template>
            </div>
          </div>

          <!-- Right: Actions -->
          <div class="flex items-center gap-1">
            <button
              class="btn btn-ghost btn-xs btn-square"
              :class="schedule.active ? 'text-success' : 'text-base-content/40'"
              title="Toggle activo"
              @click.stop="$emit('toggle', schedule.id)"
            >
              <PlayCircleIcon v-if="schedule.active" class="h-4 w-4" />
              <PauseCircleIcon v-else class="h-4 w-4" />
            </button>

            <button
              class="btn btn-ghost btn-xs btn-square text-error"
              title="Eliminar"
              @click.stop="$emit('delete', schedule.id)"
            >
              <TrashIcon class="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  CalendarIcon,
  PlayCircleIcon,
  PauseCircleIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'
import type { Schedule } from '../types/calendar.types'

defineProps<{
  schedules: Schedule[]
}>()

defineEmits<{
  select: [schedule: Schedule]
  toggle: [id: number]
  delete: [id: number]
}>()

function getTypeIcon(type: string): string {
  return {
    interval: '\uD83D\uDD04',
    specific: '\uD83D\uDD50',
    once: '\uD83D\uDCC5'
  }[type] || '\uD83D\uDCC5'
}

function getScheduleDescription(schedule: Schedule): string {
  if (schedule.schedule_type === 'interval') {
    const mins = schedule.interval_minutes || 0
    const hours = Math.floor(mins / 60)
    const remainingMins = mins % 60

    if (hours > 0 && remainingMins > 0) {
      return `Cada ${hours}h ${remainingMins}min`
    } else if (hours > 0) {
      return `Cada ${hours} hora${hours > 1 ? 's' : ''}`
    }
    return `Cada ${mins} minutos`
  }

  if (schedule.schedule_type === 'specific' && schedule.specific_times) {
    const times = schedule.specific_times.slice(0, 3).join(', ')
    const more = schedule.specific_times.length > 3
      ? ` (+${schedule.specific_times.length - 3})`
      : ''
    return `A las ${times}${more}`
  }

  if (schedule.schedule_type === 'once') {
    return 'Reproduccion unica'
  }

  return 'Programado'
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('es-CL', {
    day: '2-digit',
    month: 'short'
  })
}
</script>
