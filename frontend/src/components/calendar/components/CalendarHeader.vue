<template>
  <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-10">
    <!-- Title -->
    <div>
      <div class="flex items-center gap-3 mb-2">
        <div class="flex items-center justify-center w-10 h-10 bg-primary/10 rounded-xl">
          <CalendarDaysIcon class="w-5 h-5 text-primary" />
        </div>
        <h1 class="text-3xl font-bold tracking-tight">Calendario</h1>
      </div>
      <p class="text-base-content/50 ml-13">
        {{ activeCount }} programaciones activas
      </p>
    </div>

    <!-- Controls -->
    <div class="flex flex-wrap items-center gap-2">
      <!-- Month Navigation -->
      <div class="join">
        <button
          class="btn btn-sm join-item"
          @click="$emit('previous')"
        >
          <ChevronLeftIcon class="h-4 w-4" />
        </button>
        <button
          class="btn btn-sm join-item min-w-[140px]"
          @click="$emit('today')"
        >
          {{ monthYear }}
        </button>
        <button
          class="btn btn-sm join-item"
          @click="$emit('next')"
        >
          <ChevronRightIcon class="h-4 w-4" />
        </button>
      </div>

      <!-- Today Button -->
      <button
        class="btn btn-sm btn-outline"
        @click="$emit('today')"
      >
        Hoy
      </button>

      <!-- View Mode Toggle (future) -->
      <!--
      <div class="btn-group">
        <button
          class="btn btn-sm"
          :class="viewMode === 'month' ? 'btn-active' : ''"
          @click="$emit('update:viewMode', 'month')"
        >
          Mes
        </button>
        <button
          class="btn btn-sm"
          :class="viewMode === 'week' ? 'btn-active' : ''"
          @click="$emit('update:viewMode', 'week')"
        >
          Semana
        </button>
      </div>
      -->

      <!-- Filter Active/Inactive -->
      <div class="dropdown dropdown-end">
        <label tabindex="0" class="btn btn-sm btn-ghost">
          <FunnelIcon class="h-4 w-4" />
          Filtros
        </label>
        <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
          <li>
            <a @click="$emit('filter', { active: null })">
              Todas
            </a>
          </li>
          <li>
            <a @click="$emit('filter', { active: true })">
              Solo activas
            </a>
          </li>
          <li>
            <a @click="$emit('filter', { active: false })">
              Solo inactivas
            </a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  CalendarDaysIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  FunnelIcon
} from '@heroicons/vue/24/outline'

const props = defineProps<{
  currentDate: Date
  activeCount: number
  viewMode: string
}>()

defineEmits<{
  previous: []
  next: []
  today: []
  'update:viewMode': [mode: string]
  filter: [filters: { active: boolean | null }]
}>()

const monthYear = computed(() => {
  const months = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ]
  return `${months[props.currentDate.getMonth()]} ${props.currentDate.getFullYear()}`
})
</script>
