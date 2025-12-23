<template>
  <div class="dropdown dropdown-end">
    <label tabindex="0" class="btn btn-ghost btn-sm gap-2">
      <PaintBrushIcon class="w-5 h-5" />
      <span class="hidden sm:inline">Tema</span>
    </label>
    <div tabindex="0" class="dropdown-content z-[100] shadow-2xl bg-base-200 rounded-box w-72 mt-2 max-h-[70vh] overflow-y-auto">
      <!-- Custom Themes -->
      <div class="p-2">
        <div class="text-xs font-semibold text-base-content/60 px-2 py-1">Personalizados</div>
        <div class="grid grid-cols-5 gap-1">
          <button
            v-for="theme in customThemes"
            :key="theme.id"
            @click="changeTheme(theme.id)"
            class="btn btn-sm h-auto py-2 flex flex-col gap-1"
            :class="currentTheme === theme.id ? 'btn-primary' : 'btn-ghost'"
          >
            <component :is="theme.icon" class="w-4 h-4" />
            <span class="text-[10px]">{{ theme.name }}</span>
          </button>
        </div>
      </div>

      <div class="divider my-0 px-2"></div>

      <!-- Theme Categories -->
      <div v-for="category in themeCategories" :key="category.name" class="p-2">
        <div class="text-xs font-semibold text-base-content/60 px-2 py-1">{{ category.name }}</div>
        <div class="grid grid-cols-3 gap-1">
          <button
            v-for="theme in category.themes"
            :key="theme"
            @click="changeTheme(theme)"
            class="btn btn-xs h-auto py-2 flex flex-col items-center gap-1 capitalize"
            :class="currentTheme === theme ? 'btn-primary' : 'btn-ghost'"
          >
            <div class="flex gap-0.5">
              <div
                v-for="(color, i) in getThemeColors(theme)"
                :key="i"
                class="w-2 h-2 rounded-full"
                :style="{ backgroundColor: color }"
              ></div>
            </div>
            <span class="text-[10px] truncate w-full text-center">{{ theme }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, type Component } from 'vue'
import {
  PaintBrushIcon,
  MoonIcon,
  SunIcon,
  SparklesIcon,
} from '@heroicons/vue/24/outline'

interface CustomTheme {
  id: string
  name: string
  icon: Component
}

interface ThemeCategory {
  name: string
  themes: string[]
}

const customThemes: CustomTheme[] = [
  { id: 'nexus', name: 'Nexus', icon: SparklesIcon },
  { id: 'mediaflow', name: 'Mediaflow', icon: MoonIcon },
  { id: 'hrm', name: 'HRM', icon: SunIcon },
  { id: 'cleanwhite', name: 'Clean White', icon: SunIcon },
  { id: 'nordic', name: 'Nordic', icon: SparklesIcon },
]

const themeCategories: ThemeCategory[] = [
  {
    name: 'Claros',
    themes: ['light', 'cupcake', 'bumblebee', 'emerald', 'corporate', 'lofi', 'pastel', 'fantasy', 'wireframe', 'cmyk', 'autumn', 'acid', 'lemonade', 'winter', 'nord']
  },
  {
    name: 'Oscuros',
    themes: ['dark', 'business', 'night', 'coffee', 'dim', 'sunset', 'black', 'luxury']
  },
  {
    name: 'Coloridos',
    themes: ['synthwave', 'retro', 'cyberpunk', 'valentine', 'halloween', 'garden', 'forest', 'aqua', 'dracula']
  }
]

// Preview colors for each theme (primary, secondary, accent)
const themeColorMap: Record<string, string[]> = {
  light: ['#570df8', '#f000b8', '#37cdbe'],
  dark: ['#661AE6', '#D926AA', '#1FB2A5'],
  cupcake: ['#65c3c8', '#ef9fbc', '#eeaf3a'],
  bumblebee: ['#e0a82e', '#f9d72f', '#181830'],
  emerald: ['#66cc8a', '#377cfb', '#ea5234'],
  corporate: ['#4b6bfb', '#7b92b2', '#67cba0'],
  synthwave: ['#e779c1', '#58c7f3', '#f3cc30'],
  retro: ['#ef9995', '#a4cbb4', '#ebdc99'],
  cyberpunk: ['#ff7598', '#75d1f0', '#c07eec'],
  valentine: ['#e96d7b', '#a991f7', '#88dbdd'],
  halloween: ['#f28c18', '#6d3a9c', '#51a800'],
  garden: ['#5c7f67', '#ecf4e7', '#fae5e5'],
  forest: ['#1eb854', '#1fd65f', '#d99330'],
  aqua: ['#09ecf3', '#966fb3', '#ffe999'],
  lofi: ['#0D0D0D', '#1A1919', '#262626'],
  pastel: ['#d1c1d7', '#f6cbd1', '#b4e9d6'],
  fantasy: ['#6e0b75', '#007ebd', '#f8860d'],
  wireframe: ['#b8b8b8', '#b8b8b8', '#b8b8b8'],
  black: ['#343232', '#343232', '#343232'],
  luxury: ['#ffffff', '#152747', '#513448'],
  dracula: ['#ff79c6', '#bd93f9', '#ffb86c'],
  cmyk: ['#45AEEE', '#E8488A', '#FFF232'],
  autumn: ['#8C0327', '#D85251', '#D59B6A'],
  business: ['#1C4E80', '#7C909A', '#EA6947'],
  acid: ['#FF00F4', '#FF7400', '#CBFD03'],
  lemonade: ['#519903', '#E9E92E', '#17AF26'],
  night: ['#38bdf8', '#818cf8', '#f471b5'],
  coffee: ['#DB924B', '#263E3F', '#10576D'],
  winter: ['#047AFF', '#463AA2', '#C148AC'],
  dim: ['#9FE88D', '#FF7D5C', '#C3B1E1'],
  nord: ['#5E81AC', '#81A1C1', '#88C0D0'],
  sunset: ['#FF865B', '#FD6F9C', '#B387FA'],
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
