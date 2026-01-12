<template>
  <div v-if="!authenticated" class="fixed inset-0 z-[9999] bg-base-300 flex items-center justify-center">
    <div class="card bg-base-100 shadow-xl w-80">
      <div class="card-body items-center text-center">
        <h2 class="card-title">MediaFlow Demo</h2>
        <p class="text-sm text-base-content/70 mb-4">Ingresa la contraseña para continuar</p>

        <input
          v-model="password"
          type="password"
          placeholder="Contraseña"
          class="input input-bordered w-full"
          :class="{ 'input-error': error }"
          @keyup.enter="checkPassword"
          autofocus
        />

        <p v-if="error" class="text-error text-sm mt-1">Contraseña incorrecta</p>

        <button class="btn btn-primary w-full mt-4" @click="checkPassword">
          Entrar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const CORRECT_PASSWORD = '4321'
const STORAGE_KEY = 'mediaflow_demo_auth'

const authenticated = ref(false)
const password = ref('')
const error = ref(false)

onMounted(() => {
  authenticated.value = sessionStorage.getItem(STORAGE_KEY) === 'true'
})

function checkPassword() {
  if (password.value === CORRECT_PASSWORD) {
    authenticated.value = true
    sessionStorage.setItem(STORAGE_KEY, 'true')
    error.value = false
  } else {
    error.value = true
  }
}
</script>
