<template>
  <div class="dropdown dropdown-end">
    <label tabindex="0" class="btn btn-ghost btn-sm gap-2">
      <PaintBrushIcon class="w-5 h-5" />
      Tema
    </label>
    <ul tabindex="0" class="dropdown-content z-[1] p-2 shadow-2xl bg-base-200 rounded-box w-52 mt-2">
      <li class="menu-title">
        <span>Temas Personalizados</span>
      </li>
      <li>
        <button @click="changeTheme('mediaflow')" :class="{ 'active': currentTheme === 'mediaflow' }" class="flex items-center gap-2">
          <MoonIcon class="w-4 h-4" />
          Minimalista Oscuro
        </button>
      </li>
      <li>
        <button @click="changeTheme('cleanwhite')" :class="{ 'active': currentTheme === 'cleanwhite' }" class="flex items-center gap-2">
          <SunIcon class="w-4 h-4" />
          Clean White
        </button>
      </li>
      <li>
        <button @click="changeTheme('nordic')" :class="{ 'active': currentTheme === 'nordic' }" class="flex items-center gap-2">
          <SparklesIcon class="w-4 h-4" />
          Nordic Light
        </button>
      </li>

      <div class="divider my-1"></div>

      <li class="menu-title">
        <span>Temas DaisyUI</span>
      </li>
      <li>
        <button @click="changeTheme('dark')" :class="{ 'active': currentTheme === 'dark' }" class="flex items-center gap-2">
          <SwatchIcon class="w-4 h-4" />
          Dark
        </button>
      </li>
      <li>
        <button @click="changeTheme('light')" :class="{ 'active': currentTheme === 'light' }" class="flex items-center gap-2">
          <SwatchIcon class="w-4 h-4" />
          Light
        </button>
      </li>
      <li>
        <button @click="changeTheme('business')" :class="{ 'active': currentTheme === 'business' }" class="flex items-center gap-2">
          <BriefcaseIcon class="w-4 h-4" />
          Business
        </button>
      </li>
      <li>
        <button @click="changeTheme('cupcake')" :class="{ 'active': currentTheme === 'cupcake' }" class="flex items-center gap-2">
          <CakeIcon class="w-4 h-4" />
          Cupcake
        </button>
      </li>
      <li>
        <button @click="changeTheme('cyberpunk')" :class="{ 'active': currentTheme === 'cyberpunk' }" class="flex items-center gap-2">
          <CpuChipIcon class="w-4 h-4" />
          Cyberpunk
        </button>
      </li>
      <li>
        <button @click="changeTheme('caramellatte')" :class="{ 'active': currentTheme === 'caramellatte' }" class="flex items-center gap-2">
          <SwatchIcon class="w-4 h-4" />
          Caramellatte
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  PaintBrushIcon,
  MoonIcon,
  SunIcon,
  SparklesIcon,
  SwatchIcon,
  BriefcaseIcon,
  CakeIcon,
  CpuChipIcon
} from '@heroicons/vue/24/outline'

const currentTheme = ref('mediaflow')

const changeTheme = (theme: string) => {
  currentTheme.value = theme
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('theme', theme)
}

onMounted(() => {
  // Cargar tema guardado
  const savedTheme = localStorage.getItem('theme') || 'mediaflow'
  changeTheme(savedTheme)
})
</script>

<style scoped>
.active {
  @apply bg-primary text-primary-content;
}
</style>
