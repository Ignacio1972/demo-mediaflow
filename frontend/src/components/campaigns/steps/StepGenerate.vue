<script setup lang="ts">
import { inject, onMounted } from 'vue'
import { useAudioStore } from '@/stores/audio'
import VoiceSelectorBase from '@/components/shared/audio/VoiceSelectorBase.vue'
import MusicSelectorBase from '@/components/shared/audio/MusicSelectorBase.vue'
import type { CampaignWorkflow } from '../composables/useCampaignWorkflow'

// Inject workflow from CampaignDetail
const workflow = inject<CampaignWorkflow>('workflow')!
const audioStore = useAudioStore()

// Load voices and music on mount
onMounted(async () => {
  await Promise.all([
    audioStore.loadVoices(),
    audioStore.loadMusicTracks()
  ])

  // Set default voice if not selected
  if (!workflow.selectedVoiceId.value && audioStore.voices.length > 0) {
    const defaultVoice = audioStore.voices.find(v => v.is_default) || audioStore.voices[0]
    workflow.selectedVoiceId.value = defaultVoice.id
  }

  // Set default music if enabled and not selected
  if (workflow.addMusic.value && !workflow.selectedMusicFile.value && audioStore.activeMusicTracks.length > 0) {
    const defaultTrack = audioStore.activeMusicTracks.find(t => t.is_default) || audioStore.activeMusicTracks[0]
    workflow.selectedMusicFile.value = defaultTrack.filename
  }
})

function handleBack() {
  workflow.goToStep('suggestions')
}

function handleVoiceSelect(voiceId: string) {
  workflow.selectedVoiceId.value = voiceId
}

function handleMusicToggle(event: Event) {
  const enabled = (event.target as HTMLInputElement).checked
  workflow.addMusic.value = enabled

  if (enabled && !workflow.selectedMusicFile.value && audioStore.activeMusicTracks.length > 0) {
    const defaultTrack = audioStore.activeMusicTracks.find(t => t.is_default) || audioStore.activeMusicTracks[0]
    workflow.selectedMusicFile.value = defaultTrack.filename
  }

  if (!enabled) {
    workflow.selectedMusicFile.value = null
  }
}

function handleMusicSelect(filename: string | null) {
  workflow.selectedMusicFile.value = filename
}
</script>

<template>
  <div class="card bg-base-200">
    <div class="card-body">
      <div class="flex items-center justify-between mb-4">
        <h2 class="card-title">Generar Audio</h2>
        <button class="btn btn-ghost btn-sm" @click="handleBack">
          Volver
        </button>
      </div>

      <!-- Editable text -->
      <div class="form-control mb-6">
        <label class="label">
          <span class="label-text">Texto a convertir en audio</span>
          <span class="label-text-alt">Puedes editarlo</span>
        </label>
        <textarea
          v-model="workflow.editedText.value"
          class="textarea textarea-bordered w-full h-28"
        />
        <label class="label">
          <span class="label-text-alt">{{ workflow.editedText.value.length }} caracteres</span>
        </label>
      </div>

      <!-- Voice selector + Generate button (same row) -->
      <div class="mb-4">
        <label class="label">
          <span class="label-text">Selecciona la voz</span>
        </label>
        <div class="flex flex-col sm:flex-row sm:items-center gap-4">
          <div class="flex-1 min-w-0">
            <VoiceSelectorBase
              :voices="audioStore.activeVoices"
              :selected-voice-id="workflow.selectedVoiceId.value"
              @select="handleVoiceSelect"
            />
          </div>

          <!-- Generate button -->
          <button
            class="btn btn-primary w-full sm:w-auto flex-shrink-0"
            :disabled="!workflow.canGenerateAudio.value"
            @click="workflow.generateAudio"
          >
            <span
              v-if="workflow.isGeneratingAudio.value"
              class="loading loading-spinner"
            ></span>
            Generar Audio
          </button>
        </div>
      </div>

      <!-- Music toggle + selector -->
      <div class="mb-6">
        <div class="form-control">
          <label class="label cursor-pointer justify-start gap-4">
            <input
              type="checkbox"
              class="toggle toggle-primary"
              :checked="workflow.addMusic.value"
              @change="handleMusicToggle"
            />
            <span class="label-text">Agregar musica de fondo</span>
          </label>
        </div>

        <div v-if="workflow.addMusic.value" class="mt-3 ml-4">
          <MusicSelectorBase
            :tracks="audioStore.musicTracks"
            :selected-track-filename="workflow.selectedMusicFile.value"
            @select="handleMusicSelect"
          />
        </div>
      </div>

      <!-- Error -->
      <div v-if="workflow.audioError.value" class="alert alert-error">
        {{ workflow.audioError.value }}
      </div>
    </div>
  </div>
</template>
