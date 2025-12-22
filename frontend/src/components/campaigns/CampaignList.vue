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
      />
    </div>

    <!-- Legend -->
    <div v-if="store.campaigns.length > 0" class="mt-8 text-sm opacity-50">
      <span class="mr-4">IA ✓ = IA entrenada para esta campaña</span>
      <span>IA ✗ = Sin entrenamiento de IA</span>
    </div>

    <!-- Modal -->
    <NewCampaignModal
      v-model:isOpen="showNewModal"
      @create="handleCreateCampaign"
    />
  </div>
</template>
