<template>
  <header class="sticky top-0 z-50 bg-base-200 shadow-lg">
    <div class="container mx-auto px-4 py-4 max-w-[1600px]">
      <div class="flex items-center">
        <!-- Left: Burger Menu + Logo -->
        <div class="flex items-center gap-3">
          <!-- Burger Menu Button -->
          <button
            @click="openSidebar"
            class="btn btn-ghost btn-square"
            aria-label="Abrir menú"
          >
            <Bars3Icon class="h-6 w-6" />
          </button>

          <!-- Logo / Title -->
          <router-link
            to="/campaigns"
            class="flex items-center hover:opacity-80 transition-opacity"
          >
            <img
              src="/images/solo%20logo.png"
              alt="MediaFlow"
              class="h-10"
            />
            <span class="ml-3 text-2xl font-bold tracking-tight hidden sm:inline">
              <span class="text-primary">Media</span><span class="text-base-content">flow</span>
            </span>
          </router-link>
        </div>
      </div>
    </div>
  </header>

  <!-- Sidebar Drawer -->
  <Teleport to="body">
    <!-- Overlay -->
    <div
      v-if="isSidebarOpen"
      class="fixed inset-0 bg-black/50 z-[60] transition-opacity duration-300"
      :class="isSidebarVisible ? 'opacity-100' : 'opacity-0'"
      @click="closeSidebar"
    />

    <!-- Sidebar -->
    <aside
      v-if="isSidebarOpen"
      class="fixed top-0 left-0 h-full w-72 bg-base-200 shadow-2xl z-[70] flex flex-col transition-transform duration-300 ease-out"
      :class="isSidebarVisible ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Sidebar Header -->
      <div class="flex items-center justify-between p-4 border-b border-base-300">
        <div class="flex items-center gap-2">
          <img
            src="/images/solo%20logo.png"
            alt="MediaFlow"
            class="h-8"
          />
          <span class="text-xl font-bold">
            <span class="text-primary">Media</span><span class="text-base-content">flow</span>
          </span>
        </div>
        <button
          @click="closeSidebar"
          class="btn btn-ghost btn-sm btn-square"
          aria-label="Cerrar menú"
        >
          <XMarkIcon class="h-5 w-5" />
        </button>
      </div>

      <!-- Navigation Links -->
      <nav class="flex-1 overflow-y-auto py-4">
        <ul class="menu px-2 gap-1">
          <li v-for="item in menuItems" :key="item.path">
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

      <!-- Footer: Theme Selector -->
      <div class="border-t border-base-300 p-4">
        <div class="text-sm text-base-content/70 mb-3">Tema</div>
        <ThemeSelectorInline />
      </div>
    </aside>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, markRaw, type Component } from 'vue'
import { useRoute } from 'vue-router'
import {
  Bars3Icon,
  XMarkIcon,
  HomeIcon,
  BookOpenIcon,
  CalendarIcon,
  CogIcon,
  MegaphoneIcon,
  RocketLaunchIcon,
  DevicePhoneMobileIcon
} from '@heroicons/vue/24/outline'
import ThemeSelectorInline from './ThemeSelectorInline.vue'

interface MenuItem {
  path: string
  label: string
  icon: Component
}

const route = useRoute()

// Menu items
const menuItems: MenuItem[] = [
  { path: '/campaigns', label: 'Campañas', icon: markRaw(HomeIcon) },
  { path: '/dashboard', label: 'Anuncios', icon: markRaw(MegaphoneIcon) },
  { path: '/library', label: 'Biblioteca', icon: markRaw(BookOpenIcon) },
  { path: '/calendar', label: 'Calendario', icon: markRaw(CalendarIcon) },
  { path: '/operations', label: 'Operaciones', icon: markRaw(RocketLaunchIcon) },
  { path: '/mobile', label: 'Mobile', icon: markRaw(DevicePhoneMobileIcon) },
  { path: '/settings', label: 'Configuración', icon: markRaw(CogIcon) },
]

// Sidebar state - two-phase for animation
const isSidebarOpen = ref(false)
const isSidebarVisible = ref(false)

const openSidebar = () => {
  isSidebarOpen.value = true
  document.body.style.overflow = 'hidden'
  // Small delay to trigger CSS transition
  requestAnimationFrame(() => {
    isSidebarVisible.value = true
  })
}

const closeSidebar = () => {
  isSidebarVisible.value = false
  // Wait for animation to complete before removing from DOM
  setTimeout(() => {
    isSidebarOpen.value = false
    document.body.style.overflow = ''
  }, 300)
}

const isActive = (path: string): boolean => {
  if (path === '/campaigns') {
    return route.path === '/' || route.path.startsWith('/campaigns')
  }
  return route.path.startsWith(path)
}

// Close on escape key
const handleEscape = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && isSidebarOpen.value) {
    closeSidebar()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
  document.body.style.overflow = ''
})

// Close sidebar on route change
watch(() => route.path, () => {
  if (isSidebarOpen.value) {
    closeSidebar()
  }
})
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
