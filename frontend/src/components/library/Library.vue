<template>
  <div class="min-h-screen bg-base-100 p-6">
    <div class="container mx-auto max-w-7xl">
      <!-- Header -->
      <LibraryHeader
        :total="store.total"
        :selection-mode="selectionMode"
        :view-mode="store.viewMode"
        @toggle-selection="toggleSelectionMode"
        @upload="showUploadModal = true"
        @update:view-mode="store.setViewMode"
      />

      <!-- Filters -->
      <LibraryFilters
        :filters="store.filters"
        :categories="store.categories"
        @update:filters="store.setFilters"
        @reset="store.resetFilters"
      />

      <!-- Selection Bar -->
      <div v-if="selectionMode && hasSelection" class="mt-4">
        <SelectionBar
          :selected-count="selectedCount"
          :categories="store.categories"
          @delete="confirmDeleteSelected"
          @categorize="categorizeSelected"
          @cancel="disableSelectionMode"
        />
      </div>

      <!-- Loading -->
      <div v-if="store.isLoading" class="flex justify-center py-12">
        <span class="loading loading-spinner loading-lg text-primary"></span>
      </div>

      <!-- Empty State -->
      <EmptyState
        v-else-if="store.isEmpty"
        @upload="showUploadModal = true"
        @generate="goToDashboard"
      />

      <!-- Content -->
      <div v-else class="mt-6">
        <!-- Grid View -->
        <LibraryGrid
          v-if="store.viewMode === 'grid'"
          :messages="store.messages"
          :categories="store.categories"
          :selection-mode="selectionMode"
          :is-selected="isSelected"
          :is-message-playing="isMessagePlaying"
          @play="playMessage"
          @toggle-favorite="handleToggleFavorite"
          @toggle-select="toggleSelect"
          @update-category="handleUpdateCategory"
          @action="handleAction"
        />

        <!-- List View -->
        <LibraryList
          v-else
          :messages="store.messages"
          :categories="store.categories"
          :selection-mode="selectionMode"
          :selected-ids="selectedIds"
          :is-selected="isSelected"
          :is-message-playing="isMessagePlaying"
          @play="playMessage"
          @toggle-favorite="handleToggleFavorite"
          @toggle-select="toggleSelect"
          @select-all="selectAll"
          @clear-selection="clearSelection"
          @update-category="handleUpdateCategory"
          @action="handleAction"
        />

        <!-- Pagination -->
        <div v-if="store.totalPages > 1" class="flex justify-center mt-6">
          <div class="btn-group">
            <button
              class="btn btn-sm"
              :disabled="!store.hasPrevPage"
              @click="store.prevPage"
            >
              «
            </button>
            <button class="btn btn-sm">
              Pagina {{ store.currentPage }} de {{ store.totalPages }}
            </button>
            <button
              class="btn btn-sm"
              :disabled="!store.hasNextPage"
              @click="store.nextPage"
            >
              »
            </button>
          </div>
        </div>
      </div>

      <!-- Error Toast -->
      <div v-if="store.error" class="toast toast-end">
        <div class="alert alert-error">
          <span>{{ store.error }}</span>
          <button class="btn btn-ghost btn-xs" @click="store.clearError">×</button>
        </div>
      </div>

      <!-- Modals -->
      <UploadModal
        v-model:open="showUploadModal"
        @uploaded="onUploaded"
      />

      <ScheduleModal
        v-model:open="showScheduleModal"
        :message="selectedMessage"
        @scheduled="onScheduled"
      />

      <DeleteConfirmModal
        v-model:open="showDeleteModal"
        :count="deleteCount"
        :item-name="deleteItemName"
        @confirm="confirmDelete"
      />

      <BroadcastModal
        v-model:open="showBroadcastModal"
        :message="selectedMessage"
        @sent="onBroadcastSent"
      />

      <!-- Success Toast - Centered -->
      <Transition name="toast-scale">
        <div v-if="successToast" class="fixed inset-0 flex items-center justify-center z-50 pointer-events-none">
          <div class="bg-success text-success-content px-8 py-6 rounded-xl shadow-2xl max-w-lg pointer-events-auto">
            <div class="flex items-center gap-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="text-xl font-semibold">{{ successToast }}</span>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { AudioMessage } from '@/types/audio'
import type { MessageAction } from './types/library.types'

// Store
import { useLibraryStore } from './stores/libraryStore'

