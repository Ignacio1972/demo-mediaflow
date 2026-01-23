<template>
  <dialog class="modal modal-open">
    <div class="modal-box max-w-lg">
      <h3 class="font-bold text-lg mb-4">
        <BoltIcon class="w-5 h-5 inline-block mr-2" />
        Nuevo Shortcut
      </h3>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Audio Selection -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">Audio</span>
          </label>
          <select
            v-model="formData.audio_message_id"
            class="select select-bordered w-full"
            required
          >
            <option :value="null" disabled>Selecciona un audio...</option>
            <option
              v-for="audio in filteredAudios"
              :key="audio.id"
              :value="audio.id"
            >
              {{ audio.display_name }}
              <template v-if="audio.duration"> ({{ Math.round(audio.duration) }}s)</template>
            </option>
          </select>
          <label class="label">
            <span class="label-text-alt text-base-content/50">
              Solo audios en categoría "Accesos Directos"
            </span>
          </label>

          <!-- No audios warning -->
          <div v-if="filteredAudios.length === 0" class="alert alert-warning mt-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span class="text-sm">
              No hay audios disponibles. Primero crea un audio y asígnale la categoría "Accesos Directos" en la biblioteca.
            </span>
          </div>
        </div>

        <!-- Custom Name -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">Nombre del Botón</span>
          </label>
          <input
            v-model="formData.custom_name"
            type="text"
            class="input input-bordered"
            placeholder="Ej: Cierre de Caja"
            maxlength="50"
            required
          />
        </div>

        <!-- Icon -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">Icono (Emoji)</span>
          </label>
          <div class="flex gap-2">
            <input
              v-model="formData.custom_icon"
              type="text"
              class="input input-bordered flex-1"
              placeholder="⚡"
              maxlength="10"
            />
            <div class="flex gap-1">
              <button
                v-for="emoji in quickEmojis"
                :key="emoji"
                type="button"
                class="btn btn-ghost btn-sm text-lg"
                @click="formData.custom_icon = emoji"
              >
                {{ emoji }}
              </button>
            </div>
          </div>
        </div>

        <!-- Color -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">Color</span>
          </label>
          <div class="flex gap-2 items-center">
            <input
              v-model="formData.custom_color"
              type="color"
              class="w-12 h-10 rounded cursor-pointer border-2 border-base-300"
            />
            <div class="flex gap-1 flex-wrap">
              <button
                v-for="color in quickColors"
                :key="color"
                type="button"
                class="w-6 h-6 rounded-full border-2 border-base-300 hover:scale-110 transition-transform"
                :style="{ backgroundColor: color }"
                @click="formData.custom_color = color"
              />
            </div>
          </div>
        </div>

        <!-- Preview -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">Vista Previa</span>
          </label>
          <div
            class="w-24 h-24 mx-auto rounded-xl flex flex-col items-center justify-center text-center p-2 transition-all"
            :style="previewStyle"
          >
            <span class="text-3xl mb-1">{{ formData.custom_icon || '⚡' }}</span>
            <span class="text-xs font-medium truncate w-full">
              {{ formData.custom_name || 'Nombre' }}
            </span>
          </div>
        </div>

        <!-- Actions -->
        <div class="modal-action">
          <button
            type="button"
            class="btn btn-ghost"
            @click="$emit('close')"
          >
            Cancelar
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="!isValid"
          >
            Crear Shortcut
          </button>
        </div>
      </form>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button @click="$emit('close')">close</button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { BoltIcon } from '@heroicons/vue/24/outline'
import type { AudioMessage } from '@/types/audio'
import type { ShortcutCreate } from '@/types/shortcut'

const props = defineProps<{
  availableAudios: AudioMessage[]
  existingAudioIds: number[]
}>()

const emit = defineEmits<{
  close: []
  create: [data: ShortcutCreate]
}>()

// Form data
const formData = ref({
  audio_message_id: null as number | null,
  custom_name: '',
  custom_icon: '⚡',
  custom_color: '#10B981',
})

// Quick selections
const quickEmojis = ['⚡', '🔔', '📢', '🎵', '💰', '🚗', '📦', '⏰']
const quickColors = ['#10B981', '#3B82F6', '#EF4444', '#F59E0B', '#8B5CF6', '#EC4899']

// Filter out audios that already have shortcuts
const filteredAudios = computed(() =>
  props.availableAudios.filter(audio => !props.existingAudioIds.includes(audio.id))
)

// Validation
const isValid = computed(() => {
  return (
    formData.value.audio_message_id !== null &&
    formData.value.custom_name.trim().length > 0
  )
})

// Preview style
const previewStyle = computed(() => {
  const color = formData.value.custom_color || '#10B981'
  return {
    backgroundColor: `${color}20`,
    borderColor: `${color}60`,
    border: '2px solid',
  }
})

// Submit handler
const handleSubmit = () => {
  if (!isValid.value || formData.value.audio_message_id === null) return

  const data: ShortcutCreate = {
    audio_message_id: formData.value.audio_message_id,
    custom_name: formData.value.custom_name.trim(),
    custom_icon: formData.value.custom_icon || undefined,
    custom_color: formData.value.custom_color || undefined,
  }

  emit('create', data)
}
</script>
