<template>
  <div class="landing-page min-h-screen bg-base-100 flex flex-col">
    <!-- Logo Header -->
    <div class="py-6 flex flex-col items-center">
      <img
        src="/tenants/mallbarrio/logo.png"
        alt="Mall Barrio Independencia"
        class="h-16 w-auto object-contain"
      />
    </div>

    <!-- Buttons Grid -->
    <div class="flex-1 px-4 pb-8">
      <draggable
        v-model="sortedItems"
        item-key="id"
        class="grid grid-cols-2 gap-3 max-w-lg mx-auto"
        :animation="200"
        :delay="300"
        :delay-on-touch-only="true"
        :touch-start-threshold="10"
        ghost-class="dragging-ghost"
        drag-class="dragging-item"
        @end="saveOrder"
      >
        <template #item="{ element: item }">
          <button
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
        </template>
      </draggable>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, type Component } from 'vue'
import { useRouter } from 'vue-router'
import draggable from 'vuedraggable'
import {
  MusicalNoteIcon,
  TruckIcon,
  ClockIcon,
  SparklesIcon,
  BookOpenIcon,
  PhoneIcon,
  RocketLaunchIcon,
  ChatBubbleLeftIcon
} from '@heroicons/vue/24/outline'

interface MenuItem {
  id: string
  path: string
  label: string
  icon: Component
  color: string
  disabled?: boolean
}

const router = useRouter()

const STORAGE_KEY = 'landing-menu-order'

const defaultItems: MenuItem[] = [
  {
    id: 'music',
    path: '/music',
    label: 'Música',
    icon: MusicalNoteIcon,
    color: '#3B82F6'
  },
  {
    id: 'vehicles',
    path: '/operations/vehicles',
    label: 'Autos Mal Estacionados',
    icon: TruckIcon,
    color: '#3B82F6'
  },
  {
    id: 'schedules',
    path: '/operations/schedules',
    label: 'Horarios de Cierre',
    icon: ClockIcon,
    color: '#3B82F6'
  },
  {
    id: 'playroom',
    path: '/playroom',
    label: 'Playroom',
    icon: SparklesIcon,
    color: '#3B82F6'
  },
  {
    id: 'campaigns',
    path: '/campaigns',
    label: 'Campañas',
    icon: RocketLaunchIcon,
    color: '#3B82F6'
  },
  {
    id: 'library',
    path: '/library',
    label: 'Biblioteca',
    icon: BookOpenIcon,
    color: '#3B82F6'
  },
  {
    id: 'dashboard',
    path: '/dashboard',
    label: 'Crear Mensaje',
    icon: ChatBubbleLeftIcon,
    color: '#3B82F6'
  },
  {
    id: 'client-call',
    path: '/operations/employee-call',
    label: 'Llamado a Empleado',
    icon: PhoneIcon,
    color: '#3B82F6'
  },
]

const sortedItems = ref<MenuItem[]>([])

onMounted(() => {
  loadOrder()
})

function loadOrder() {
  const savedOrder = localStorage.getItem(STORAGE_KEY)
  if (savedOrder) {
    try {
      const orderIds = JSON.parse(savedOrder) as string[]
      // Reorder based on saved order, keeping new items at the end
      const ordered: MenuItem[] = []
      for (const id of orderIds) {
        const item = defaultItems.find(i => i.id === id)
        if (item) ordered.push(item)
      }
      // Add any new items not in saved order
      for (const item of defaultItems) {
        if (!ordered.find(i => i.id === item.id)) {
          ordered.push(item)
        }
      }
      sortedItems.value = ordered
    } catch {
      sortedItems.value = [...defaultItems]
    }
  } else {
    sortedItems.value = [...defaultItems]
  }
}

function saveOrder() {
  const orderIds = sortedItems.value.map(item => item.id)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(orderIds))
}

function navigate(path: string) {
  if (path) {
    router.push(path)
  }
}
</script>

<style scoped>
button:disabled {
  cursor: not-allowed;
}

.dragging-ghost {
  opacity: 0.5;
  background: oklch(var(--b2));
}

.dragging-item {
  transform: scale(1.05);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}
</style>
