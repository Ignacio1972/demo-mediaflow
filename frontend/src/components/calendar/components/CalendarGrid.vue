<template>
  <div class="bg-base-100 rounded-lg border border-base-300 overflow-hidden">
    <!-- Days Header -->
    <div class="grid grid-cols-7 bg-base-200">
      <div
        v-for="day in weekDays"
        :key="day"
        class="py-2 text-center text-sm font-medium text-base-content/70"
      >
        {{ day }}
      </div>
    </div>

    <!-- Calendar Grid -->
    <div class="grid grid-cols-7">
      <div
        v-for="(day, index) in days"
        :key="index"
        class="min-h-[100px] border-t border-l border-base-300 p-1 cursor-pointer hover:bg-base-200/50 transition-colors"
        :class="{
          'bg-base-200/30': !day.isCurrentMonth,
          'bg-primary/5': day.isToday
        }"
        @click="$emit('select-day', day)"
      >
        <!-- Day Number -->
        <div class="flex items-center justify-between mb-1">
          <span
            class="text-sm font-medium w-6 h-6 flex items-center justify-center rounded-full"
            :class="{
              'text-base-content/40': !day.isCurrentMonth,
              'bg-primary text-primary-content': day.isToday,
              'text-base-content': day.isCurrentMonth && !day.isToday
            }"
          >
            {{ day.dayOfMonth }}
          </span>

          <!-- Schedule Count Badge -->
          <span
            v-if="day.schedules.length > 0"
            class="badge badge-sm badge-primary"
          >
            {{ day.schedules.length }}
          </span>
        </div>

        <!-- Schedule Pills (max 3 visible) -->
        <div class="space-y-0.5">
          <div
            v-for="schedule in day.schedules.slice(0, 3)"
            :key="schedule.id"
            class="text-xs px-1.5 py-0.5 rounded truncate cursor-pointer hover:opacity-80"
            :class="getScheduleClass(schedule)"
            :title="getScheduleTitle(schedule)"
            @click.stop="$emit('select-schedule', schedule)"
          >
            {{ getScheduleIcon(schedule) }} {{ getScheduleLabel(schedule) }}
          </div>

          <!-- More indicator -->
          <div
            v-if="day.schedules.length > 3"
            class="text-xs text-base-content/60 px-1.5"
          >
            +{{ day.schedules.length - 3 }} mas
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CalendarDay, Schedule } from '../types/calendar.types'

defineProps<{
  days: CalendarDay[]
}>()

defineEmits<{
  'select-day': [day: CalendarDay]
  'select-schedule': [schedule: Schedule]
}>()

const weekDays = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom']

function getScheduleClass(schedule: Schedule): string {
  const baseClass = schedule.active
    ? 'bg-primary/20 text-primary-content'
    : 'bg-base-300 text-base-content/60'

  const typeClass = {
    interval: 'border-l-2 border-info',
    specific: 'border-l-2 border-success',
    once: 'border-l-2 border-warning'
  }[schedule.schedule_type]

  return `${baseClass} ${typeClass}`
}

function getScheduleIcon(schedule: Schedule): string {
  return {
    interval: '\uD83D\uDD04',
    specific: '\uD83D\uDD50',
    once: '\uD83D\uDCC5'
  }[schedule.schedule_type]
}

function getScheduleLabel(schedule: Schedule): string {
  if (schedule.schedule_type === 'interval') {
    const mins = schedule.interval_minutes || 0
    if (mins >= 60) {
      return `c/${Math.floor(mins / 60)}h`
    }
    return `c/${mins}m`
  }

  if (schedule.schedule_type === 'specific' && schedule.specific_times) {
    return schedule.specific_times[0] || 'Especifico'
  }

  if (schedule.schedule_type === 'once') {
    return 'Una vez'
  }

  return 'Programado'
}

function getScheduleTitle(schedule: Schedule): string {
  let title = `ID: ${schedule.id}\n`
  title += `Tipo: ${schedule.schedule_type}\n`
  title += `Estado: ${schedule.active ? 'Activo' : 'Inactivo'}`

  if (schedule.specific_times?.length) {
    title += `\nHorarios: ${schedule.specific_times.join(', ')}`
  }

  return title
}
</script>
