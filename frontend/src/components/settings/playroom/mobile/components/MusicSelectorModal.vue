<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-end sm:items-center justify-center"
        @click.self="$emit('close')"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>

        <!-- Modal Card (slides up on mobile) -->
        <div class="relative bg-base-100 rounded-t-2xl sm:rounded-2xl shadow-2xl w-full sm:max-w-sm max-h-[80vh] overflow-hidden animate-modal-enter">
          <!-- Header -->
          <div class="p-4 border-b border-base-200 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-secondary/10 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
              </div>
              <div>
                <h3 class="font-bold text-base-content">Música de fondo</h3>
                <p class="text-xs text-base-content/60">{{ profileName }}</p>
              </div>
            </div>
            <button
              @click="$emit('close')"
              class="btn btn-ghost btn-sm btn-circle"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Music Options -->
          <div class="p-4 overflow-y-auto max-h-[50vh]">
            <!-- No music option -->
            <label
              class="flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors mb-2"
              :class="selectedMusic === null ? 'bg-primary/10 border border-primary' : 'bg-base-200 hover:bg-base-300'"
            >
              <input
                type="radio"
                name="music"
                :checked="selectedMusic === null"
                @change="selectedMusic = null"
                class="radio radio-primary"
              />
              <div class="flex items-center gap-3 flex-1">
                <div class="w-10 h-10 rounded-lg bg-base-300 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-base-content/50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
                  </svg>
                </div>
                <div>
                  <p class="font-medium text-base-content">Sin música</p>
                  <p class="text-xs text-base-content/60">Solo voz</p>
                </div>
              </div>
            </label>

            <!-- Divider -->
            <div class="divider text-xs text-base-content/40 my-2">Tracks disponibles</div>

            <!-- Music tracks -->
            <div class="space-y-2">
              <label
                v-for="track in musicTracks"
                :key="track.filename"
                class="flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors"
                :class="selectedMusic === track.filename ? 'bg-primary/10 border border-primary' : 'bg-base-200 hover:bg-base-300'"
              >
                <input
                  type="radio"
                  name="music"
                  :value="track.filename"
                  :checked="selectedMusic === track.filename"
                  @change="selectedMusic = track.filename"
                  class="radio radio-primary"
                />
                <div class="flex items-center gap-3 flex-1">
                  <div class="w-10 h-10 rounded-lg bg-secondary/20 flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="font-medium text-base-content truncate">{{ track.display_name }}</p>
                    <p class="text-xs text-base-content/60">
                      {{ formatDuration(track.duration) }}
                      <span v-if="track.is_default" class="ml-1 badge badge-xs badge-secondary">Default</span>
                    </p>
                  </div>
                </div>
              </label>
            </div>

            <!-- Empty state -->
            <div v-if="musicTracks.length === 0" class="text-center py-8 text-base-content/50">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-2 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
              </svg>
              <p class="text-sm">No hay música disponible</p>
            </div>
          </div>

          <!-- Footer -->
          <div class="p-4 border-t border-base-200">
            <button
              @click="confirmSelection"
              class="btn btn-primary w-full"
            >
              Confirmar
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { MusicTrack } from '@/types/audio'

// Props
interface Props {
  show: boolean
  profileName: string
  currentMusic: string | null
  musicTracks: MusicTrack[]
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'select', musicFile: string | null): void
}>()

// Local state
const selectedMusic = ref<string | null>(props.currentMusic)

// Sync with prop when modal opens
watch(() => props.show, (newShow) => {
  if (newShow) {
    selectedMusic.value = props.currentMusic
  }
})

// Confirm selection
const confirmSelection = () => {
  emit('select', selectedMusic.value)
  emit('close')
}

// Format duration helper
const formatDuration = (seconds?: number): string => {
  if (!seconds) return ''
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>

<style scoped>
/* Modal transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .animate-modal-enter {
  animation: slide-up 0.3s ease forwards;
}

.modal-leave-active .animate-modal-enter {
  animation: slide-down 0.2s ease forwards;
}

@keyframes slide-up {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes slide-down {
  from {
    transform: translateY(0);
    opacity: 1;
  }
  to {
    transform: translateY(100%);
    opacity: 0;
  }
}

@media (min-width: 640px) {
  .modal-enter-active .animate-modal-enter {
    animation: scale-up 0.2s ease forwards;
  }

  .modal-leave-active .animate-modal-enter {
    animation: scale-down 0.15s ease forwards;
  }

  @keyframes scale-up {
    from {
      transform: scale(0.95);
      opacity: 0;
    }
    to {
      transform: scale(1);
      opacity: 1;
    }
  }

  @keyframes scale-down {
    from {
      transform: scale(1);
      opacity: 1;
    }
    to {
      transform: scale(0.95);
      opacity: 0;
    }
  }
}
</style>
