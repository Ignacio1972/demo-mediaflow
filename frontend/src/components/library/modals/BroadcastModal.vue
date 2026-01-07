<template>
  <dialog class="modal" :class="{ 'modal-open': open }">
    <div class="modal-box max-w-md">
      <!-- Header -->
      <div class="flex items-center gap-3 mb-4">
        <div class="p-2 bg-primary/10 rounded-lg">
          <SignalIcon class="h-6 w-6 text-primary" />
        </div>
        <div>
          <h2 class="text-xl font-bold">Enviar a Radio</h2>
          <p class="text-sm text-base-content/60">AzuraCast</p>
        </div>
      </div>

      <!-- Message Info -->
      <div v-if="message" class="p-3 bg-base-200 rounded-lg mb-4">
        <p class="font-medium text-sm truncate">{{ message.display_name || message.original_text }}</p>
        <p class="text-xs text-base-content/50 mt-1">{{ message.filename }}</p>
      </div>

      <!-- Broadcast Options -->
      <div class="space-y-3">
        <!-- Interrupt Option (Default) -->
        <label
          class="flex items-start gap-3 cursor-pointer p-4 rounded-lg border-2 transition-all"
          :class="interruptMode ? 'bg-primary/5 border-primary' : 'bg-base-100 border-base-300 hover:border-base-content/20'"
        >
          <input
            type="radio"
            name="broadcast-mode"
            class="radio radio-primary mt-0.5"
            :checked="interruptMode"
            @change="interruptMode = true"
          />
          <div class="flex-1">
            <div class="flex items-center gap-2">
              <span class="font-medium">Reproducir ahora</span>
              <span class="badge badge-primary badge-sm">Recomendado</span>
            </div>
            <p class="text-sm text-base-content/60 mt-1">
              Interrumpe la programacion actual y reproduce el audio inmediatamente
            </p>
          </div>
        </label>

        <!-- Library Only Option -->
        <label
          class="flex items-start gap-3 cursor-pointer p-4 rounded-lg border-2 transition-all"
          :class="!interruptMode ? 'bg-base-200 border-base-content/20' : 'bg-base-100 border-base-300 hover:border-base-content/20'"
        >
          <input
            type="radio"
            name="broadcast-mode"
            class="radio mt-0.5"
            :checked="!interruptMode"
            @change="interruptMode = false"
          />
          <div class="flex-1">
            <span class="font-medium">Solo subir a libreria</span>
            <p class="text-sm text-base-content/60 mt-1">
              Sube el archivo a AzuraCast sin reproducirlo
            </p>
          </div>
        </label>
      </div>

      <!-- Status Message -->
      <div v-if="statusMessage" class="mt-4">
        <div
          class="alert"
          :class="{
            'alert-success': statusType === 'success',
            'alert-error': statusType === 'error',
            'alert-info': statusType === 'info'
          }"
        >
          <span>{{ statusMessage }}</span>
        </div>
      </div>

      <!-- Actions -->
      <div class="modal-action">
        <button class="btn btn-ghost" @click="close" :disabled="isSending">
          Cancelar
        </button>
        <button
          class="btn btn-primary"
          :disabled="isSending"
          @click="send"
        >
          <span v-if="isSending" class="loading loading-spinner loading-sm"></span>
          <template v-else>
            <SignalIcon class="h-4 w-4" />
            {{ interruptMode ? 'Enviar y Reproducir' : 'Subir a Libreria' }}
          </template>
        </button>
      </div>
    </div>

    <form method="dialog" class="modal-backdrop">
      <button @click="close" :disabled="isSending">close</button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { SignalIcon } from '@heroicons/vue/24/solid'
import type { AudioMessage } from '@/types/audio'
import { libraryApi } from '../services/libraryApi'

const props = defineProps<{
  open: boolean
  message: AudioMessage | null
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'sent': [result: { success: boolean; interrupt: boolean; requestId?: string }]
}>()

const interruptMode = ref(true)
const isSending = ref(false)
const statusMessage = ref('')
const statusType = ref<'success' | 'error' | 'info'>('info')

// Reset state when modal opens
watch(() => props.open, (isOpen) => {
  if (isOpen) {
    interruptMode.value = true
    statusMessage.value = ''
    statusType.value = 'info'
  }
})

async function send() {
  if (!props.message) return

  isSending.value = true
  statusMessage.value = ''

  try {
    statusMessage.value = interruptMode.value
      ? 'Enviando audio a la radio...'
      : 'Subiendo archivo a la libreria...'
    statusType.value = 'info'

    const result = await libraryApi.sendToRadio(props.message.id, interruptMode.value)

    if (result.success) {
      statusType.value = 'success'
      statusMessage.value = interruptMode.value
        ? `Audio enviado y reproduciendo (ID: ${result.data?.azuracast?.interrupt?.request_id || 'OK'})`
        : 'Archivo subido a la libreria de AzuraCast'

      emit('sent', {
        success: true,
        interrupt: interruptMode.value,
        requestId: result.data?.azuracast?.interrupt?.request_id
      })

      // Close modal after short delay
      setTimeout(() => {
        close()
      }, 1500)
    } else {
      throw new Error(result.message || 'Error desconocido')
    }
  } catch (error: any) {
    statusType.value = 'error'
    statusMessage.value = error.response?.data?.detail || error.message || 'Error al enviar a la radio'
    console.error('Send to radio error:', error)
  } finally {
    isSending.value = false
  }
}

function close() {
  if (isSending.value) return
  statusMessage.value = ''
  emit('update:open', false)
}
</script>
