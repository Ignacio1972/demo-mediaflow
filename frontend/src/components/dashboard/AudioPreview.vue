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

        <!-- Action Buttons -->
        <div class="card-actions justify-end mt-4">
          <button
            @click="downloadAudio"
            class="btn btn-outline btn-sm"
          >
            ⬇️ Descargar
          </button>

          <button
            @click="copyUrl"
            class="btn btn-outline btn-sm"
            :class="{ 'btn-success': urlCopied }"
          >
            {{ urlCopied ? '✓ Copiado' : '🔗 Copiar URL' }}
          </button>

          <button
            @click="sendToPlayer"
            class="btn btn-primary btn-sm"
            :disabled="sending"
          >
            <span v-if="sending" class="loading loading-spinner loading-xs"></span>
            <span v-else>📡 Enviar al Player</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { AudioGenerateResponse } from '@/types/audio'

// Props
const props = defineProps<{
  audio: AudioGenerateResponse | null
}>()

// State
const audioPlayer = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const urlCopied = ref(false)
const sending = ref(false)

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

const sendToPlayer = async () => {
  if (!props.audio) return

  sending.value = true

  try {
    // TODO: Implement player API call (Semana 2)
    await new Promise(resolve => setTimeout(resolve, 1000))
    console.log('📡 Sent to player:', props.audio.filename)

    alert('✅ Audio enviado al player correctamente')
  } catch (e) {
    console.error('Failed to send to player:', e)
    alert('❌ Error al enviar al player')
  } finally {
    sending.value = false
  }
}
</script>

<style scoped>
audio {
  border-radius: 0.5rem;
}
</style>
