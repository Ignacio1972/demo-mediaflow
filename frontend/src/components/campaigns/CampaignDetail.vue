<script setup lang="ts">
import { ref, onMounted, provide, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCampaignStore } from './stores/campaignStore'
import { useCampaignWorkflow } from './composables/useCampaignWorkflow'
import type { CampaignWorkflow } from './composables/useCampaignWorkflow'
import type { CampaignAudio } from '@/types/campaign'

// Components
import AITrainingPanel from './components/AITrainingPanel.vue'
import RecentMessagesPanel from './components/RecentMessagesPanel.vue'
import CampaignAudioGrid from './components/CampaignAudioGrid.vue'
import StepInput from './steps/StepInput.vue'
import StepSuggestions from './steps/StepSuggestions.vue'
import StepGenerate from './steps/StepGenerate.vue'
import StepPreview from './steps/StepPreview.vue'

// Route & Store
const route = useRoute()
const router = useRouter()
const store = useCampaignStore()

// Campaign ID from route
const campaignId = route.params.id as string

// Workflow with campaign ID
const workflow = useCampaignWorkflow(campaignId)

// Provide workflow to children with proper typing
provide<CampaignWorkflow>('workflow', workflow)

// Load campaign data
onMounted(async () => {
  const campaign = await store.fetchCampaign(campaignId)
  if (!campaign) {
    router.push('/campaigns')
  }
})

// Handlers
function goBack() {
  router.push('/campaigns')
}

async function handleSaveAITraining(instructions: string) {
  await store.updateAITraining(campaignId, instructions)
}

function handleSelectRecentMessage(message: CampaignAudio) {
  // Pre-fill the text editor with this message
  workflow.editedText.value = message.original_text
  workflow.goToStep('generate')
}

// Refresh trigger for audio grid
const audioGridRefreshTrigger = ref(0)

async function handleAudioSaved() {
  // Refresh campaign to update audio count
  await store.fetchCampaign(campaignId)
  // Trigger grid refresh
  audioGridRefreshTrigger.value += 1
}

// Dynamic component based on step
const currentStepComponent = computed(() => {
  switch (workflow.currentStep.value) {
    case 'input': return StepInput
    case 'suggestions': return StepSuggestions
    case 'generate': return StepGenerate
    case 'preview': return StepPreview
    default: return StepInput
  }
})
</script>

<template>
  <div class="min-h-screen">
    <!-- Header -->
    <header class="bg-base-200 border-b border-base-300 px-6 py-4">
      <div class="flex items-center justify-between">
        <!-- Back + Title -->
        <div class="flex items-center gap-4">
          <button
            class="btn btn-ghost btn-sm"
            @click="goBack"
          >
            Campanas
          </button>

          <div
            v-if="store.currentCampaign"
            class="flex items-center gap-2"
          >
            <span class="text-2xl">{{ store.currentCampaign.icon || '' }}</span>
            <h1 class="text-xl font-bold">{{ store.currentCampaign.name }}</h1>
          </div>
        </div>

        <!-- Right side (future: actions) -->
        <div></div>
      </div>
    </header>

    <!-- Loading -->
    <div v-if="store.isLoading" class="flex justify-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <!-- Error -->
    <div v-else-if="store.error" class="p-6">
      <div class="alert alert-error">
        {{ store.error }}
      </div>
    </div>

    <!-- Main Content -->
    <main v-else-if="store.currentCampaign" class="p-6">
      <div class="flex gap-6">
        <!-- Left Column (3/5) - Workflow -->
        <div class="flex-[3] space-y-6">
          <!-- Dynamic Step Component -->
          <component
            :is="currentStepComponent"
            @saved="handleAudioSaved"
          />
        </div>

        <!-- Right Column (2/5) - Panels -->
        <div class="flex-[2] space-y-4">
          <!-- AI Training Panel -->
          <AITrainingPanel
            :campaign-id="campaignId"
            :initial-instructions="store.currentCampaign.ai_instructions"
            @save="handleSaveAITraining"
          />

          <!-- Recent Messages Panel -->
          <RecentMessagesPanel
            :campaign-id="campaignId"
            @select="handleSelectRecentMessage"
          />
        </div>
      </div>

      <!-- Audio Grid -->
      <div class="mt-8">
        <CampaignAudioGrid
          :campaign-id="campaignId"
          :refresh-trigger="audioGridRefreshTrigger"
        />
      </div>
    </main>
  </div>
</template>
