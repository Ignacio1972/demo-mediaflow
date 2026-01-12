<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { apiClient } from '@/api/client'
import type { CampaignAudio, CampaignAudiosResponse } from '@/types/campaign'
import CampaignAudioCard from './CampaignAudioCard.vue'

interface Props {
  campaignId: string
  refreshTrigger?: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  schedule: [audio: CampaignAudio]
  broadcast: [audio: CampaignAudio]
}>()

// State
const audios = ref<CampaignAudio[]>([])
const total = ref(0)
const isLoading = ref(false)
const error = ref<string | null>(null)

// Pagination
const limit = 12
const offset = ref(0)

// Currently playing (for exclusive playback)
const currentlyPlaying = ref<number | null>(null)

// Element refs for animations
const audioRefs = ref<Map<number, HTMLElement>>(new Map())

function setAudioRef(id: number, el: any) {
  if (el) {
    audioRefs.value.set(id, el as HTMLElement)
  }
}

// Toast state
const showToast = ref(false)

function showSuccessToast() {
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// Load audios
async function loadAudios() {
  isLoading.value = true
  error.value = null

  try {
    const response = await apiClient.get<CampaignAudiosResponse>(
      `/api/v1/campaigns/${props.campaignId}/audios`,
      { params: { limit, offset: offset.value } }
    )
    audios.value = response.audios
    total.value = response.total
  } catch (err) {
    error.value = 'Error al cargar audios'
    console.error('Load audios error:', err)
  } finally {
    isLoading.value = false
  }
}

// Initial load
onMounted(() => {
  loadAudios()
})

// Refresh when trigger changes
watch(() => props.refreshTrigger, () => {
  loadAudios()
})

// Handle play (stop others)
function handlePlay(audio: CampaignAudio) {
  currentlyPlaying.value = audio.id
}

// Handle delete
async function handleDelete(audio: CampaignAudio) {
  if (!confirm(`¿Eliminar "${audio.display_name}"?`)) return

  try {
    await apiClient.delete(`/api/v1/library/${audio.id}`)
    // Remove from local list
    audios.value = audios.value.filter(a => a.id !== audio.id)
    total.value -= 1
  } catch (err) {
    console.error('Delete error:', err)
    alert('Error al eliminar')
  }
}

// Handle save to library
async function handleSaveToLibrary(audio: CampaignAudio) {
  const audioEl = audioRefs.value.get(audio.id)

  try {
    await apiClient.patch(`/api/v1/audio/${audio.id}/save-to-library`)

    // Slide-out animation to the right
    if (audioEl) {
      audioEl.style.transition = 'transform 0.4s ease, opacity 0.4s ease'
      audioEl.style.transform = 'translateX(100%)'
      audioEl.style.opacity = '0'

      // After animation, remove from list and show toast
      setTimeout(() => {
        audios.value = audios.value.filter(a => a.id !== audio.id)
        total.value -= 1
        audioRefs.value.delete(audio.id)
        showSuccessToast()
      }, 400)
    } else {
      // Fallback if no element ref
      audios.value = audios.value.filter(a => a.id !== audio.id)
      total.value -= 1
      showSuccessToast()
    }
  } catch (err) {
    console.error('Save to library error:', err)
    // Reset styles on error
    if (audioEl) {
      audioEl.style.transition = ''
      audioEl.style.transform = ''
      audioEl.style.opacity = ''
    }
    alert('Error al guardar en biblioteca')
  }
}

// Pagination
const hasMore = computed(() => offset.value + limit < total.value)
const hasPrev = computed(() => offset.value > 0)

function nextPage() {
  if (hasMore.value) {
    offset.value += limit
    loadAudios()
  }
}

function prevPage() {
  if (hasPrev.value) {
    offset.value -= limit
    loadAudios()
  }
}
</script>

<template>
  <div class="card bg-base-200 relative">
    <div class="card-body">
      <!-- Header -->
      <div class="flex items-center justify-between mb-4">
        <h2 class="card-title">
          📚 Audios de esta Campaña
          <span class="badge badge-ghost">{{ total }}</span>
        </h2>

        <!-- Pagination -->
        <div v-if="total > limit" class="join">
          <button
            class="btn btn-sm join-item"
            :disabled="!hasPrev"
            @click="prevPage"
          >
            ←
          </button>
          <button class="btn btn-sm join-item btn-disabled">
            {{ Math.floor(offset / limit) + 1 }} / {{ Math.ceil(total / limit) }}
          </button>
          <button
            class="btn btn-sm join-item"
            :disabled="!hasMore"
            @click="nextPage"
          >
            →
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="isLoading" class="flex justify-center py-8">
        <span class="loading loading-spinner loading-lg"></span>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="alert alert-error">
        {{ error }}
      </div>

      <!-- Empty state -->
      <div
        v-else-if="audios.length === 0"
        class="text-center py-12 opacity-50"
      >
        <div class="text-4xl mb-2">📭</div>
        <p>Sin audios aún</p>
        <p class="text-sm">Crea tu primer anuncio para esta campaña</p>
      </div>

      <!-- Grid -->
      <div
        v-else
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        <div
          v-for="audio in audios"
          :key="audio.id"
          :ref="el => setAudioRef(audio.id, el)"
          class="audio-card-wrapper"
        >
          <CampaignAudioCard
            :audio="audio"
            @play="handlePlay"
            @delete="handleDelete"
            @save-to-library="handleSaveToLibrary"
            @schedule="emit('schedule', $event)"
            @broadcast="emit('broadcast', $event)"
          />
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <div class="toast toast-end toast-bottom z-50">
      <Transition name="toast">
        <div v-if="showToast" class="alert alert-success">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Guardado en biblioteca</span>
        </div>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
/* Card wrapper for animations */
.audio-card-wrapper {
  transform: translateX(0);
  opacity: 1;
}

/* Toast animation */
.toast-enter-active {
  animation: toast-in 0.3s ease-out;
}

.toast-leave-active {
  animation: toast-out 0.3s ease-in;
}

@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes toast-out {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(100%);
  }
}
</style>
