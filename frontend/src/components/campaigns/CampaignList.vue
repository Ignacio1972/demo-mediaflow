<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCampaignStore } from './stores/campaignStore'
import CampaignCard from './components/CampaignCard.vue'
import NewCampaignModal from './modals/NewCampaignModal.vue'
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

// Current year for header
const currentYear = new Date().getFullYear()
</script>

<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-2xl font-bold">
        Campañas {{ currentYear }}
      </h1>
      <button
        class="btn btn-primary"
        @click="showNewModal = true"
      >
        + Nueva
      </button>
    </div>

    <!-- Loading -->
    <div v-if="store.isLoading" class="flex justify-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <!-- Error -->
    <div v-else-if="store.error" class="alert alert-error">
      {{ store.error }}
    </div>

    <!-- Empty state -->
    <div
      v-else-if="store.campaigns.length === 0"
      class="text-center py-12 opacity-70"
    >
      <div class="text-5xl mb-4">📭</div>
      <p>No hay campañas aún</p>
      <button
        class="btn btn-primary btn-sm mt-4"
        @click="showNewModal = true"
      >
        Crear primera campaña
      </button>
    </div>

    <!-- Campaigns grid -->
    <div
      v-else
      class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4"
    >
      <CampaignCard
        v-for="campaign in store.campaigns"
        :key="campaign.id"
        :campaign="campaign"
        @click="handleCampaignClick"
        @dragStart="handleDragStart(campaign, $event)"
        @dragOver="handleDragOver"
        @drop="handleDrop(campaign)"
        @dragEnd="handleDragEnd"
      />
    </div>

    <!-- Modal -->
    <NewCampaignModal
      v-model:isOpen="showNewModal"
      @create="handleCreateCampaign"
    />
  </div>
</template>
