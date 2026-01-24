<template>
  <header class="sticky top-0 z-50 bg-base-200 shadow-lg">
    <div class="container mx-auto px-4 py-4 max-w-[1600px]">
      <div class="flex items-center justify-between gap-3">
        <!-- Left: Home (mobile) or Burger Menu (desktop) -->
        <button
          v-if="isMobile"
          @click="goToLanding"
          class="btn btn-ghost btn-square"
          aria-label="Ir a inicio"
        >
          <HomeIcon class="h-8 w-8" />
        </button>
        <button
          v-else
          @click="openSidebar"
          class="btn btn-ghost btn-square"
          aria-label="Abrir menú"
        >
          <Bars3Icon class="h-6 w-6" />
        </button>

        <!-- Logo / Title -->
        <router-link
          :to="isMobile ? '/landing' : '/campaigns'"
          class="flex items-center hover:opacity-80 transition-opacity"
        >
          <span class="text-xl md:text-2xl font-semibold tracking-tight">
            <span style="color: #00adef">Media</span><span class="text-base-content">Flow</span>
          </span>
        </router-link>

        <!-- Spacer -->
        <div class="flex-1"></div>

        <!-- Right: Theme Buttons -->
        <div class="flex items-center gap-1">
          <button
            v-for="theme in themes"
            :key="theme.id"
            @click="changeTheme(theme.id)"
            class="btn btn-ghost btn-sm btn-square"
            :class="{ 'btn-active': currentTheme === theme.id }"
            :title="theme.name"
          >
            <component :is="theme.icon" class="w-5 h-5" />
          </button>
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
        <span class="text-xl font-semibold tracking-tight">
          <span style="color: #00adef">Media</span><span class="text-base-content">Flow</span>
        </span>
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

    </aside>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, markRaw, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { isMobileDevice } from '@/composables/useMobileDevice'
import {
  Bars3Icon,
  XMarkIcon,
  HomeIcon,
  BookOpenIcon,
  CalendarIcon,
  CogIcon,
  MegaphoneIcon,
  RocketLaunchIcon,
  DevicePhoneMobileIcon,
  MusicalNoteIcon,
  BoltIcon,
  MoonIcon,
  SunIcon
} from '@heroicons/vue/24/outline'

interface MenuItem {
  path: string
  label: string
  icon: Component
}

interface ThemeOption {
  id: string
  name: string
  icon: Component
}

const route = useRoute()
const router = useRouter()

// Mobile detection (User-Agent based, not viewport)
const isMobile = isMobileDevice()

const goToLanding = () => {
  router.push('/landing')
}

// Menu items
const menuItems: MenuItem[] = [
  { path: '/landing', label: 'Landing', icon: markRaw(DevicePhoneMobileIcon) },
  { path: '/campaigns', label: 'Campañas', icon: markRaw(HomeIcon) },
  { path: '/library', label: 'Biblioteca', icon: markRaw(BookOpenIcon) },
  { path: '/dashboard', label: 'Crear', icon: markRaw(MegaphoneIcon) },
  { path: '/calendar', label: 'Calendario', icon: markRaw(CalendarIcon) },
  { path: '/music', label: 'Música', icon: markRaw(MusicalNoteIcon) },
  { path: '/operations', label: 'Operaciones', icon: markRaw(RocketLaunchIcon) },
  { path: '/shortcuts', label: 'Shortcuts', icon: markRaw(BoltIcon) },
  { path: '/playroom', label: 'Playroom', icon: markRaw(DevicePhoneMobileIcon) },
  { path: '/settings', label: 'Configuración', icon: markRaw(CogIcon) },
]

// Theme options
const themes: ThemeOption[] = [
  { id: 'nexus', name: 'Nexus', icon: markRaw(SunIcon) },
  { id: 'mediaflow', name: 'Dark', icon: markRaw(MoonIcon) },
]

const currentTheme = ref('nexus')

const changeTheme = (theme: string) => {
  currentTheme.value = theme
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('theme', theme)
}

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
  // Initialize theme from localStorage
  const savedTheme = localStorage.getItem('theme') || 'nexus'
  changeTheme(savedTheme)
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
