<template>
  <!-- Desktop Sidebar Card (below header) -->
  <aside class="hidden lg:flex fixed top-24 left-4 bottom-4 w-60 bg-base-100 rounded-2xl shadow-theme-sm z-40 flex-col overflow-hidden">
    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto py-3">
      <ul class="menu px-3 gap-1">
        <li v-for="item in mainItems" :key="item.path">
          <router-link
            :to="item.path"
            class="nav-item"
            :class="{ 'active': isActive(item.path) }"
          >
            <component :is="item.icon" class="h-5 w-5" />
            <span>{{ item.label }}</span>
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- Bottom: Settings -->
    <div class="p-3 shrink-0">
      <ul class="menu px-0">
        <li>
          <router-link
            to="/settings"
            class="nav-item"
            :class="{ 'active': isActive('/settings') }"
          >
            <CogIcon class="h-5 w-5" />
            <span>Configuración</span>
          </router-link>
        </li>
      </ul>
    </div>
  </aside>

  <!-- Mobile Drawer -->
  <Teleport to="body">
    <!-- Overlay -->
    <div
      v-if="isSidebarOpen"
      class="fixed inset-0 bg-black/50 z-[60] transition-opacity duration-300 lg:hidden"
      :class="isSidebarVisible ? 'opacity-100' : 'opacity-0'"
      @click="closeSidebar"
    />

    <!-- Drawer -->
    <aside
      v-if="isSidebarOpen"
      class="fixed top-0 left-0 h-full w-72 bg-base-100 border-r border-base-content/10 shadow-lg z-[70] flex flex-col transition-transform duration-300 ease-out lg:hidden"
      :class="isSidebarVisible ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Drawer Header -->
      <div class="h-14 flex items-center justify-between px-5 shrink-0" style="background-color: #0171dc;">
        <img
          :src="tenantLogo"
          :alt="tenantName"
          class="h-8 w-auto object-contain"
        />
        <button
          @click="closeSidebar"
          class="btn btn-ghost btn-sm btn-square text-white"
          aria-label="Cerrar menú"
        >
          <XMarkIcon class="h-5 w-5" />
        </button>
      </div>

      <!-- Drawer Navigation -->
      <nav class="flex-1 overflow-y-auto py-4">
        <ul class="menu px-2 gap-1">
          <li v-for="item in allItems" :key="item.path">
            <router-link
              :to="item.path"
              class="nav-item"
              :class="{ 'active': isActive(item.path) }"
              @click="closeSidebar"
            >
              <component :is="item.icon" class="h-5 w-5" />
              <span>{{ item.label }}</span>
            </router-link>
          </li>
        </ul>
      </nav>
    </aside>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, markRaw, type Component } from 'vue'
import { useRoute } from 'vue-router'
import { useLayout } from '@/composables/useLayout'
import { useTenantStore } from '@/stores/tenant'
import {
  XMarkIcon,
  HomeIcon,
  BookOpenIcon,
  CalendarIcon,
  CogIcon,
  MegaphoneIcon,
  RocketLaunchIcon,
  MusicalNoteIcon,
  ChatBubbleLeftRightIcon,
} from '@heroicons/vue/24/outline'

interface MenuItem {
  path: string
  label: string
  icon: Component
}

const route = useRoute()
const tenantStore = useTenantStore()
const { isSidebarOpen, isSidebarVisible, closeSidebar } = useLayout()

const tenantLogo = computed(() => tenantStore.tenantLogo)
const tenantName = computed(() => tenantStore.tenantName)

// Main nav items (shown in desktop sidebar)
const mainItems: MenuItem[] = [
  { path: '/campaigns', label: 'Marketing', icon: markRaw(HomeIcon) },
  { path: '/operations', label: 'Operaciones', icon: markRaw(RocketLaunchIcon) },
  { path: '/music', label: 'Música', icon: markRaw(MusicalNoteIcon) },
  { path: '/calendar', label: 'Calendario', icon: markRaw(CalendarIcon) },
  { path: '/library', label: 'Librería', icon: markRaw(BookOpenIcon) },
  { path: '/chat', label: 'Asistente', icon: markRaw(ChatBubbleLeftRightIcon) },
]

// All items including settings (for mobile drawer)
const allItems: MenuItem[] = [
  ...mainItems,
  { path: '/settings', label: 'Configuración', icon: markRaw(CogIcon) },
]

const isActive = (path: string): boolean => {
  if (path === '/campaigns') {
    return route.path === '/' || route.path.startsWith('/campaigns')
  }
  return route.path.startsWith(path)
}
</script>

<style scoped>
.nav-item {
  @apply flex items-center gap-3 px-4 py-3 rounded-lg text-base-content/80;
  @apply hover:bg-base-300 hover:text-base-content transition-all duration-200;
}

.nav-item.active {
  @apply bg-primary/10 text-primary font-medium;
}
</style>
