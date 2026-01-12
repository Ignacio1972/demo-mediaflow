<template>
  <div class="space-y-3">
    <!-- Quick Theme Buttons -->
    <div class="flex flex-wrap gap-2">
      <button
        v-for="theme in quickThemes"
        :key="theme.id"
        @click="changeTheme(theme.id)"
        class="btn btn-sm gap-1.5"
        :class="currentTheme === theme.id ? 'btn-primary' : 'btn-ghost'"
      >
        <component :is="theme.icon" class="w-4 h-4" />
        <span class="text-xs">{{ theme.name }}</span>
      </button>
    </div>

    <!-- More Themes Collapse -->
    <div class="collapse collapse-arrow bg-base-300 rounded-lg">
      <input type="checkbox" />
      <div class="collapse-title text-sm font-medium py-2 min-h-0">
        Más temas
      </div>
      <div class="collapse-content px-2">
        <!-- Light Themes -->
        <div class="mb-3">
          <div class="text-xs text-base-content/60 mb-2">Claros</div>
          <div class="flex flex-wrap gap-1">
            <button
              v-for="theme in lightThemes"
              :key="theme"
              @click="changeTheme(theme)"
              class="theme-chip"
              :class="{ 'active': currentTheme === theme }"
              :title="theme"
            >
              <div class="flex gap-0.5">
                <div
                  v-for="(color, i) in getThemeColors(theme)"
                  :key="i"
                  class="w-2 h-2 rounded-full"
                  :style="{ backgroundColor: color }"
                />
              </div>
            </button>
          </div>
        </div>

        <!-- Dark Themes -->
        <div class="mb-3">
          <div class="text-xs text-base-content/60 mb-2">Oscuros</div>
          <div class="flex flex-wrap gap-1">
            <button
              v-for="theme in darkThemes"
              :key="theme"
              @click="changeTheme(theme)"
              class="theme-chip"
              :class="{ 'active': currentTheme === theme }"
              :title="theme"
            >
              <div class="flex gap-0.5">
                <div
                  v-for="(color, i) in getThemeColors(theme)"
                  :key="i"
                  class="w-2 h-2 rounded-full"
                  :style="{ backgroundColor: color }"
                />
              </div>
            </button>
          </div>
        </div>

        <!-- Colorful Themes -->
        <div>
          <div class="text-xs text-base-content/60 mb-2">Coloridos</div>
          <div class="flex flex-wrap gap-1">
            <button
              v-for="theme in colorfulThemes"
              :key="theme"
              @click="changeTheme(theme)"
              class="theme-chip"
              :class="{ 'active': currentTheme === theme }"
              :title="theme"
            >
              <div class="flex gap-0.5">
                <div
                  v-for="(color, i) in getThemeColors(theme)"
                  :key="i"
                  class="w-2 h-2 rounded-full"
                  :style="{ backgroundColor: color }"
                />
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, markRaw, type Component } from 'vue'
import { MoonIcon, SunIcon, SparklesIcon } from '@heroicons/vue/24/outline'

interface QuickTheme {
  id: string
  name: string
  icon: Component
}

const quickThemes: QuickTheme[] = [
  { id: 'mediaflow', name: 'Dark', icon: markRaw(MoonIcon) },
  { id: 'cleanwhite', name: 'Light', icon: markRaw(SunIcon) },
  { id: 'nexus', name: 'Nexus', icon: markRaw(SparklesIcon) },
]

const lightThemes = ['light', 'cupcake', 'emerald', 'corporate', 'lofi', 'pastel', 'winter', 'nord']
const darkThemes = ['dark', 'business', 'night', 'coffee', 'dim', 'sunset', 'black', 'luxury']
const colorfulThemes = ['synthwave', 'retro', 'cyberpunk', 'valentine', 'halloween', 'dracula', 'aqua']

const themeColorMap: Record<string, string[]> = {
  light: ['#570df8', '#f000b8', '#37cdbe'],
  dark: ['#661AE6', '#D926AA', '#1FB2A5'],
  cupcake: ['#65c3c8', '#ef9fbc', '#eeaf3a'],
  emerald: ['#66cc8a', '#377cfb', '#ea5234'],
  corporate: ['#4b6bfb', '#7b92b2', '#67cba0'],
  synthwave: ['#e779c1', '#58c7f3', '#f3cc30'],
  retro: ['#ef9995', '#a4cbb4', '#ebdc99'],
  cyberpunk: ['#ff7598', '#75d1f0', '#c07eec'],
  valentine: ['#e96d7b', '#a991f7', '#88dbdd'],
  halloween: ['#f28c18', '#6d3a9c', '#51a800'],
  aqua: ['#09ecf3', '#966fb3', '#ffe999'],
  lofi: ['#0D0D0D', '#1A1919', '#262626'],
  pastel: ['#d1c1d7', '#f6cbd1', '#b4e9d6'],
  black: ['#343232', '#343232', '#343232'],
  luxury: ['#ffffff', '#152747', '#513448'],
  dracula: ['#ff79c6', '#bd93f9', '#ffb86c'],
  business: ['#1C4E80', '#7C909A', '#EA6947'],
  night: ['#38bdf8', '#818cf8', '#f471b5'],
  coffee: ['#DB924B', '#263E3F', '#10576D'],
  winter: ['#047AFF', '#463AA2', '#C148AC'],
  dim: ['#9FE88D', '#FF7D5C', '#C3B1E1'],
  nord: ['#5E81AC', '#81A1C1', '#88C0D0'],
  sunset: ['#FF865B', '#FD6F9C', '#B387FA'],
  mediaflow: ['#6366f1', '#8b5cf6', '#06b6d4'],
  cleanwhite: ['#3b82f6', '#8b5cf6', '#10b981'],
  nexus: ['#00d4ff', '#7c3aed', '#f59e0b'],
}

const currentTheme = ref('mediaflow')

const getThemeColors = (theme: string): string[] => {
  return themeColorMap[theme] || ['#666', '#888', '#aaa']
}

const changeTheme = (theme: string) => {
  currentTheme.value = theme
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('theme', theme)
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme') || 'mediaflow'
  changeTheme(savedTheme)
})
</script>

<style scoped>
.theme-chip {
  @apply p-1.5 rounded-md transition-all duration-200;
  @apply hover:bg-base-100 hover:scale-110;
  @apply border border-transparent;
}

.theme-chip.active {
  @apply border-primary bg-primary/10 scale-110;
}
</style>
