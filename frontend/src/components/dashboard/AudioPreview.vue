<template>
  <div class="audio-preview" v-if="audio">
    <div class="card bg-base-200 shadow-xl">
      <div class="card-body">
        <!-- Audio Player -->
        <div>
          <audio
            ref="audioPlayer"
            :src="audio.audio_url"
            controls
            class="w-full"
            @play="isPlaying = true"
            @pause="isPlaying = false"
            @ended="isPlaying = false"
          ></audio>
        </div>

        <!-- Main Action Buttons (3 buttons like old dashboard) -->
        <div class="flex flex-wrap gap-3 mt-4 justify-end">
          <!-- Guardar en Biblioteca -->
          <button
            @click="saveToLibrary"
            class="btn btn-success"
            :class="{ 'btn-disabled': isSaved }"
            :disabled="savingToLibrary || isSaved"
          >
            <span v-if="savingToLibrary" class="loading loading-spinner loading-xs"></span>
            <span v-else-if="isSaved">Guardado</span>
            <span v-else>Guardar en Biblioteca</span>
          </button>

          <!-- Enviar a Máquina Local -->
          <button
            @click="sendToLocalPlayer"
            class="btn btn-outline"
            :disabled="sendingToLocal"
            title="Enviar al reproductor local"
          >
            <span v-if="sendingToLocal" class="loading loading-spinner loading-xs"></span>
            <span v-else>Enviar a Maquina Local</span>
          </button>

          <!-- Enviar a AzuraCast -->
          <button
            @click="sendToAzuracast"
            class="btn btn-outline"
            :disabled="sendingToAzuracast"
            title="Enviar a la radio AzuraCast"
          >
            <span v-if="sendingToAzuracast" class="loading loading-spinner loading-xs"></span>
            <span v-else>Enviar a AzuraCast</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useAudioStore } from '@/stores/audio'
import type { AudioGenerateResponse } from '@/types/audio'

// Props
const props = defineProps<{
  audio: AudioGenerateResponse | null
}>()

// Store
const audioStore = useAudioStore()

// State
const audioPlayer = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const savingToLibrary = ref(false)
const sendingToLocal = ref(false)
const sendingToAzuracast = ref(false)
const isSaved = ref(false)

// Reset isSaved when audio changes
watch(() => props.audio?.audio_id, () => {
  isSaved.value = false
})

// Auto-play when new audio is generated (like legacy system)
watch(() => props.audio, async (newAudio, oldAudio) => {
  // Check if we have a new audio (different audio_id or first time)
  if (newAudio && (!oldAudio || newAudio.audio_id !== oldAudio.audio_id)) {
    console.log('🎵 New audio detected, preparing auto-play:', newAudio.filename)

    // Wait for DOM to update and audio element to be created
    await nextTick()

    // Double-check that audioPlayer ref is available
    if (audioPlayer.value) {
      // Small delay to ensure the src is loaded
      setTimeout(async () => {
        try {
          await audioPlayer.value!.play()
          console.log('🔊 Auto-playing generated audio:', newAudio.filename)
        } catch (error) {
          console.warn('⚠️ Auto-play prevented by browser:', error)
          // Browser blocked autoplay - user will need to click play manually
        }
      }, 100)
    } else {
      console.warn('⚠️ Audio player element not available for auto-play')
    }
  }
}, { deep: true })

// Save to Library
const saveToLibrary = async () => {
  if (!props.audio) return

  savingToLibrary.value = true

  try {
    await audioStore.saveToLibrary(props.audio.audio_id)
    isSaved.value = true
    console.log('Guardado en biblioteca:', props.audio.filename)
  } catch (e) {
    console.error('Error al guardar en biblioteca:', e)
    alert('Error al guardar en biblioteca')
  } finally {
    savingToLibrary.value = false
  }
}

// Send to Local Player
const sendToLocalPlayer = async () => {
  if (!props.audio) return

  sendingToLocal.value = true

  try {
    // TODO: Implement local player API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    console.log('Enviado a maquina local:', props.audio.filename)
    alert('Audio enviado a Maquina Local')
  } catch (e) {
    console.error('Error al enviar a maquina local:', e)
    alert('Error al enviar a Maquina Local')
  } finally {
    sendingToLocal.value = false
  }
}

// Send to AzuraCast
const sendToAzuracast = async () => {
  if (!props.audio) return

  sendingToAzuracast.value = true

  try {
    // TODO: Implement AzuraCast API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    console.log('Enviado a AzuraCast:', props.audio.filename)
    alert('Audio enviado a AzuraCast')
  } catch (e) {
    console.error('Error al enviar a AzuraCast:', e)
    alert('Error al enviar a AzuraCast')
  } finally {
    sendingToAzuracast.value = false
  }
}
</script>

<style scoped>
audio {
  border-radius: 0.5rem;
}
</style>
