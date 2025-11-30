<template>
  <div class="min-h-screen bg-base-100 p-6">
    <div class="container mx-auto max-w-7xl">
      <!-- Header -->
      <CalendarHeader
        :current-date="store.currentDate"
        :active-count="store.activeSchedules.length"
        :view-mode="store.viewMode"
        @previous="store.previousMonth"
        @next="store.nextMonth"
        @today="store.goToToday"
        @update:view-mode="store.setViewMode"
        @filter="handleFilter"
      />

      <!-- Loading -->
      <div v-if="store.isLoading" class="flex justify-center py-12">
        <span class="loading loading-spinner loading-lg text-primary"></span>
      </div>

      <!-- Content -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Calendar Grid (3 cols) -->
        <div class="lg:col-span-3">
          <CalendarGrid
            :days="store.calendarDays"
            @select-day="handleSelectDay"
            @select-schedule="handleSelectSchedule"
          />

          <!-- Legend -->
          <div class="flex items-center gap-4 mt-4 text-sm text-base-content/60">
            <div class="flex items-center gap-1">
              <span class="w-3 h-3 rounded border-l-2 border-info bg-info/20"></span>
              Intervalo
            </div>
            <div class="flex items-center gap-1">
              <span class="w-3 h-3 rounded border-l-2 border-success bg-success/20"></span>
              Especifico
            </div>
            <div class="flex items-center gap-1">
              <span class="w-3 h-3 rounded border-l-2 border-warning bg-warning/20"></span>
              Una vez
            </div>
          </div>
        </div>

        <!-- Sidebar (1 col) -->
        <div class="space-y-4">
          <!-- Schedule Detail -->
          <ScheduleDetail
            v-if="store.selectedSchedule"
            :schedule="store.selectedSchedule"
            @close="store.selectSchedule(null)"
            @toggle="handleToggle"
            @delete="confirmDelete"
          />

          <!-- Schedule List -->
          <ScheduleList
            :schedules="filteredSchedules"
            @select="handleSelectSchedule"
            @toggle="handleToggle"
            @delete="confirmDelete"
          />
        </div>
      </div>

      <!-- Error Toast -->
      <div v-if="store.error" class="toast toast-end">
        <div class="alert alert-error">
          <span>{{ store.error }}</span>
          <button class="btn btn-ghost btn-xs" @click="store.clearError">x</button>
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <dialog class="modal" :class="{ 'modal-open': showDeleteModal }">
        <div class="modal-box">
          <h3 class="font-bold text-lg">Eliminar Programacion</h3>
          <p class="py-4">
            ¿Estas seguro de que deseas eliminar esta programacion?
            Esta accion no se puede deshacer.
          </p>
          <div class="modal-action">
            <button class="btn btn-ghost" @click="showDeleteModal = false">
              Cancelar
            </button>
            <button
              class="btn btn-error"
              :disabled="isDeleting"
              @click="executeDelete"
            >
              <span v-if="isDeleting" class="loading loading-spinner loading-sm"></span>
              Eliminar
            </button>
          </div>
        </div>
        <form method="dialog" class="modal-backdrop">
          <button @click="showDeleteModal = false">close</button>
        </form>
      </dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { Schedule, CalendarDay, CalendarFilters } from './types/calendar.types'

// Store
import { useCalendarStore } from './stores/calendarStore'

// Components
import CalendarHeader from './components/CalendarHeader.vue'
import CalendarGrid from './components/CalendarGrid.vue'
import ScheduleList from './components/ScheduleList.vue'
import ScheduleDetail from './components/ScheduleDetail.vue'

const store = useCalendarStore()

// Local state
const showDeleteModal = ref(false)
const pendingDeleteId = ref<number | null>(null)
const isDeleting = ref(false)
const filters = ref<Partial<CalendarFilters>>({})

// Computed
const filteredSchedules = computed(() => {
  let result = store.schedules

  if (filters.value.active !== null && filters.value.active !== undefined) {
    result = result.filter(s => s.active === filters.value.active)
  }

  return result
})

// Handlers
function handleSelectDay(day: CalendarDay) {
  if (day.schedules.length === 1) {
    store.selectSchedule(day.schedules[0])
  } else if (day.schedules.length > 1) {
    // Could open a day detail modal in the future
    store.selectSchedule(day.schedules[0])
  }
}

function handleSelectSchedule(schedule: Schedule) {
  store.selectSchedule(schedule)
}

async function handleToggle(id: number) {
  await store.toggleScheduleActive(id)
}

function handleFilter(newFilters: Partial<CalendarFilters>) {
  filters.value = newFilters
}

function confirmDelete(id: number) {
  pendingDeleteId.value = id
  showDeleteModal.value = true
}

async function executeDelete() {
  if (!pendingDeleteId.value) return

  isDeleting.value = true
  try {
    await store.deleteSchedule(pendingDeleteId.value)
    showDeleteModal.value = false
    pendingDeleteId.value = null
  } finally {
    isDeleting.value = false
  }
}

// Load data on mount
onMounted(async () => {
  await store.fetchSchedules()
})
</script>
