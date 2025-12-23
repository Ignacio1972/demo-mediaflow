<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCampaignStore } from './stores/campaignStore'
import CampaignCardV2 from './components/CampaignCardV2.vue'
import NewCampaignModal from './modals/NewCampaignModal.vue'
import { PlusIcon, RocketLaunchIcon } from '@heroicons/vue/24/outline'
import type { Campaign, CampaignCreate } from '@/types/campaign'

const router = useRouter()
const store = useCampaignStore()

// Modal state
const showNewModal = ref(false)

// Drag and drop state
const draggedCampaign = ref<Campaign | null>(null)

// Load campaigns on mount
onMounted(() => {
  store.fetchCampaigns()
})

// Computed
const currentYear = new Date().getFullYear()
const totalAudios = computed(() =>
  store.campaigns.reduce((sum, c) => sum + (c.audio_count || 0), 0)
)

// Handlers
function handleCampaignClick(campaign: Campaign) {
  router.push(`/campaigns/${campaign.id}`)
}

async function handleCreateCampaign(data: CampaignCreate) {
  try {
    await store.createCampaign(data)
  } catch (error) {
    console.error('Create campaign failed:', error)
  }
}

// Drag handlers
function handleDragStart(campaign: Campaign, event: DragEvent) {
  draggedCampaign.value = campaign
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', campaign.id)
  }
}

function handleDragOver(event: DragEvent) {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
}

async function handleDrop(targetCampaign: Campaign) {
  if (!draggedCampaign.value || draggedCampaign.value.id === targetCampaign.id) {
    return
  }

  const currentOrder = store.campaigns.map(c => c.id)
  const draggedIndex = currentOrder.indexOf(draggedCampaign.value.id)
  const targetIndex = currentOrder.indexOf(targetCampaign.id)

  currentOrder.splice(draggedIndex, 1)
  currentOrder.splice(targetIndex, 0, draggedCampaign.value.id)

  try {
    await store.reorderCampaigns(currentOrder)
  } catch (error) {
    console.error('Reorder failed:', error)
  }
}

function handleDragEnd() {
  draggedCampaign.value = null
}
</script>

<template>
  <div class="min-h-screen bg-base-100">
    <div class="container mx-auto px-6 py-8 max-w-7xl">
      <!-- Header Section -->
      <div class="mb-10">
        <div class="flex items-start justify-between">
          <!-- Title & Stats -->
          <div>
            <div class="flex items-center gap-3 mb-2">
              <div class="flex items-center justify-center w-10 h-10 bg-primary/10 rounded-xl">
                <RocketLaunchIcon class="w-5 h-5 text-primary" />
              </div>
              <h1 class="text-3xl font-bold tracking-tight">Campañas</h1>
              <span class="text-3xl font-light text-base-content/30">{{ currentYear }}</span>
            </div>
            <p class="text-base-content/50 ml-13">
              {{ store.campaigns.length }} campañas · {{ totalAudios }} audios generados
            </p>
          </div>

          <!-- New Campaign Button (hidden on mobile) -->
          <button
            class="hidden md:flex btn btn-primary gap-2 rounded-xl shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 transition-all"
            @click="showNewModal = true"
          >
            <PlusIcon class="w-5 h-5" />
            Nueva Campaña
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="store.isLoading" class="flex flex-col items-center justify-center py-20">
        <span class="loading loading-spinner loading-lg text-primary"></span>
        <p class="text-sm text-base-content/50 mt-4">Cargando campañas...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="store.error" class="max-w-md mx-auto">
        <div class="alert bg-error/10 text-error border-0 rounded-2xl">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>{{ store.error }}</span>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="store.campaigns.length === 0"
        class="flex flex-col items-center justify-center py-20"
      >
        <div class="relative mb-6">
          <!-- Decorative circles -->
          <div class="absolute -inset-4 bg-primary/5 rounded-full animate-pulse"></div>
          <div class="relative flex items-center justify-center w-24 h-24 bg-base-200 rounded-2xl">
            <RocketLaunchIcon class="w-12 h-12 text-base-content/20" />
          </div>
        </div>
        <h3 class="text-xl font-semibold mb-2">Sin campañas aún</h3>
        <p class="text-base-content/50 text-center max-w-sm mb-6">
          Las campañas te ayudan a organizar los audios por temporada o evento especial
        </p>
        <button
          class="btn btn-primary gap-2 rounded-xl"
          @click="showNewModal = true"
        >
          <PlusIcon class="w-5 h-5" />
          Crear primera campaña
        </button>
      </div>

      <!-- Campaigns Grid -->
      <div
        v-else
        class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-5"
      >
        <CampaignCardV2
          v-for="(campaign, index) in store.campaigns"
          :key="campaign.id"
          :campaign="campaign"
          :style="{ animationDelay: `${index * 50}ms` }"
          class="campaign-card-enter"
          @click="handleCampaignClick"
          @dragStart="handleDragStart(campaign, $event)"
          @dragOver="handleDragOver"
          @drop="handleDrop(campaign)"
          @dragEnd="handleDragEnd"
        />

        <!-- Add Campaign Card (always last) -->
        <button
          @click="showNewModal = true"
          class="group flex flex-col items-center justify-center min-h-[180px] border-2 border-dashed border-base-300 rounded-2xl hover:border-primary hover:bg-primary/5 transition-all duration-200"
        >
          <div class="flex items-center justify-center w-12 h-12 bg-base-200 group-hover:bg-primary/10 rounded-xl transition-colors mb-3">
            <PlusIcon class="w-6 h-6 text-base-content/40 group-hover:text-primary transition-colors" />
          </div>
          <span class="text-sm text-base-content/50 group-hover:text-primary transition-colors">
            Agregar
          </span>
        </button>
      </div>

      <!-- Modal -->
      <NewCampaignModal
        v-model:isOpen="showNewModal"
        @create="handleCreateCampaign"
      />
    </div>
  </div>
</template>

<style scoped>
.ml-13 {
  margin-left: 3.25rem;
}

/* Staggered entrance animation */
.campaign-card-enter {
  animation: cardEnter 0.4s ease-out backwards;
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>
