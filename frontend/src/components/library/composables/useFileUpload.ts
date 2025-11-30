import { ref } from 'vue'
import { useLibraryStore } from '../stores/libraryStore'

const ALLOWED_TYPES = [
  'audio/mpeg',      // MP3
  'audio/wav',       // WAV
  'audio/x-wav',
  'audio/flac',      // FLAC
  'audio/aac',       // AAC
  'audio/ogg',       // OGG
  'audio/mp4',       // M4A
  'audio/x-m4a'
]

const ALLOWED_EXTENSIONS = ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'opus']

const MAX_SIZE = 50 * 1024 * 1024 // 50 MB

export function useFileUpload() {
  const store = useLibraryStore()

  const isUploading = ref(false)
  const uploadProgress = ref(0)
  const uploadError = ref<string | null>(null)
  const selectedFile = ref<File | null>(null)

  function validateFile(file: File): string | null {
    // Check MIME type
    if (!ALLOWED_TYPES.includes(file.type)) {
      // Fallback to extension check
      const ext = file.name.split('.').pop()?.toLowerCase()
      if (!ext || !ALLOWED_EXTENSIONS.includes(ext)) {
        return 'Formato no permitido. Use: MP3, WAV, FLAC, AAC, OGG, M4A'
      }
    }

    // Check file size
    if (file.size > MAX_SIZE) {
      return `Archivo excede el limite de ${formatSize(MAX_SIZE)}`
    }

    // Check if file is empty
    if (file.size === 0) {
      return 'El archivo esta vacio'
    }

    return null
  }

  function formatSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  async function uploadFile(file: File, displayName?: string) {
    uploadError.value = null
    selectedFile.value = file

    // Validate
    const error = validateFile(file)
    if (error) {
      uploadError.value = error
      return null
    }

    isUploading.value = true
    uploadProgress.value = 0

    try {
      // Simulate progress (real progress would need XHR)
      const progressInterval = setInterval(() => {
        if (uploadProgress.value < 90) {
          uploadProgress.value += 10
        }
      }, 200)

      const message = await store.uploadAudio(file, displayName)

      clearInterval(progressInterval)
      uploadProgress.value = 100

      return message
    } catch (err: any) {
      uploadError.value = err.message || 'Error al subir archivo'
      return null
    } finally {
      isUploading.value = false
    }
  }

  function resetUpload() {
    isUploading.value = false
    uploadProgress.value = 0
    uploadError.value = null
    selectedFile.value = null
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault()
    const files = event.dataTransfer?.files
    if (files && files.length > 0) {
      selectedFile.value = files[0]
      return files[0]
    }
    return null
  }

  function handleFileSelect(event: Event) {
    const input = event.target as HTMLInputElement
    if (input.files && input.files.length > 0) {
      selectedFile.value = input.files[0]
      return input.files[0]
    }
    return null
  }

  return {
    isUploading,
    uploadProgress,
    uploadError,
    selectedFile,
    validateFile,
    formatSize,
    uploadFile,
    resetUpload,
    handleDrop,
    handleFileSelect,
    ALLOWED_EXTENSIONS,
    MAX_SIZE
  }
}
