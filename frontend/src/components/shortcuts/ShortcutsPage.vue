<template>
  <div class="shortcuts-page min-h-screen bg-base-100">
    <!-- Header -->
    <div class="bg-base-200 border-b border-base-300 px-4 py-6">
      <div class="container mx-auto max-w-lg">
        <div class="flex items-center gap-3">
          <div class="flex items-center justify-center w-12 h-12 bg-primary/10 rounded-xl">
            <BoltIcon class="w-6 h-6 text-primary" />
          </div>
          <div>
            <h1 class="text-2xl font-bold">Shortcuts</h1>
            <p class="text-sm text-base-content/50">Accesos directos</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container mx-auto max-w-lg p-4">
      <!-- Error Message -->
      <div v-if="error" class="alert alert-error mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ error }}</span>
      </div>

      <!-- Success Toast -->
      <div v-if="successMessage" class="alert alert-success mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ successMessage }}</span>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex justify-center py-16">
        <span class="loading loading-spinner loading-lg text-primary"></span>
      </div>

      <!-- Empty State -->
      <div v-else-if="shortcuts.length === 0" class="text-center py-16">
        <div class="text-6xl mb-4">⚡</div>
        <h2 class="text-xl font-semibold text-base-content/70 mb-2">
          No hay shortcuts configurados
        </h2>
        <p class="text-base-content/50 mb-6">
          Configura accesos directos desde Configuración
        </p>
        <router-link to="/settings/shortcuts" class="btn btn-primary">
          <CogIcon class="w-5 h-5" />
          Configurar Shortcuts
        </router-link>
      </div>

      <!-- Shortcuts Grid -->
      <div v-else class="grid grid-cols-2 gap-4">
        <ShortcutButton
          v-for="pos in 6"
          :key="pos"
          :shortcut="getShortcutByPosition(pos)"
          :position="pos"
          @click="handleShortcutClick(pos)"
        />
      </div>

      <!-- Settings Link -->
      <div v-if="shortcuts.length > 0" class="mt-8 text-center">
        <router-link
          to="/settings/shortcuts"
          class="btn btn-ghost btn-sm gap-2 text-base-content/50"
        >
          <CogIcon class="w-4 h-4" />
          Administrar Shortcuts
        </router-link>
      </div>
    </div>

    <!-- Action Modal -->
    <ShortcutActionModal
      v-if="selectedShortcut"
      :shortcut="selectedShortcut"
      @close="selectedShortcut = null"
      @broadcast="handleBroadcast"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { BoltIcon, CogIcon } from '@heroicons/vue/24/outline'
import { useShortcuts } from './composables/useShortcuts'
import ShortcutButton from './components/ShortcutButton.vue'
import ShortcutActionModal from './components/ShortcutActionModal.vue'
import type { ShortcutPublic } from '@/types/shortcut'

// Composable
const {
  shortcuts,
  isLoading,
  error,
  loadShortcuts,
  getShortcutByPosition,
  sendToSpeakers,
} = useShortcuts()

// Local state
const selectedShortcut = ref<ShortcutPublic | null>(null)
const successMessage = ref<string | null>(null)

// Handlers
const handleShortcutClick = (position: number) => {
  const shortcut = getShortcutByPosition(position)
  if (shortcut) {
    selectedShortcut.value = shortcut
  }
}

const handleBroadcast = async () => {
  if (!selectedShortcut.value) return

  try {
    await sendToSpeakers(selectedShortcut.value.audio_message_id)
    successMessage.value = `"${selectedShortcut.value.custom_name}" enviado a parlantes`
    selectedShortcut.value = null

    // Clear success message after 3s
    setTimeout(() => {
      successMessage.value = null
    }, 3000)
  } catch (e: any) {
    error.value = e.message || 'Error al enviar a parlantes'
    setTimeout(() => {
      error.value = null
    }, 3000)
  }
}

// Load shortcuts on mount
onMounted(() => {
  loadShortcuts()
})
</script>
