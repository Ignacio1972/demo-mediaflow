<template>
  <div class="shortcut-manager min-h-screen bg-base-100">
    <SettingsNav />
    <div class="p-6">
      <div class="container mx-auto max-w-7xl">
        <!-- Header -->
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-10">
          <div>
            <div class="flex items-center gap-3 mb-2">
              <div class="flex items-center justify-center w-10 h-10 bg-primary/10 rounded-xl">
                <BoltIcon class="w-5 h-5 text-primary" />
              </div>
              <h1 class="text-3xl font-bold tracking-tight">Shortcuts</h1>
            </div>
            <p class="text-base-content/50 ml-13">
              Configura hasta 6 accesos directos para la página mobile
            </p>
          </div>
          <button
            @click="showAddModal = true"
            class="btn btn-primary gap-2"
          >
            <PlusIcon class="w-5 h-5" />
            Nuevo Shortcut
          </button>
        </div>

        <!-- Toast Messages -->
        <div v-if="error" class="alert alert-error mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ error }}</span>
        </div>

        <div v-if="successMessage" class="alert alert-success mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ successMessage }}</span>
        </div>

        <!-- Slot Grid Preview -->
        <div class="card bg-base-200 shadow-lg mb-6">
          <div class="card-body">
            <h2 class="card-title text-lg mb-4">
              <DevicePhoneMobileIcon class="w-5 h-5" />
              Vista Previa Mobile
            </h2>
            <div class="grid grid-cols-2 gap-3 max-w-md mx-auto">
              <div
                v-for="pos in 6"
                :key="pos"
                class="aspect-square rounded-xl flex flex-col items-center justify-center text-center p-3 border-2 border-dashed transition-all"
                :class="getSlotClass(pos)"
                @click="handleSlotClick(pos)"
              >
                <template v-if="getShortcutByPosition(pos)">
                  <span class="text-3xl mb-1">{{ getShortcutByPosition(pos)?.custom_icon || '⚡' }}</span>
                  <span class="text-sm font-medium truncate w-full">
                    {{ getShortcutByPosition(pos)?.custom_name }}
                  </span>
                </template>
                <template v-else>
                  <span class="text-2xl opacity-30">{{ pos }}</span>
                  <span class="text-xs opacity-40">Vacío</span>
                </template>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Content -->
        <div class="grid lg:grid-cols-3 gap-6">
          <!-- Left: Shortcut List (1 column) -->
          <div class="lg:col-span-1">
            <ShortcutList
              :shortcuts="sortedShortcuts"
              :selected-shortcut="selectedShortcut"
              :is-loading="isLoading"
              @select="handleSelectShortcut"
            />
          </div>

          <!-- Right: Shortcut Editor (2 columns) -->
          <div class="lg:col-span-2">
            <ShortcutEditor
              v-if="selectedShortcut"
              :shortcut="selectedShortcut"
              :available-positions="availablePositions"
              :is-saving="isSaving"
              @save="handleSaveShortcut"
              @cancel="handleCancelEdit"
              @delete="handleDeleteShortcut"
              @update-position="handleUpdatePosition"
            />

            <!-- Empty State -->
            <div v-else class="card bg-base-100 shadow-xl">
              <div class="card-body items-center text-center py-16">
                <div class="text-6xl mb-4">👈</div>
                <h3 class="text-xl font-semibold text-base-content/70">
                  Selecciona un shortcut
                </h3>
                <p class="text-base-content/50 mt-2">
                  Elige un shortcut de la lista para editarlo o crea uno nuevo
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Add Shortcut Modal -->
        <ShortcutAddModal
          v-if="showAddModal"
          :available-audios="availableAudios"
          :existing-audio-ids="existingAudioIds"
          @close="showAddModal = false"
          @create="handleCreateShortcut"
        />

        <!-- Delete Confirmation Modal -->
        <dialog v-if="shortcutToDelete" class="modal modal-open">
          <div class="modal-box">
            <h3 class="font-bold text-lg text-error">
              Confirmar Eliminación
            </h3>
            <p class="py-4">
              ¿Estás seguro de que quieres eliminar el shortcut
              <strong>"{{ shortcutToDelete.custom_name }}"</strong>?
            </p>
            <p class="text-sm text-base-content/60">
              El audio asociado no será eliminado.
            </p>

            <div class="modal-action">
              <button
                class="btn btn-ghost"
                @click="shortcutToDelete = null"
              >
                Cancelar
              </button>
              <button
                class="btn btn-error"
                @click="confirmDelete"
                :disabled="isSaving"
              >
                <span v-if="isSaving" class="loading loading-spinner loading-sm"></span>
                Eliminar
              </button>
            </div>
          </div>
          <form method="dialog" class="modal-backdrop">
            <button @click="shortcutToDelete = null">close</button>
          </form>
        </dialog>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { BoltIcon, PlusIcon, DevicePhoneMobileIcon } from '@heroicons/vue/24/outline'
