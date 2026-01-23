<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title text-lg mb-4">
        <PencilIcon class="w-5 h-5" />
        Editar Shortcut
      </h2>

      <form @submit.prevent="handleSubmit" class="space-y-4">
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
          <label class="label">
            <span class="label-text-alt text-base-content/50">
              {{ formData.custom_name?.length || 0 }}/50 caracteres
            </span>
          </label>
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
            <!-- Quick emoji picker -->
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
            <span class="label-text font-medium">Color del Botón</span>
          </label>
          <div class="flex gap-2 items-center">
            <input
              v-model="formData.custom_color"
              type="color"
              class="w-12 h-10 rounded cursor-pointer border-2 border-base-300"
            />
            <input
              v-model="formData.custom_color"
              type="text"
              class="input input-bordered flex-1"
              placeholder="#10B981"
              pattern="^#[0-9A-Fa-f]{6}$"
            />
            <!-- Quick color picker -->
            <div class="flex gap-1">
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

        <!-- Position -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">Posición en el Grid</span>
          </label>
          <div class="grid grid-cols-6 gap-2">
            <button
              v-for="pos in 6"
              :key="pos"
              type="button"
              class="btn btn-sm"
              :class="{
                'btn-primary': formData.position === pos,
                'btn-outline': formData.position !== pos && isPositionAvailable(pos),
                'btn-disabled opacity-30': !isPositionAvailable(pos) && formData.position !== pos,
              }"
              @click="setPosition(pos)"
              :disabled="!isPositionAvailable(pos) && formData.position !== pos"
            >
              {{ pos }}
            </button>
          </div>
          <label class="label">
            <span class="label-text-alt text-base-content/50">
              {{ formData.position ? `Posición ${formData.position} asignada` : 'Sin posición (no visible en mobile)' }}
            </span>
            <button
              v-if="formData.position"
              type="button"
              class="btn btn-ghost btn-xs"
              @click="clearPosition"
            >
              Quitar del grid
            </button>
          </label>
        </div>

        <!-- Audio Info (read-only) -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">Audio Vinculado</span>
          </label>
          <div class="bg-base-200 rounded-lg p-3">
            <div class="flex items-center gap-3">
              <MusicalNoteIcon class="w-5 h-5 text-primary" />
              <div class="flex-1 min-w-0">
                <div class="font-medium truncate">
                  {{ shortcut.audio_message?.display_name || 'Sin audio' }}
                </div>
                <div class="text-xs text-base-content/50">
                  {{ shortcut.audio_message?.duration ? `${Math.round(shortcut.audio_message.duration)}s` : '' }}
                </div>
              </div>
              <!-- Play preview -->
              <button
                v-if="shortcut.audio_message?.audio_url"
                type="button"
                class="btn btn-ghost btn-sm btn-circle"
                @click="togglePreview"
              >
                <PlayIcon v-if="!isPlaying" class="w-5 h-5" />
                <StopIcon v-else class="w-5 h-5" />
              </button>
            </div>
          </div>
          <audio ref="audioRef" :src="shortcut.audio_message?.audio_url" @ended="isPlaying = false" />
        </div>

        <!-- Preview -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">Vista Previa</span>
          </label>
          <div
            class="w-32 h-32 mx-auto rounded-xl flex flex-col items-center justify-center text-center p-3 transition-all"
            :style="previewStyle"
          >
            <span class="text-4xl mb-2">{{ formData.custom_icon || '⚡' }}</span>
            <span class="text-sm font-medium truncate w-full">
              {{ formData.custom_name || 'Nombre' }}
            </span>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-between pt-4 border-t border-base-300">
          <button
            type="button"
            class="btn btn-error btn-outline"
            @click="$emit('delete', shortcut.id)"
          >
            <TrashIcon class="w-4 h-4" />
            Eliminar
          </button>
          <div class="flex gap-2">
            <button
              type="button"
              class="btn btn-ghost"
              @click="$emit('cancel')"
            >
              Cancelar
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isSaving || !isValid"
            >
              <span v-if="isSaving" class="loading loading-spinner loading-sm"></span>
              Guardar
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
  PencilIcon,
  TrashIcon,
  MusicalNoteIcon,
  PlayIcon,
  StopIcon,
} from '@heroicons/vue/24/outline'
import type { Shortcut, ShortcutUpdate } from '@/types/shortcut'

const props = defineProps<{
  shortcut: Shortcut
  availablePositions: number[]
  isSaving: boolean
}>()

const emit = defineEmits<{
  save: [updates: ShortcutUpdate]
  cancel: []
  delete: [id: number]
  'update-position': [position: number | null]
}>()

// Form data
const formData = ref({
  custom_name: '',
  custom_icon: '',
  custom_color: '',
  position: null as number | null,
})

// Audio preview
const audioRef = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)

// Quick selections
const quickEmojis = ['⚡', '🔔', '📢', '🎵', '💰', '🚗', '📦', '⏰']
const quickColors = ['#10B981', '#3B82F6', '#EF4444', '#F59E0B', '#8B5CF6', '#EC4899']

// Watch for shortcut changes
watch(
  () => props.shortcut,
  (newShortcut) => {
    formData.value = {
      custom_name: newShortcut.custom_name || '',
      custom_icon: newShortcut.custom_icon || '',
      custom_color: newShortcut.custom_color || '#10B981',
      position: newShortcut.position ?? null,
    }
  },
  { immediate: true }
)

// Computed
const isValid = computed(() => {
  return formData.value.custom_name.trim().length > 0
})

const previewStyle = computed(() => {
  const color = formData.value.custom_color || '#10B981'
  return {
    backgroundColor: `${color}20`,
    borderColor: `${color}60`,
    border: '2px solid',
  }
})

// Position helpers
const isPositionAvailable = (pos: number): boolean => {
  return props.availablePositions.includes(pos) || formData.value.position === pos
}

const setPosition = (pos: number) => {
  if (formData.value.position === pos) {
    // Toggle off
    formData.value.position = null
  } else {
    formData.value.position = pos
  }
}

const clearPosition = () => {
  formData.value.position = null
}

// Audio preview
const togglePreview = () => {
  if (!audioRef.value) return

  if (isPlaying.value) {
    audioRef.value.pause()
    audioRef.value.currentTime = 0
    isPlaying.value = false
  } else {
    audioRef.value.play()
    isPlaying.value = true
  }
}

// Submit handler
const handleSubmit = () => {
  if (!isValid.value) return

  const updates: ShortcutUpdate = {
    custom_name: formData.value.custom_name.trim(),
    custom_icon: formData.value.custom_icon || undefined,
    custom_color: formData.value.custom_color || undefined,
    position: formData.value.position,
  }

  emit('save', updates)
}
</script>
