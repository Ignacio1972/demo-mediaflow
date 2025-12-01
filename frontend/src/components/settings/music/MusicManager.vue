<template>
  <div class="music-manager">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-3xl font-bold text-primary flex items-center gap-3">
          <span class="text-4xl">🎵</span>
          Music Manager
        </h1>
        <p class="text-sm text-base-content/60 mt-1">
          Gestiona la música disponible para jingles en el Dashboard
        </p>
      </div>
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

    <!-- Main Content -->
    <div class="grid lg:grid-cols-3 gap-6">
      <!-- Left Column: Upload + List -->
      <div class="lg:col-span-1 space-y-6">
        <!-- Upload Section -->
        <MusicUpload
          ref="uploadRef"
          :is-uploading="isUploading"
          :upload-progress="uploadProgress"
          @upload="handleUpload"
        />

        <!-- Music List -->
        <MusicList
          :tracks="sortedTracks"
          :selected-track="selectedTrack"
          :is-loading="isLoading"
          @select="selectTrack"
          @set-default="handleSetDefault"
        />
      </div>

      <!-- Right Column: Editor -->
      <div class="lg:col-span-2">
        <MusicEditor
          v-if="selectedTrack"
          :track="selectedTrack"
          :is-saving="isLoading"
          @save="handleSave"
          @delete="handleDelete"
          @set-default="handleSetDefault"
        />

        <!-- Empty State -->
        <div v-else class="card bg-base-100 shadow-xl">
          <div class="card-body items-center text-center py-16">
            <div class="text-6xl mb-4">👈</div>
            <h3 class="text-xl font-semibold text-base-content/70">
              Selecciona un track
            </h3>
            <p class="text-base-content/50 mt-2">
              Elige un track de la lista para ver y editar su información
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <dialog v-if="trackToDelete" class="modal modal-open">
      <div class="modal-box">
        <h3 class="font-bold text-lg text-error">
          ⚠️ Confirmar Eliminación
        </h3>
        <p class="py-4">
          ¿Estás seguro de que quieres eliminar
          <strong>"{{ trackToDelete.display_name }}"</strong>?
        </p>
        <p class="text-sm text-base-content/60">
          El archivo será eliminado permanentemente del servidor.
        </p>
        <div class="modal-action">
          <button
            class="btn btn-ghost"
            @click="trackToDelete = null"
          >
            Cancelar
          </button>
          <button
            class="btn btn-error"
            @click="confirmDelete"
            :disabled="isLoading"
          >
            <span v-if="isLoading" class="loading loading-spinner loading-sm"></span>
            Eliminar
          </button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop">
        <button @click="trackToDelete = null">close</button>
      </form>
    </dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMusicManager } from './composables/useMusicManager'
import MusicList from './components/MusicList.vue'
import MusicUpload from './components/MusicUpload.vue'
import MusicEditor from './components/MusicEditor.vue'
import type { MusicTrack } from '@/types/audio'

const {
  tracks,
  selectedTrack,
  isLoading,
  isUploading,
  uploadProgress,
  error,
  successMessage,
  sortedTracks,
  loadTracks,
  selectTrack,
  uploadTrack,
  updateTrack,
  deleteTrack,
  setDefaultTrack,
} = useMusicManager()

// Refs
const uploadRef = ref<InstanceType<typeof MusicUpload> | null>(null)
const trackToDelete = ref<MusicTrack | null>(null)

// Handlers
const handleUpload = async (
  file: File,
  metadata: { display_name?: string; artist?: string; genre?: string; mood?: string }
) => {
  try {
    const newTrack = await uploadTrack(file, metadata)
    if (newTrack) {
      selectTrack(newTrack)
      uploadRef.value?.clearSelection()
    }
  } catch (e) {
    console.error('Upload failed:', e)
  }
}

const handleSave = async (updates: Partial<MusicTrack>) => {
  if (!selectedTrack.value) return

  try {
    await updateTrack(selectedTrack.value.id, updates)
  } catch (e) {
    console.error('Save failed:', e)
  }
}

const handleDelete = (trackId: number) => {
  const track = tracks.value.find(t => t.id === trackId)
  if (track) {
    trackToDelete.value = track
  }
}

const confirmDelete = async () => {
  if (!trackToDelete.value) return

  try {
    await deleteTrack(trackToDelete.value.id)
    trackToDelete.value = null
  } catch (e) {
    console.error('Delete failed:', e)
  }
}

const handleSetDefault = async (trackId: number) => {
  try {
    await setDefaultTrack(trackId)
  } catch (e) {
    console.error('Set default failed:', e)
  }
}

// Load tracks on mount
onMounted(() => {
  loadTracks()
})
</script>
