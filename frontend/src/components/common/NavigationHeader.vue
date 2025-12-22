<template>
  <header class="sticky top-0 z-50 bg-base-200 shadow-lg">
    <div class="container mx-auto px-4 py-4">
      <div class="flex items-center justify-between">
        <!-- Logo / Title (Left) -->
        <router-link
          to="/dashboard"
          class="flex items-center hover:opacity-80 transition-opacity pl-6"
        >
          <img
            src="/images/Mediaflow%20trans.png"
            alt="MediaFlow"
            class="h-16"
          />
        </router-link>

        <!-- Navigation Menu (Right) -->
        <nav class="flex items-center gap-6">
          <!-- Library Link -->
          <router-link
            to="/library"
            class="nav-link tooltip"
            :class="{ 'active': isActive('/library') }"
            data-tooltip="Library"
          >
            <BookOpenIcon class="h-6 w-6" />
          </router-link>

          <!-- Calendar Link -->
          <router-link
            to="/calendar"
            class="nav-link tooltip"
            :class="{ 'active': isActive('/calendar') }"
            data-tooltip="Calendar"
          >
            <CalendarIcon class="h-6 w-6" />
          </router-link>

          <!-- Campaigns Link -->
          <router-link
            to="/campaigns"
            class="nav-link tooltip"
            :class="{ 'active': isActive('/campaigns') }"
            data-tooltip="Campañas"
          >
            <RocketLaunchIcon class="h-6 w-6" />
          </router-link>

          <!-- Operations Link -->
          <router-link
            to="/operations"
            class="nav-link tooltip"
            :class="{ 'active': isActive('/operations') }"
            data-tooltip="Operaciones"
          >
            <MegaphoneIcon class="h-6 w-6" />
          </router-link>

          <!-- Settings Link -->
          <router-link
            to="/settings"
            class="nav-link tooltip"
            :class="{ 'active': isActive('/settings') }"
            data-tooltip="Settings"
          >
            <CogIcon class="h-6 w-6" />
          </router-link>

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

/* Tooltip styles */
.tooltip {
  position: relative;
}

.tooltip::after {
  content: attr(data-tooltip);
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 0.5rem;
  background-color: #1e293b;
  color: white;
  font-size: 0.875rem;
  font-weight: normal;
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 200ms;
  z-index: 100;
}

.tooltip:hover::after {
  opacity: 1;
}
</style>
