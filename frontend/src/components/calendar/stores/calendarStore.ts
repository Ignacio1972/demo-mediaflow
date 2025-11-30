import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Schedule, CalendarDay, CalendarViewMode } from '../types/calendar.types'
import { calendarApi } from '../services/calendarApi'

export const useCalendarStore = defineStore('calendar', () => {
  // State
  const schedules = ref<Schedule[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const currentDate = ref(new Date())
  const viewMode = ref<CalendarViewMode>('month')
  const selectedSchedule = ref<Schedule | null>(null)

  // Computed
  const currentMonth = computed(() => currentDate.value.getMonth())
  const currentYear = computed(() => currentDate.value.getFullYear())

  const activeSchedules = computed(() =>
    schedules.value.filter(s => s.active)
  )

  const inactiveSchedules = computed(() =>
    schedules.value.filter(s => !s.active)
  )

  // Generate calendar days for current month view
  const calendarDays = computed((): CalendarDay[] => {
    const year = currentYear.value
    const month = currentMonth.value
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    // First day of the month
    const firstDay = new Date(year, month, 1)
    // Last day of the month
    const lastDay = new Date(year, month + 1, 0)

    // Start from Monday of the week containing the first day
    const startDate = new Date(firstDay)
    const dayOfWeek = firstDay.getDay()
    // Adjust for Monday start (0 = Monday, 6 = Sunday)
    const mondayOffset = dayOfWeek === 0 ? 6 : dayOfWeek - 1
    startDate.setDate(startDate.getDate() - mondayOffset)

    // End on Sunday of the week containing the last day
    const endDate = new Date(lastDay)
    const lastDayOfWeek = lastDay.getDay()
    const sundayOffset = lastDayOfWeek === 0 ? 0 : 7 - lastDayOfWeek
    endDate.setDate(endDate.getDate() + sundayOffset)

    const days: CalendarDay[] = []
    const current = new Date(startDate)

    while (current <= endDate) {
      const date = new Date(current)
      const daySchedules = getSchedulesForDate(date)

      days.push({
        date,
        dayOfMonth: date.getDate(),
        isCurrentMonth: date.getMonth() === month,
        isToday: date.getTime() === today.getTime(),
        schedules: daySchedules
      })

      current.setDate(current.getDate() + 1)
    }

    return days
  })

  // Get schedules that apply to a specific date
  function getSchedulesForDate(date: Date): Schedule[] {
    const dayOfWeek = date.getDay()
    // Convert Sunday=0 to our format (Monday=0)
    const adjustedDay = dayOfWeek === 0 ? 6 : dayOfWeek - 1

    return schedules.value.filter(schedule => {
      if (!schedule.active) return false

      const startDate = new Date(schedule.start_date)
      startDate.setHours(0, 0, 0, 0)

      const endDate = schedule.end_date ? new Date(schedule.end_date) : null
      if (endDate) endDate.setHours(23, 59, 59, 999)

      // Check if date is within schedule range
      if (date < startDate) return false
      if (endDate && date > endDate) return false

      // Check schedule type
      if (schedule.schedule_type === 'once') {
        // For once, check if the date matches start_date
        const scheduleDate = new Date(schedule.start_date)
        scheduleDate.setHours(0, 0, 0, 0)
        const checkDate = new Date(date)
        checkDate.setHours(0, 0, 0, 0)
        return scheduleDate.getTime() === checkDate.getTime()
      }

      // For interval and specific, check days_of_week
      if (schedule.days_of_week && schedule.days_of_week.length > 0) {
        return schedule.days_of_week.includes(adjustedDay)
      }

      return true
    })
  }

  // Actions
  async function fetchSchedules() {
    isLoading.value = true
    error.value = null

    try {
      const response = await calendarApi.getSchedules()
      schedules.value = response.data
    } catch (err: any) {
      error.value = err.message || 'Error al cargar programaciones'
      console.error('Error fetching schedules:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function toggleScheduleActive(id: number) {
    const schedule = schedules.value.find(s => s.id === id)
    if (!schedule) return

    try {
      const response = await calendarApi.toggleActive(id, !schedule.active)
      const index = schedules.value.findIndex(s => s.id === id)
      if (index !== -1) {
        schedules.value[index] = response.data
      }
    } catch (err: any) {
      error.value = err.message || 'Error al actualizar programacion'
    }
  }

  async function deleteSchedule(id: number) {
    try {
      await calendarApi.deleteSchedule(id)
      schedules.value = schedules.value.filter(s => s.id !== id)
    } catch (err: any) {
      error.value = err.message || 'Error al eliminar programacion'
    }
  }

  function previousMonth() {
    const newDate = new Date(currentDate.value)
    newDate.setMonth(newDate.getMonth() - 1)
    currentDate.value = newDate
  }

  function nextMonth() {
    const newDate = new Date(currentDate.value)
    newDate.setMonth(newDate.getMonth() + 1)
    currentDate.value = newDate
  }

  function goToToday() {
    currentDate.value = new Date()
  }

  function setViewMode(mode: CalendarViewMode) {
    viewMode.value = mode
  }

  function selectSchedule(schedule: Schedule | null) {
    selectedSchedule.value = schedule
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    schedules,
    isLoading,
    error,
    currentDate,
    viewMode,
    selectedSchedule,

    // Computed
    currentMonth,
    currentYear,
    activeSchedules,
    inactiveSchedules,
    calendarDays,

    // Actions
    fetchSchedules,
    toggleScheduleActive,
    deleteSchedule,
    previousMonth,
    nextMonth,
    goToToday,
    setViewMode,
    selectSchedule,
    clearError,
    getSchedulesForDate
  }
})
