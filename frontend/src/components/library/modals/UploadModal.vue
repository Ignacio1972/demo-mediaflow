<template>
  <dialog class="modal" :class="{ 'modal-open': open }">
    <div class="modal-box max-w-md">
      <h3 class="font-bold text-lg flex items-center gap-2">
        <ArrowUpTrayIcon class="h-5 w-5" />
        Subir Audio
      </h3>

      <!-- Drop Zone -->
      <div
        class="mt-4 border-2 border-dashed rounded-lg p-8 text-center transition-colors"
        :class="{
          'border-primary bg-primary/5': isDragging,
          'border-base-300 hover:border-primary/50': !isDragging
        }"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="onDrop"
      >
        <div v-if="!selectedFile">
          <CloudArrowUpIcon class="h-12 w-12 mx-auto text-base-content/30" />
          <p class="mt-2 text-base-content/60">
            Arrastra un archivo aqui o
          </p>
          <label class="btn btn-sm btn-primary mt-2">
            Seleccionar archivo
            <input
              type="file"
              class="hidden"
              :accept="acceptFormats"
              @change="onFileSelect"
            />
          </label>
          <p class="text-xs text-base-content/40 mt-3">
            Formatos: MP3, WAV, FLAC, AAC, OGG, M4A (max 50MB)
          </p>
        </div>

        <!-- Selected File -->
        <div v-else class="text-left">
          <div class="flex items-center gap-3">
            <MusicalNoteIcon class="h-10 w-10 text-primary" />
            <div class="flex-1 min-w-0">
              <p class="font-medium truncate">{{ selectedFile.name }}</p>
              <p class="text-sm text-base-content/60">
                {{ formatSize(selectedFile.size) }}
              </p>
            </div>
            <button
              v-if="!isUploading"
              class="btn btn-ghost btn-sm btn-square"
              @click="resetUpload"
            >
              <XMarkIcon class="h-4 w-4" />
            </button>
          </div>

          <!-- Progress -->
          <div v-if="isUploading" class="mt-4">
            <progress
              class="progress progress-primary w-full"
              :value="uploadProgress"
              max="100"
            ></progress>
            <p class="text-sm text-center mt-1">{{ uploadProgress }}%</p>
          </div>
        </div>
      </div>

      <!-- Display Name -->
      <div v-if="selectedFile && !isUploading" class="form-control mt-4">
        <label class="label">
          <span class="label-text">Nombre (opcional)</span>
        </label>
        <input
          v-model="displayName"
          type="text"
          class="input input-bordered input-sm"
          :placeholder="selectedFile?.name.replace(/\.[^.]+$/, '')"
        />
      </div>

      <!-- Error -->
      <div v-if="uploadError" class="alert alert-error mt-4">
        <ExclamationCircleIcon class="h-5 w-5" />
        <span>{{ uploadError }}</span>
      </div>

      <!-- Actions -->
      <div class="modal-action">
        <button
          class="btn btn-ghost"
          @click="close"
          :disabled="isUploading"
        >
          Cancelar
        </button>
        <button
          class="btn btn-primary"
          :disabled="!selectedFile || isUploading"
          @click="upload"
        >
          <span v-if="isUploading" class="loading loading-spinner loading-sm"></span>
          {{ isUploading ? 'Subiendo...' : 'Subir' }}
        </button>
      </div>
    </div>

    <form method="dialog" class="modal-backdrop">
      <button @click="close">close</button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  ArrowUpTrayIcon,
  CloudArrowUpIcon,
  MusicalNoteIcon,
  XMarkIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline'
import { useFileUpload } from '../composables/useFileUpload'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'uploaded': [message: any]
}>()

const {
  isUploading,
  uploadProgress,
  uploadError,
  selectedFile,
  formatSize,
  uploadFile,
  resetUpload: resetUploadState,
  ALLOWED_EXTENSIONS
} = useFileUpload()

const displayName = ref('')
const isDragging = ref(false)

const acceptFormats = computed(() =>
  ALLOWED_EXTENSIONS.map(ext => `.${ext}`).join(',')
)

function onDrop(event: DragEvent) {
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    selectedFile.value = files[0]
  }
}

function onFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    selectedFile.value = input.files[0]
  }
}

function resetUpload() {
  resetUploadState()
  displayName.value = ''
}

async function upload() {
  if (!selectedFile.value) return

  const message = await uploadFile(
    selectedFile.value,
    displayName.value || undefined
  )

  if (message) {
    emit('uploaded', message)
    close()
  }
}

function close() {
  if (!isUploading.value) {
    resetUpload()
    emit('update:open', false)
  }
}
</script>
