<template>
  <div class="audio-preview" v-if="audio">
    <div class="card bg-base-200 shadow-xl">
      <div class="card-body">
        <h3 class="card-title text-xl">
          <span>✅ Audio Generado</span>
          <div class="badge badge-success">Listo</div>
        </h3>

        <!-- Audio Info -->
        <div class="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span class="opacity-70">Archivo:</span>
            <span class="font-mono ml-2">{{ audio.filename }}</span>
          </div>
          <div>
            <span class="opacity-70">Voz:</span>
            <span class="font-semibold ml-2">{{ audio.voice_name }}</span>
          </div>
          <div>
            <span class="opacity-70">Duración:</span>
            <span class="font-mono ml-2">{{ formatDuration(audio.duration) }}</span>
          </div>
          <div>
            <span class="opacity-70">Tamaño:</span>
            <span class="font-mono ml-2">{{ formatFileSize(audio.file_size) }}</span>
          </div>
        </div>

        <!-- Settings Applied -->
        <div class="collapse collapse-arrow bg-base-300 mt-3">
          <input type="checkbox" />
          <div class="collapse-title text-sm font-medium">
            Settings Aplicados
          </div>
          <div class="collapse-content text-xs">
            <div class="grid grid-cols-2 gap-2">
              <div>
                <span class="opacity-70">Estilo:</span>
                <span class="font-mono ml-2">{{ audio.settings_applied.style }}%</span>
              </div>
              <div>
                <span class="opacity-70">Estabilidad:</span>
                <span class="font-mono ml-2">{{ audio.settings_applied.stability }}%</span>
              </div>
              <div>
                <span class="opacity-70">Similitud:</span>
                <span class="font-mono ml-2">{{ audio.settings_applied.similarity_boost }}%</span>
              </div>
              <div>
                <span class="opacity-70">Volumen:</span>
                <span class="font-mono ml-2">{{ audio.settings_applied.volume_adjustment > 0 ? '+' : '' }}{{ audio.settings_applied.volume_adjustment }} dB</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Audio Player -->
        <div class="mt-4">
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

        <!-- Secondary Actions (download, copy URL) -->
        <div class="card-actions justify-end mt-3 pt-3 border-t border-base-300">
          <button
            @click="downloadAudio"
            class="btn btn-ghost btn-sm"
          >
            Descargar
          </button>

          <button
            @click="copyUrl"
            class="btn btn-ghost btn-sm"
            :class="{ 'text-success': urlCopied }"
          >
            {{ urlCopied ? 'Copiado' : 'Copiar URL' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
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
const urlCopied = ref(false)
const savingToLibrary = ref(false)
const sendingToLocal = ref(false)
const sendingToAzuracast = ref(false)
const isSaved = ref(false)

// Reset isSaved when audio changes
watch(() => props.audio?.audio_id, () => {
  isSaved.value = false
})

// Methods
const formatDuration = (seconds: number): string => {
  if (!seconds) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatFileSize = (bytes: number): string => {
  if (!bytes) return '0 KB'
  const kb = bytes / 1024
  return kb < 1024
    ? `${kb.toFixed(1)} KB`
    : `${(kb / 1024).toFixed(2)} MB`
}

const downloadAudio = () => {
  if (!props.audio) return

  const link = document.createElement('a')
  link.href = props.audio.audio_url
  link.download = props.audio.filename
  link.click()
}

const copyUrl = async () => {
  if (!props.audio) return

  try {
    await navigator.clipboard.writeText(props.audio.audio_url)
    urlCopied.value = true

    setTimeout(() => {
      urlCopied.value = false
    }, 2000)
  } catch (e) {
    console.error('Failed to copy URL:', e)
  }
}

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
