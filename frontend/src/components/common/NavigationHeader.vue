<template>
  <header class="sticky top-0 z-50 bg-base-200 shadow-lg">
    <div class="container mx-auto px-4 py-4 max-w-[1600px]">
      <div class="flex items-center justify-between">
        <!-- Logo / Title (Left) -->
        <router-link
          to="/dashboard"
          class="flex items-center hover:opacity-80 transition-opacity"
        >
          <img
            src="/images/solo%20logo.png"
            alt="MediaFlow"
            class="h-10"
          />
          <span class="ml-3 text-2xl font-bold tracking-tight">
            <span class="text-primary">Media</span><span class="text-base-content">flow</span>
          </span>
        </router-link>

        <!-- Navigation Menu (Right) -->
        <nav class="flex items-center gap-6">
          <!-- Library Link -->
          <div class="tooltip tooltip-bottom" data-tip="Biblioteca">
            <router-link
              to="/library"
              class="nav-link"
              :class="{ 'active': isActive('/library') }"
            >
              <BookOpenIcon class="h-6 w-6" />
            </router-link>
          </div>

          <!-- Calendar Link -->
          <div class="tooltip tooltip-bottom" data-tip="Calendario">
            <router-link
              to="/calendar"
              class="nav-link"
              :class="{ 'active': isActive('/calendar') }"
            >
              <CalendarIcon class="h-6 w-6" />
            </router-link>
          </div>

          <!-- Campaigns Link -->
          <div class="tooltip tooltip-bottom" data-tip="Campañas">
            <router-link
              to="/campaigns"
              class="nav-link"
              :class="{ 'active': isActive('/campaigns') }"
            >
              <RocketLaunchIcon class="h-6 w-6" />
            </router-link>
          </div>

          <!-- Operations Link -->
          <div class="tooltip tooltip-bottom" data-tip="Operaciones">
            <router-link
              to="/operations"
              class="nav-link"
              :class="{ 'active': isActive('/operations') }"
            >
              <MegaphoneIcon class="h-6 w-6" />
            </router-link>
          </div>

          <!-- Settings Link -->
          <div class="tooltip tooltip-bottom" data-tip="Configuración">
            <router-link
              to="/settings"
              class="nav-link"
              :class="{ 'active': isActive('/settings') }"
            >
              <CogIcon class="h-6 w-6" />
            </router-link>
          </div>

          <!-- Theme Selector -->
          <div class="ml-2">
            <ThemeSelector />
          </div>
        </nav>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { BookOpenIcon, CalendarIcon, CogIcon, MegaphoneIcon, RocketLaunchIcon } from '@heroicons/vue/24/outline'
import ThemeSelector from './ThemeSelector.vue'

const route = useRoute()

const isActive = (path: string): boolean => {
  return route.path.startsWith(path)
}
</script>

<style scoped>
.nav-link {
  @apply flex items-center justify-center text-base-content font-medium transition-all duration-200;
  @apply hover:text-primary;
  @apply p-2 rounded-lg hover:bg-base-300;
}

.nav-link.active {
  @apply text-primary bg-base-300;
}
</style>
