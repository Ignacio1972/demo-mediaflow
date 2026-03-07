<template>
  <div v-if="!authenticated" class="fixed inset-0 z-[9999] bg-base-300 flex items-center justify-center overflow-hidden">
    <div class="card bg-base-100 shadow-xl w-80">
      <div class="card-body items-center text-center">
        <div class="rounded-xl px-6 py-4 mb-4" style="background-color: #0171dc;">
          <img
            :src="tenantLogo"
            :alt="tenantName"
            class="h-16 w-auto object-contain"
          />
        </div>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useTenantStore } from '@/stores/tenant'

const CORRECT_PASSWORD = '4321'
const STORAGE_KEY = 'mediaflow_demo_auth_v2'
const VERSION_KEY = 'mediaflow_auth_version'
const POLL_INTERVAL = 30000 // 30 seconds

const tenantStore = useTenantStore()
const tenantLogo = computed(() => tenantStore.tenantLogo)
const tenantName = computed(() => tenantStore.tenantName)

const authenticated = ref(false)
const password = ref('')
const error = ref(false)

let pollTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  authenticated.value = sessionStorage.getItem(STORAGE_KEY) === 'true'
  startPolling()
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

function startPolling() {
  checkAuthVersion()
  pollTimer = setInterval(checkAuthVersion, POLL_INTERVAL)
}

async function checkAuthVersion() {
  try {
    const res = await fetch('/api/v1/auth/version')
    const data = await res.json()
    const savedVersion = sessionStorage.getItem(VERSION_KEY)

    if (savedVersion && savedVersion !== data.version) {
      // Version changed - force reload
      sessionStorage.removeItem(STORAGE_KEY)
      location.reload()
    } else if (!savedVersion) {
      // First time - save current version
      sessionStorage.setItem(VERSION_KEY, data.version)
    }
  } catch {
    // Ignore network errors
  }
}

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
