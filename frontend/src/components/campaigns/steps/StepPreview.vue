<script setup lang="ts">
import { ref, inject } from 'vue'
import { SignalIcon } from '@heroicons/vue/24/solid'
import AudioPlayerBase from '@/components/shared/audio/AudioPlayerBase.vue'
import BroadcastModal from '../modals/BroadcastModal.vue'
import type { CampaignWorkflow } from '../composables/useCampaignWorkflow'

// Inject workflow from CampaignDetail
const workflow = inject<CampaignWorkflow>('workflow')!

const emit = defineEmits<{
  saved: []
}>()

const isSaving = ref(false)
const saveSuccess = ref(false)
const showBroadcastModal = ref(false)

async function handleSave() {
  isSaving.value = true
  const success = await workflow.saveAudioToCampaign()
  isSaving.value = false

  if (success) {
    saveSuccess.value = true
    emit('saved')

    // Reset after brief delay
    setTimeout(() => {
      workflow.startOver()
    }, 1500)
  }
}

function handleRegenerate() {
  workflow.goToStep('generate')
}

function handleNewAudio() {
  workflow.startOver()
}

// Format duration for display
function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>

<template>
  <div class="card bg-base-200">
    <div class="card-body">
      <h2 class="card-title">Audio Generado</h2>

      <!-- Audio player -->
      <div v-if="workflow.generatedAudio.value" class="my-4">
        <AudioPlayerBase
          :audio-url="workflow.generatedAudio.value.audio_url"
          :duration="workflow.generatedAudio.value.duration"
          :title="workflow.editedText.value.slice(0, 60) + (workflow.editedText.value.length > 60 ? '...' : '')"
          :subtitle="`${workflow.generatedAudio.value.voice_name} - ${formatDuration(workflow.generatedAudio.value.duration)}`"
          autoplay
        />
      </div>

      <!-- Success message -->
      <div v-if="saveSuccess" class="alert alert-success">
        Audio guardado
      </div>

      <!-- Actions -->
      <div class="card-actions justify-between mt-4">
        <div class="flex gap-2">
          <button
            class="btn btn-ghost btn-sm"
            @click="handleRegenerate"
          >
            Regenerar
          </button>
          <button
            class="btn btn-ghost btn-sm"
            @click="handleNewAudio"
          >
            Nuevo anuncio
          </button>
        </div>

        <div class="flex gap-2">
          <button
            class="btn btn-primary"
            :disabled="isSaving || saveSuccess"
            @click="showBroadcastModal = true"
          >
            <SignalIcon class="h-4 w-4" />
            Enviar a parlantes
          </button>
          <button
            class="btn btn-primary"
            :disabled="isSaving || saveSuccess"
            @click="handleSave"
          >
            <span v-if="isSaving" class="loading loading-spinner loading-sm"></span>
            Guardar
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Broadcast Modal -->
  <BroadcastModal
    :open="showBroadcastModal"
    :audio-id="workflow.generatedAudio.value?.audio_id ?? null"
    @update:open="showBroadcastModal = $event"
  />
</template>
