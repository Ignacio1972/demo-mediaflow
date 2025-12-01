<template>
  <div class="music-editor card bg-base-100 shadow-xl">
    <div class="card-body">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold text-xl">Editar Track</h3>
        <div class="flex items-center gap-2">
          <span v-if="track.is_default" class="badge badge-warning">Default</span>
          <span
            class="badge"
            :class="track.active ? 'badge-success' : 'badge-ghost'"
          >
            {{ track.active ? 'Activo' : 'Inactivo' }}
          </span>
        </div>
      </div>

      <!-- Audio Preview -->
      <div class="bg-base-200 rounded-lg p-4 mb-6">
        <div class="flex items-center gap-4">
          <button
            @click="togglePlay"
            class="btn btn-circle btn-primary"
          >
            <svg v-if="isPlaying" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>

          <div class="flex-1">
            <input
              type="range"
              :value="currentTime"
              :max="duration"
              @input="seekTo"
              class="range range-primary range-sm"
            />
            <div class="flex justify-between text-xs text-base-content/50 mt-1">
              <span>{{ formatTime(currentTime) }}</span>
              <span>{{ formatTime(duration) }}</span>
            </div>
          </div>
        </div>

        <audio
          ref="audioPlayer"
          :src="track.audio_url"
          @loadedmetadata="onLoadedMetadata"
          @timeupdate="onTimeUpdate"
          @ended="isPlaying = false"
        ></audio>
      </div>

      <!-- Track Info -->
      <div class="grid grid-cols-2 gap-4 mb-6">
        <div class="stat bg-base-200 rounded-lg p-3">
          <div class="stat-title text-xs">Duración</div>
          <div class="stat-value text-lg">{{ formatTime(track.duration || 0) }}</div>
        </div>
        <div class="stat bg-base-200 rounded-lg p-3">
          <div class="stat-title text-xs">Bitrate</div>
          <div class="stat-value text-lg">{{ track.bitrate || '--' }}</div>
        </div>
        <div class="stat bg-base-200 rounded-lg p-3">
          <div class="stat-title text-xs">Tamaño</div>
          <div class="stat-value text-lg">{{ formatFileSize(track.file_size) }}</div>
        </div>
        <div class="stat bg-base-200 rounded-lg p-3">
          <div class="stat-title text-xs">Formato</div>
          <div class="stat-value text-lg uppercase">{{ track.format || 'mp3' }}</div>
        </div>
      </div>

      <!-- Edit Form -->
      <div class="space-y-4">
        <div class="form-control">
          <label class="label">
            <span class="label-text">Nombre</span>
          </label>
          <input
            v-model="editForm.display_name"
            type="text"
            class="input input-bordered"
            placeholder="Nombre del track"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="form-control">
            <label class="label">
              <span class="label-text">Artista</span>
            </label>
            <input
              v-model="editForm.artist"
              type="text"
              class="input input-bordered"
              placeholder="Artista (opcional)"
            />
          </div>

          <div class="form-control">
            <label class="label">
              <span class="label-text">Género</span>
            </label>
            <select v-model="editForm.genre" class="select select-bordered">
              <option value="">Sin género</option>
              <option value="Electronic">Electronic</option>
              <option value="Pop">Pop</option>
              <option value="Rock">Rock</option>
              <option value="Jazz">Jazz</option>
              <option value="Ambient">Ambient</option>
              <option value="Classical">Classical</option>
              <option value="Latin">Latin</option>
              <option value="Other">Otro</option>
            </select>
          </div>
        </div>

        <div class="form-control">
          <label class="label">
            <span class="label-text">Mood</span>
          </label>
          <select v-model="editForm.mood" class="select select-bordered">
            <option value="">Sin mood</option>
            <option value="energetic">Energético</option>
            <option value="calm">Calmado</option>
            <option value="happy">Alegre</option>
            <option value="inspiring">Inspirador</option>
            <option value="relaxed">Relajado</option>
            <option value="upbeat">Animado</option>
            <option value="festive">Festivo</option>
          </select>
        </div>

        <div class="form-control">
          <label class="label cursor-pointer justify-start gap-3">
            <input
              v-model="editForm.active"
              type="checkbox"
              class="toggle toggle-primary"
            />
            <span class="label-text">Track activo (disponible en Dashboard)</span>
          </label>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-between mt-6 pt-4 border-t border-base-300">
        <div class="flex gap-2">
          <button
            v-if="!track.is_default"
            @click="$emit('set-default', track.id)"
            class="btn btn-outline btn-warning btn-sm"
          >
            ⭐ Set Default
          </button>
          <button
            @click="$emit('delete', track.id)"
            class="btn btn-outline btn-error btn-sm"
          >
            🗑️ Eliminar
          </button>
        </div>

        <div class="flex gap-2">
          <button
            @click="resetForm"
            class="btn btn-ghost"
            :disabled="!hasChanges"
          >
            Cancelar
          </button>
          <button
            @click="saveChanges"
            class="btn btn-primary"
            :disabled="!hasChanges || isSaving"
          >
            <span v-if="isSaving" class="loading loading-spinner loading-sm"></span>
            Guardar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import type { MusicTrack } from '@/types/audio'

