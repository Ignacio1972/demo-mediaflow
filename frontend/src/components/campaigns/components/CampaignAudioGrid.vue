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
  <div class="card bg-base-200">
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
        <CampaignAudioCard
          v-for="audio in audios"
          :key="audio.id"
          :audio="audio"
          @play="handlePlay"
          @delete="handleDelete"
          @schedule="emit('schedule', $event)"
          @broadcast="emit('broadcast', $event)"
        />
      </div>
    </div>
  </div>
</template>
