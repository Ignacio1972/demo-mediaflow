<script setup lang="ts">
import { ref, onMounted, provide, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCampaignStore } from './stores/campaignStore'
import { useCampaignWorkflow } from './composables/useCampaignWorkflow'
import type { CampaignWorkflow } from './composables/useCampaignWorkflow'
import type { CampaignAudio } from '@/types/campaign'
import type { AudioMessage } from '@/types/audio'

// Components
import DynamicIcon from '@/components/shared/ui/DynamicIcon.vue'
import AITrainingPanel from './components/AITrainingPanel.vue'
import RecentMessagesPanel from './components/RecentMessagesPanel.vue'
import CampaignAudioGrid from './components/CampaignAudioGrid.vue'
import StepInput from './steps/StepInput.vue'
import StepSuggestions from './steps/StepSuggestions.vue'
import StepGenerate from './steps/StepGenerate.vue'
import StepPreview from './steps/StepPreview.vue'

// Modals
import BroadcastModal from './modals/BroadcastModal.vue'
import ScheduleModal from '@/components/library/modals/ScheduleModal.vue'

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

function handleSelectRecentMessage(message: AudioMessage) {
  // Pre-fill the text editor with this message
  workflow.editedText.value = message.original_text
  workflow.goToStep('generate')
}

// Refresh trigger for audio grid
const audioGridRefreshTrigger = ref(0)

// Modal state
const showBroadcastModal = ref(false)
const showScheduleModal = ref(false)
const selectedAudio = ref<CampaignAudio | null>(null)
const successToast = ref<string | null>(null)

// Convert CampaignAudio to AudioMessage format for modals
function toAudioMessage(audio: CampaignAudio): AudioMessage {
  return {
    id: audio.id,
    filename: audio.filename,
    display_name: audio.display_name,
    original_text: audio.original_text,
    voice_id: audio.voice_id,
    duration: audio.duration,
    has_jingle: audio.has_jingle,
    music_file: audio.music_file,
    is_favorite: audio.is_favorite,
    status: audio.status,
    created_at: audio.created_at,
    // Fields not in CampaignAudio but needed by AudioMessage
    category_id: campaignId,
    file_path: '',
    file_size: 0,
    sent_to_player: false,
    priority: 'normal'
  } as AudioMessage
}

// Handlers for broadcast/schedule
function handleBroadcast(audio: CampaignAudio) {
  selectedAudio.value = audio
  showBroadcastModal.value = true
}

function handleSchedule(audio: CampaignAudio) {
  selectedAudio.value = audio
  showScheduleModal.value = true
}

function onBroadcastSent(branchCount: number) {
  successToast.value = branchCount === 1
    ? 'Audio enviado a 1 sucursal'
    : `Audio enviado a ${branchCount} sucursales`
  setTimeout(() => { successToast.value = null }, 3000)
}

function onScheduleCreated() {
  successToast.value = 'Audio programado exitosamente'
  setTimeout(() => { successToast.value = null }, 3000)
}

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
    <header class="bg-base-200 border-b border-base-300 px-4 md:px-6 py-3 md:py-4">
      <div class="flex items-center justify-between">
        <!-- Back + Title -->
        <div class="flex items-center gap-2 md:gap-4 min-w-0 flex-1">
          <button
            class="btn btn-ghost btn-sm md:btn-md md:text-xl font-bold"
            @click="goBack"
          >
            Campañas
          </button>

          <div
            v-if="store.currentCampaign"
            class="flex items-center gap-2 min-w-0"
          >
            <DynamicIcon
              :name="store.currentCampaign.icon"
              fallback="Folder"
              class="w-5 h-5 md:w-6 md:h-6 flex-shrink-0"
            />
            <h1 class="text-base md:text-xl font-bold truncate">{{ store.currentCampaign.name }}</h1>
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
    <main v-else-if="store.currentCampaign" class="p-4 md:p-6">
      <div class="flex flex-col md:flex-row gap-4 md:gap-6">
        <!-- Left Column (3/5) - Workflow -->
        <div class="w-full md:flex-[3] space-y-4 md:space-y-6">
          <!-- Dynamic Step Component -->
          <component
            :is="currentStepComponent"
            @saved="handleAudioSaved"
            @generated="handleAudioSaved"
          />
        </div>

        <!-- Right Column (2/5) - Panels -->
        <div class="w-full md:flex-[2] space-y-4">
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
          @broadcast="handleBroadcast"
          @schedule="handleSchedule"
        />
      </div>
    </main>

    <!-- Modals -->
    <BroadcastModal
      v-model:open="showBroadcastModal"
      :audio-id="selectedAudio?.id ?? null"
      @sent="onBroadcastSent"
    />

    <ScheduleModal
      v-model:open="showScheduleModal"
      :message="selectedAudio ? toAudioMessage(selectedAudio) : null"
      @created="onScheduleCreated"
    />

    <!-- Success Toast -->
    <Transition name="toast-scale">
      <div v-if="successToast" class="fixed inset-0 flex items-center justify-center z-50 pointer-events-none">
        <div class="bg-success text-success-content px-8 py-6 rounded-xl shadow-2xl max-w-lg pointer-events-auto">
          <div class="flex items-center gap-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-xl font-semibold">{{ successToast }}</span>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.toast-scale-enter-active,
.toast-scale-leave-active {
  transition: all 0.3s ease;
}

.toast-scale-enter-from,
.toast-scale-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