const props = defineProps<{
  track: MusicTrack
  isSaving: boolean
}>()

const emit = defineEmits<{
  save: [updates: Partial<MusicTrack>]
  delete: [trackId: number]
  'set-default': [trackId: number]
}>()

// Audio player
const audioPlayer = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)

// Edit form
const editForm = reactive({
  display_name: props.track.display_name,
  artist: props.track.artist || '',
  genre: props.track.genre || '',
  mood: props.track.mood || '',
  active: props.track.active,
})

// Reset form when track changes
watch(() => props.track, (newTrack) => {
  editForm.display_name = newTrack.display_name
  editForm.artist = newTrack.artist || ''
  editForm.genre = newTrack.genre || ''
  editForm.mood = newTrack.mood || ''
  editForm.active = newTrack.active

  // Reset audio player
  isPlaying.value = false
  currentTime.value = 0
}, { immediate: true })

const hasChanges = computed(() => {
  return (
    editForm.display_name !== props.track.display_name ||
    editForm.artist !== (props.track.artist || '') ||
    editForm.genre !== (props.track.genre || '') ||
    editForm.mood !== (props.track.mood || '') ||
    editForm.active !== props.track.active
  )
})

const togglePlay = () => {
  if (!audioPlayer.value) return

  if (isPlaying.value) {
    audioPlayer.value.pause()
  } else {
    audioPlayer.value.play()
  }
  isPlaying.value = !isPlaying.value
}

const onLoadedMetadata = () => {
  if (audioPlayer.value) {
    duration.value = audioPlayer.value.duration
  }
}

const onTimeUpdate = () => {
  if (audioPlayer.value) {
    currentTime.value = audioPlayer.value.currentTime
  }
}

const seekTo = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (audioPlayer.value) {
    audioPlayer.value.currentTime = parseFloat(target.value)
  }
}

const formatTime = (seconds: number): string => {
  if (!seconds || isNaN(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatFileSize = (bytes?: number): string => {
  if (!bytes) return '--'
  const mb = bytes / (1024 * 1024)
  return `${mb.toFixed(1)} MB`
}

const resetForm = () => {
  editForm.display_name = props.track.display_name
  editForm.artist = props.track.artist || ''
  editForm.genre = props.track.genre || ''
  editForm.mood = props.track.mood || ''
  editForm.active = props.track.active
}

const saveChanges = () => {
  const updates: Partial<MusicTrack> = {}

  if (editForm.display_name !== props.track.display_name) {
    updates.display_name = editForm.display_name
  }
  if (editForm.artist !== (props.track.artist || '')) {
    updates.artist = editForm.artist || undefined
  }
  if (editForm.genre !== (props.track.genre || '')) {
    updates.genre = editForm.genre || undefined
  }
  if (editForm.mood !== (props.track.mood || '')) {
    updates.mood = editForm.mood || undefined
  }
  if (editForm.active !== props.track.active) {
    updates.active = editForm.active
  }

  emit('save', updates)
}
</script>
