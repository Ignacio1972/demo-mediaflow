<template>
  <div>
    <div class="max-w-7xl mx-auto">
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
      <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 md:gap-4">
        <ShortcutButton
          v-for="(pos, index) in 8"
          :key="pos"
          :shortcut="getShortcutByPosition(pos)"
          :position="pos"
          :style="{ animationDelay: `${index * 50}ms` }"
          class="shortcut-card-enter"
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
      @broadcast="openBroadcastModal"
      @delete="handleDelete"
    />

    <!-- Broadcast Modal (reused from library) -->
    <BroadcastModal
      v-model:open="showBroadcastModal"
      :message="broadcastMessage"
      @sent="onBroadcastSent"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { CogIcon } from '@heroicons/vue/24/outline'
import { useShortcuts } from './composables/useShortcuts'
import ShortcutButton from './components/ShortcutButton.vue'
import ShortcutActionModal from './components/ShortcutActionModal.vue'
import BroadcastModal from '@/components/library/modals/BroadcastModal.vue'
import type { ShortcutPublic } from '@/types/shortcut'
import type { AudioMessage } from '@/types/audio'

// Composable
const {
  shortcuts,
  isLoading,
  error,
  loadShortcuts,
  getShortcutByPosition,
  deleteShortcut,
} = useShortcuts()

// Local state
const selectedShortcut = ref<ShortcutPublic | null>(null)
const successMessage = ref<string | null>(null)
const showBroadcastModal = ref(false)
const broadcastMessage = ref<AudioMessage | null>(null)

// Handlers
const handleShortcutClick = (position: number) => {
  const shortcut = getShortcutByPosition(position)
  if (shortcut) {
    selectedShortcut.value = shortcut
  }
}

const openBroadcastModal = () => {
  if (!selectedShortcut.value) return

  const s = selectedShortcut.value
  broadcastMessage.value = {
    id: s.audio_message_id,
    filename: '',
    display_name: s.custom_name,
    file_path: '',
    format: 'mp3',
    original_text: '',
    voice_id: '',
    is_favorite: false,
    volume_adjustment: 0,
    has_jingle: false,
    status: 'ready',
    sent_to_player: false,
    priority: 0,
    created_at: '',
    updated_at: '',
    audio_url: s.audio_url,
  } as AudioMessage

  selectedShortcut.value = null
  showBroadcastModal.value = true
}

function onBroadcastSent(branchCount: number) {
  successMessage.value = `Audio enviado a ${branchCount} sucursal${branchCount > 1 ? 'es' : ''}`
  setTimeout(() => { successMessage.value = null }, 3000)
}

const handleDelete = async () => {
  if (!selectedShortcut.value) return

  try {
    const name = selectedShortcut.value.custom_name
    await deleteShortcut(selectedShortcut.value.id)
    selectedShortcut.value = null
    successMessage.value = `Shortcut "${name}" eliminado`
    setTimeout(() => { successMessage.value = null }, 3000)
  } catch (e: any) {
    error.value = e.message || 'Error al eliminar shortcut'
    setTimeout(() => { error.value = null }, 3000)
  }
}

// Load shortcuts on mount
onMounted(() => {
  loadShortcuts()
})
</script>

<style scoped>
.shortcut-card-enter {
  animation: cardEnter 0.4s ease-out backwards;
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>
