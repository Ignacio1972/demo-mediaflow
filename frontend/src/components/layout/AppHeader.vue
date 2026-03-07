<template>
  <header class="fixed top-4 left-4 right-4 h-16 rounded-xl shadow-theme-sm z-50 flex items-center" style="background-color: #0171dc;">
    <!-- Mobile: Burger -->
    <button
      class="lg:hidden btn btn-ghost btn-sm btn-square ml-2 text-white"
      @click="openSidebar"
      aria-label="Abrir menú"
    >
      <Bars3Icon class="h-5 w-5" />
    </button>

    <!-- Logo area (matches sidebar width on desktop) -->
    <div class="lg:w-60 flex items-center px-3 lg:px-5 shrink-0">
      <router-link to="/campaigns" class="hover:opacity-80 transition-opacity">
        <img
          :src="tenantLogo"
          :alt="tenantName"
          class="h-8 w-auto object-contain"
        />
      </router-link>
    </div>

    <!-- Vertical separator (desktop) -->
    <div class="hidden lg:block w-px h-8 bg-white/30 shrink-0" />

    <!-- Desktop: Page title -->
    <h1 class="hidden lg:block text-lg font-medium text-white ml-4">
      {{ pageTitle }}
    </h1>

    <!-- Spacer -->
    <div class="flex-1" />

    <!-- Theme toggle -->
    <div class="flex items-center gap-1 pr-4">
      <button
        v-for="theme in themes"
        :key="theme.id"
        @click="changeTheme(theme.id)"
        class="btn btn-ghost btn-sm btn-square text-white/80 hover:text-white"
        :title="theme.name"
      >
        <component :is="theme.icon" class="w-4 h-4" />
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, markRaw, type Component } from 'vue'
import { useLayout } from '@/composables/useLayout'
import { useTenantStore } from '@/stores/tenant'
import { Bars3Icon, MoonIcon, SunIcon, SparklesIcon } from '@heroicons/vue/24/outline'

interface ThemeOption {
  id: string
  name: string
  icon: Component
}

const { pageTitle, openSidebar } = useLayout()
const tenantStore = useTenantStore()
const tenantLogo = computed(() => tenantStore.tenantLogo)
const tenantName = computed(() => tenantStore.tenantName)

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

onMounted(() => {
  const savedTheme = localStorage.getItem('theme') || 'nexus'
  changeTheme(savedTheme)
})
</script>
