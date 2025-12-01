<template>
  <div class="music-upload card bg-base-100 shadow-xl">
    <div class="card-body p-4">
      <h3 class="font-semibold text-lg mb-4">Subir Nueva Música</h3>

      <!-- Drag & Drop Zone -->
      <div
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
        class="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all"
        :class="[
          isDragging
            ? 'border-primary bg-primary/10'
            : 'border-base-300 hover:border-primary/50 hover:bg-base-200'
        ]"
      >
        <div v-if="isUploading" class="space-y-4">
          <span class="loading loading-spinner loading-lg text-primary"></span>
          <div class="w-full">
            <progress
              class="progress progress-primary w-full"
              :value="uploadProgress"
              max="100"
            ></progress>
            <p class="text-sm mt-2">{{ uploadProgress }}% subido</p>
          </div>
        </div>

        <div v-else class="space-y-2">
          <div class="text-4xl">📤</div>
          <p class="font-medium">
            {{ isDragging ? 'Suelta el archivo aquí' : 'Arrastra música aquí' }}
          </p>
          <p class="text-sm text-base-content/50">
            o haz click para seleccionar
          </p>
          <p class="text-xs text-base-content/40">
            Formatos: MP3, WAV, OGG, M4A (máx. 50MB)
          </p>
        </div>
      </div>

      <!-- Hidden File Input -->
      <input
        ref="fileInput"
        type="file"
        accept=".mp3,.wav,.ogg,.m4a,audio/*"
        class="hidden"
        @change="handleFileSelect"
      />

      <!-- Selected File Preview -->
      <div v-if="selectedFile && !isUploading" class="mt-4 p-4 bg-base-200 rounded-lg">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <span class="text-2xl">🎵</span>
            <div>
              <p class="font-medium">{{ selectedFile.name }}</p>
              <p class="text-sm text-base-content/50">
                {{ formatFileSize(selectedFile.size) }}
              </p>
            </div>
          </div>
          <button
            @click="clearSelection"
            class="btn btn-ghost btn-sm btn-circle"
          >
            ✕
          </button>
        </div>

        <!-- Optional Metadata -->
        <div class="mt-4 grid grid-cols-2 gap-3">
          <input
            v-model="metadata.display_name"
            type="text"
            placeholder="Nombre (opcional)"
            class="input input-bordered input-sm"
          />
          <input
            v-model="metadata.artist"
            type="text"
            placeholder="Artista (opcional)"
            class="input input-bordered input-sm"
          />
          <select v-model="metadata.genre" class="select select-bordered select-sm">
            <option value="">Género (opcional)</option>
            <option value="Electronic">Electronic</option>
            <option value="Pop">Pop</option>
            <option value="Rock">Rock</option>
            <option value="Jazz">Jazz</option>
            <option value="Ambient">Ambient</option>
            <option value="Classical">Classical</option>
            <option value="Latin">Latin</option>
            <option value="Other">Otro</option>
          </select>
          <select v-model="metadata.mood" class="select select-bordered select-sm">
            <option value="">Mood (opcional)</option>
            <option value="energetic">Energético</option>
            <option value="calm">Calmado</option>
            <option value="happy">Alegre</option>
            <option value="inspiring">Inspirador</option>
            <option value="relaxed">Relajado</option>
            <option value="upbeat">Animado</option>
            <option value="festive">Festivo</option>
          </select>
        </div>

        <button
          @click="uploadFile"
          class="btn btn-primary w-full mt-4"
          :disabled="isUploading"
        >
          <span v-if="isUploading" class="loading loading-spinner loading-sm"></span>
          Subir Música
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const props = defineProps<{
  isUploading: boolean
  uploadProgress: number
}>()

const emit = defineEmits<{
  upload: [file: File, metadata: { display_name?: string; artist?: string; genre?: string; mood?: string }]
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const selectedFile = ref<File | null>(null)

const metadata = reactive({
  display_name: '',
  artist: '',
  genre: '',
  mood: '',
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    validateAndSetFile(input.files[0])
  }
}

const handleDrop = (event: DragEvent) => {
  isDragging.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    validateAndSetFile(event.dataTransfer.files[0])
  }
}

const validateAndSetFile = (file: File) => {
  const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4', 'audio/x-m4a']
  const allowedExtensions = ['.mp3', '.wav', '.ogg', '.m4a']
  const maxSize = 50 * 1024 * 1024 // 50MB

  const ext = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))

  if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(ext)) {
    alert('Formato no soportado. Usa MP3, WAV, OGG o M4A.')
    return
  }

  if (file.size > maxSize) {
    alert('El archivo es muy grande. Máximo 50MB.')
    return
  }

  selectedFile.value = file
  // Pre-fill display name from filename
  metadata.display_name = file.name.replace(/\.[^/.]+$/, '')
}

const clearSelection = () => {
  selectedFile.value = null
  metadata.display_name = ''
  metadata.artist = ''
  metadata.genre = ''
  metadata.mood = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const uploadFile = () => {
  if (!selectedFile.value) return

  const cleanMetadata = {
    display_name: metadata.display_name || undefined,
    artist: metadata.artist || undefined,
    genre: metadata.genre || undefined,
    mood: metadata.mood || undefined,
  }

  emit('upload', selectedFile.value, cleanMetadata)
}

const formatFileSize = (bytes: number): string => {
  const mb = bytes / (1024 * 1024)
  return `${mb.toFixed(1)} MB`
}

// Expose clearSelection for parent component
defineExpose({ clearSelection })
</script>
