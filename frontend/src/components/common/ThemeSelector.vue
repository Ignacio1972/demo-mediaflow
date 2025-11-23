<template>
  <div class="dropdown dropdown-end">
    <label tabindex="0" class="btn btn-ghost btn-sm gap-2">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="w-5 h-5 stroke-current">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
      </svg>
      Tema
    </label>
    <ul tabindex="0" class="dropdown-content z-[1] p-2 shadow-2xl bg-base-200 rounded-box w-52 mt-2">
      <li class="menu-title">
        <span>Temas Personalizados</span>
      </li>
      <li>
        <button @click="changeTheme('mediaflow')" :class="{ 'active': currentTheme === 'mediaflow' }">
          🌙 Minimalista Oscuro
        </button>
      </li>
      <li>
        <button @click="changeTheme('cleanwhite')" :class="{ 'active': currentTheme === 'cleanwhite' }">
          ☀️ Clean White
        </button>
      </li>
      <li>
        <button @click="changeTheme('nordic')" :class="{ 'active': currentTheme === 'nordic' }">
          ❄️ Nordic Light
        </button>
      </li>

      <div class="divider my-1"></div>

      <li class="menu-title">
        <span>Temas DaisyUI</span>
      </li>
      <li>
        <button @click="changeTheme('dark')" :class="{ 'active': currentTheme === 'dark' }">
          🎨 Dark
        </button>
      </li>
      <li>
        <button @click="changeTheme('light')" :class="{ 'active': currentTheme === 'light' }">
          🎨 Light
        </button>
      </li>
      <li>
        <button @click="changeTheme('business')" :class="{ 'active': currentTheme === 'business' }">
          💼 Business
        </button>
      </li>
      <li>
        <button @click="changeTheme('cupcake')" :class="{ 'active': currentTheme === 'cupcake' }">
          🧁 Cupcake
        </button>
      </li>
      <li>
        <button @click="changeTheme('cyberpunk')" :class="{ 'active': currentTheme === 'cyberpunk' }">
          🤖 Cyberpunk
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

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
