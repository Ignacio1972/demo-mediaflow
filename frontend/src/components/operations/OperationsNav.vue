<template>
  <div class="operations-nav bg-base-200 border-b border-base-300">
    <div class="container mx-auto px-4">
      <div class="tabs tabs-boxed bg-transparent py-2 gap-2">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="tab gap-2"
          :class="{ 'tab-active': isActive(item.path) }"
        >
          <component :is="item.icon" class="w-5 h-5" />
          {{ item.label }}
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// SVG icons as components
const TruckIcon = () => h('svg', {
  xmlns: 'http://www.w3.org/2000/svg',
  fill: 'none',
  viewBox: '0 0 24 24',
  'stroke-width': '2',
  stroke: 'currentColor',
  class: 'w-5 h-5'
}, [
  h('path', {
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
    d: 'M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 00-3.213-9.193 2.056 2.056 0 00-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 00-10.026 0 1.106 1.106 0 00-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12'
  })
])

// Navigation items
const navItems = computed(() => [
  {
    path: '/operations/vehicles',
    label: 'Vehiculos',
    icon: TruckIcon,
  },
  // Future navigation items:
  // { path: '/operations/lost-child', label: 'Nino Perdido', icon: ... },
  // { path: '/operations/promotions', label: 'Promociones', icon: ... },
])

function isActive(path: string): boolean {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>
