<template>
  <div class="landing-page min-h-screen bg-base-100 flex flex-col">
    <!-- Logo Header -->
    <div class="py-8 text-center">
      <span class="text-3xl font-light tracking-tight">
        <span style="color: #00adef">Media</span><span class="text-base-content">Flow</span>
      </span>
    </div>

    <!-- Buttons Grid -->
    <div class="flex-1 px-4 pb-8">
      <div class="grid grid-cols-2 gap-4 max-w-lg mx-auto">
        <button
          v-for="item in menuItems"
          :key="item.path"
          class="landing-button aspect-square rounded-xl flex flex-col items-center justify-center text-center p-4 transition-all active:scale-95 shadow-sm"
          :style="getButtonStyle(item.color)"
          :disabled="item.disabled"
          @click="navigate(item.path)"
        >
          <component :is="item.icon" class="w-10 h-10 mb-3 stroke-1" />
          <span class="text-sm font-medium leading-tight">{{ item.label }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { markRaw, type Component } from 'vue'
import { useRouter } from 'vue-router'
import {
  MusicalNoteIcon,
  TruckIcon,
  ClockIcon,
  ChatBubbleLeftIcon,
  BookOpenIcon,
  PhoneIcon,
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
    icon: markRaw(MusicalNoteIcon),
    color: '#10B981'
  },
  {
    path: '/operations/vehicles',
    label: 'Autos Mal Estacionados',
    icon: markRaw(TruckIcon),
    color: '#EF4444'
  },
  {
    path: '/operations/schedules',
    label: 'Horarios de Cierre',
    icon: markRaw(ClockIcon),
    color: '#3B82F6'
  },
  {
    path: '/mobile',
    label: 'Crear Mensaje',
    icon: markRaw(ChatBubbleLeftIcon),
    color: '#8B5CF6'
  },
  {
    path: '/library',
    label: 'Biblioteca',
    icon: markRaw(BookOpenIcon),
    color: '#F59E0B'
  },
  {
    path: '',
    label: 'Llamado al Cliente',
    icon: markRaw(PhoneIcon),
    color: '#6B7280',
    disabled: true
  },
]

const getButtonStyle = (color: string) => ({
  backgroundColor: `${color}15`,
  borderColor: `${color}40`,
  border: '1px solid',
})

const navigate = (path: string) => {
  if (path) {
    router.push(path)
  }
}
</script>

<style scoped>
.landing-button {
  min-height: 140px;
}

.landing-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