import { useShortcutManager } from './composables/useShortcutManager'
import ShortcutList from './components/ShortcutList.vue'
import ShortcutEditor from './components/ShortcutEditor.vue'
import ShortcutAddModal from './components/ShortcutAddModal.vue'
import SettingsNav from '../SettingsNav.vue'
import type { Shortcut, ShortcutUpdate, ShortcutCreate } from '@/types/shortcut'

// Composable
const {
  shortcuts,
  selectedShortcut,
  availableAudios,
  isLoading,
  isSaving,
  error,
  successMessage,
  sortedShortcuts,
  availablePositions,
  loadShortcuts,
  loadAvailableAudios,
  selectShortcut,
  createShortcut,
  updateShortcut,
  updatePosition,
  deleteShortcut,
  getShortcutByPosition,
} = useShortcutManager()

// Local state
const showAddModal = ref(false)
const shortcutToDelete = ref<Shortcut | null>(null)

// Computed
const existingAudioIds = computed(() => shortcuts.value.map(s => s.audio_message_id))

// Get slot class based on state
const getSlotClass = (position: number) => {
  const shortcut = getShortcutByPosition(position)
  if (shortcut) {
    const color = shortcut.custom_color || '#10B981'
    return {
      'border-solid cursor-pointer hover:scale-105': true,
      'bg-opacity-20': true,
    }
  }
  return 'border-base-300 bg-base-100 opacity-60'
}

// Get slot style for color
const getSlotStyle = (position: number) => {
  const shortcut = getShortcutByPosition(position)
  if (shortcut?.custom_color) {
    return {
      backgroundColor: `${shortcut.custom_color}20`,
      borderColor: `${shortcut.custom_color}60`,
    }
  }
  return {}
}

// Handlers
const handleSlotClick = (position: number) => {
  const shortcut = getShortcutByPosition(position)
  if (shortcut) {
    selectShortcut(shortcut)
  }
}

const handleSelectShortcut = (shortcut: Shortcut) => {
  selectShortcut(shortcut)
}

const handleSaveShortcut = async (updates: ShortcutUpdate) => {
  if (!selectedShortcut.value) return

  try {
    await updateShortcut(selectedShortcut.value.id, updates)
  } catch (e) {
    console.error('Failed to save shortcut:', e)
  }
}

const handleUpdatePosition = async (position: number | null) => {
  if (!selectedShortcut.value) return

  try {
    await updatePosition(selectedShortcut.value.id, position)
  } catch (e) {
    console.error('Failed to update position:', e)
  }
}

const handleCancelEdit = () => {
  if (selectedShortcut.value) {
    const shortcut = shortcuts.value.find(s => s.id === selectedShortcut.value?.id)
    if (shortcut) {
      selectShortcut(shortcut)
    }
  }
}

const handleDeleteShortcut = (shortcutId: number) => {
  const shortcut = shortcuts.value.find(s => s.id === shortcutId)
  if (shortcut) {
    shortcutToDelete.value = shortcut
  }
}

const confirmDelete = async () => {
  if (!shortcutToDelete.value) return

  try {
    await deleteShortcut(shortcutToDelete.value.id)
    shortcutToDelete.value = null
  } catch (e) {
    console.error('Failed to delete shortcut:', e)
  }
}

const handleCreateShortcut = async (shortcutData: ShortcutCreate) => {
  try {
    const newShortcut = await createShortcut(shortcutData)
    showAddModal.value = false
    if (newShortcut) {
      selectShortcut(newShortcut)
    }
  } catch (e) {
    console.error('Failed to create shortcut:', e)
  }
}

// Load data on mount
onMounted(() => {
  loadShortcuts()
  loadAvailableAudios()
})
</script>

<style scoped>
.aspect-square {
  aspect-ratio: 1 / 1;
}
</style>
