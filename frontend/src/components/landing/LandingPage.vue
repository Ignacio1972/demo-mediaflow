<template>
  <div class="landing-page min-h-screen bg-base-100 flex flex-col">
    <!-- Logo Header -->
    <div class="py-8 text-center">
      <span class="text-3xl font-semibold tracking-tight">
        <span style="color: #00adef">Media</span><span class="text-base-content">Flow</span>
      </span>
    </div>

    <!-- Buttons Grid -->
    <div class="flex-1 px-4 pb-8">
      <div class="grid grid-cols-2 gap-3 max-w-lg mx-auto">
        <button
          v-for="item in menuItems"
          :key="item.path"
          class="group relative bg-base-100 border-2 border-base-300 rounded-xl flex flex-col items-center justify-center text-center p-4 transition-all duration-200 active:scale-95"
          :class="{ 'opacity-40': item.disabled }"
          :disabled="item.disabled"
          @click="navigate(item.path)"
        >
          <!-- Icon Container -->
          <div
            class="flex items-center justify-center w-14 h-14 rounded-xl mb-3 transition-all"
            :style="{ backgroundColor: `${item.color}15` }"
          >
            <component
              :is="item.icon"
              class="w-7 h-7"
              :style="{ color: item.color }"
            />
          </div>
          <!-- Label -->
          <span class="text-sm font-semibold text-base-content leading-tight">
            {{ item.label }}
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { type Component } from 'vue'
import {
  MusicalNoteIcon,
  TruckIcon,
  ClockIcon,
  ChatBubbleLeftIcon,
  BookOpenIcon,
  PhoneIcon
} from '@heroicons/vue/24/outline'

interface MenuItem {
  path: string
  label: string
  icon: Component
  color: string
  disabled?: boolean
}

const router = useRouter()

const menuItems: MenuItem[] = [
  {
    path: '/music',
    label: 'Música',
    icon: MusicalNoteIcon,
    color: '#3B82F6'
  },
  {
    path: '/operations/vehicles',
    label: 'Autos Mal Estacionados',
    icon: TruckIcon,
    color: '#3B82F6'
  },
  {
    path: '/operations/schedules',
    label: 'Horarios de Cierre',
    icon: ClockIcon,
    color: '#3B82F6'
  },
  {
    path: '/mobile',
    label: 'Crear Mensaje',
    icon: ChatBubbleLeftIcon,
    color: '#3B82F6'
  },
  {
    path: '/library',
    label: 'Biblioteca',
    icon: BookOpenIcon,
    color: '#3B82F6'
  },
  {
    path: '',
    label: 'Llamado al Cliente',
    icon: PhoneIcon,
    color: '#3B82F6',
    disabled: true
  },
]

const navigate = (path: string) => {
  if (path) {
    router.push(path)
  }
}
</script>

<style scoped>
button:disabled {
  cursor: not-allowed;
}
</style>