// Composables
import { useAudioPlayer } from './composables/useAudioPlayer'
import { useSelection } from './composables/useSelection'

// Components
import LibraryHeader from './components/LibraryHeader.vue'
import LibraryFilters from './components/LibraryFilters.vue'
import LibraryGrid from './components/LibraryGrid.vue'
import LibraryList from './components/LibraryList.vue'
import SelectionBar from './components/SelectionBar.vue'
import EmptyState from './components/EmptyState.vue'

// Modals
import UploadModal from './modals/UploadModal.vue'
import ScheduleModal from './modals/ScheduleModal.vue'
import DeleteConfirmModal from './modals/DeleteConfirmModal.vue'
import BroadcastModal from './modals/BroadcastModal.vue'

const router = useRouter()
const store = useLibraryStore()

// Audio player
const { playMessage, isMessagePlaying } = useAudioPlayer()

// Selection
const {
  selectionMode,
  selectedIds,
  selectedCount,
  hasSelection,
  toggleSelectionMode,
  disableSelectionMode,
  toggleSelect,
  selectAll,
  clearSelection,
  isSelected,
  getSelectedArray
} = useSelection()

// Modal state
const showUploadModal = ref(false)
const showScheduleModal = ref(false)
const showDeleteModal = ref(false)
const showBroadcastModal = ref(false)
const selectedMessage = ref<AudioMessage | null>(null)
const deleteCount = ref(0)
const deleteItemName = ref<string | undefined>(undefined)
const pendingDeleteIds = ref<number[]>([])

// Toast state
const successToast = ref<string | null>(null)

// Handlers
async function handleToggleFavorite(id: number) {
  await store.toggleFavorite(id)
}

async function handleUpdateCategory(id: number, categoryId: string | null) {
  await store.updateCategory(id, categoryId)
}

function handleAction(action: MessageAction, message: AudioMessage) {
  switch (action) {
    case 'play':
      playMessage(message)
      break
    case 'schedule':
      selectedMessage.value = message
      showScheduleModal.value = true
      break
    case 'send-to-radio':
      selectedMessage.value = message
      showBroadcastModal.value = true
      break
    case 'edit-in-dashboard':
      editInDashboard(message)
      break
    case 'delete':
      confirmDeleteSingle(message)
      break
  }
}

function onBroadcastSent(branchCount: number) {
  successToast.value = `Audio enviado a ${branchCount} sucursal${branchCount > 1 ? 'es' : ''}`
  setTimeout(() => {
    successToast.value = null
  }, 3000)
}

function editInDashboard(message: AudioMessage) {
  // Store text in sessionStorage for Dashboard to pick up
  sessionStorage.setItem('editMessage', JSON.stringify({
    text: message.original_text,
    voice_id: message.voice_id
  }))
  router.push('/dashboard')
}

function confirmDeleteSingle(message: AudioMessage) {
  deleteCount.value = 1
  deleteItemName.value = message.display_name
  pendingDeleteIds.value = [message.id]
  showDeleteModal.value = true
}

function confirmDeleteSelected() {
  const ids = getSelectedArray()
  deleteCount.value = ids.length
  deleteItemName.value = undefined
  pendingDeleteIds.value = ids
  showDeleteModal.value = true
}

async function confirmDelete() {
  if (pendingDeleteIds.value.length === 1) {
    await store.deleteMessage(pendingDeleteIds.value[0])
  } else {
    await store.deleteMessages(pendingDeleteIds.value)
  }
  clearSelection()
  pendingDeleteIds.value = []
}

async function categorizeSelected(categoryId: string | null) {
  const ids = getSelectedArray()
  for (const id of ids) {
    await store.updateCategory(id, categoryId)
  }
  clearSelection()
}

function onUploaded(_message: AudioMessage) {
  // Message already added to store by uploadAudio
}

function onScheduled(_schedule: any) {
  // Could show success notification
}

function goToDashboard() {
  router.push('/dashboard')
}

// Load data on mount
onMounted(async () => {
  await Promise.all([
    store.fetchMessages(),
    store.fetchCategories()
  ])
})
</script>

<style scoped>
.toast-scale-enter-active {
  transition: all 0.3s ease-out;
}

.toast-scale-leave-active {
  transition: all 0.2s ease-in;
}

.toast-scale-enter-from {
  opacity: 0;
  transform: scale(0.8);
}

.toast-scale-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
