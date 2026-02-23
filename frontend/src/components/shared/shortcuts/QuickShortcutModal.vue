<template>
  <dialog class="modal modal-open">
    <div class="modal-box max-w-sm">
      <h3 class="font-bold text-lg mb-4">Crear Shortcut</h3>

      <!-- Already has shortcut -->
      <div v-if="alreadyHasShortcut" class="text-center py-4">
        <div class="text-4xl mb-3">⚡</div>
        <p class="text-base-content/70">Este audio ya tiene un shortcut</p>
        <div class="mt-6">
          <button class="btn btn-ghost btn-block" @click="emit('close')">Cerrar</button>
        </div>
      </div>

      <!-- Max shortcuts reached -->
      <div v-else-if="shortcutCount >= 8" class="text-center py-4">
        <div class="text-4xl mb-3">⚠️</div>
        <p class="text-base-content/70">Debes eliminar un shortcut antes de agregar otro</p>
        <div class="mt-6">
          <button class="btn btn-ghost btn-block" @click="emit('close')">Cerrar</button>
        </div>
      </div>

      <!-- Create form -->
      <div v-else>
        <!-- Name -->
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text font-medium">Nombre</span>
          </label>
          <input
            v-model="name"
            type="text"
            class="input input-bordered"
            maxlength="50"
            placeholder="Nombre del shortcut"
          />
        </div>

        <!-- Color -->
        <div class="form-control mb-6">
          <label class="label">
            <span class="label-text font-medium">Color</span>
          </label>
          <div class="flex gap-2">
            <button
              v-for="c in colors"
              :key="c"
              type="button"
              class="w-10 h-10 rounded-full border-4 transition-transform hover:scale-110"
              :class="selectedColor === c ? 'border-base-content scale-110' : 'border-transparent'"
              :style="{ backgroundColor: c }"
              @click="selectedColor = c"
            />
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-2">
          <button class="btn btn-ghost flex-1" @click="emit('close')">
            Cancelar
          </button>
          <button
            class="btn btn-primary flex-1"
            :disabled="!name.trim() || isCreating"
            @click="handleCreate"
          >
            <span v-if="isCreating" class="loading loading-spinner loading-sm"></span>
            Crear Shortcut
          </button>
        </div>
      </div>
    </div>

    <form method="dialog" class="modal-backdrop">
      <button @click="emit('close')">close</button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { apiClient } from '@/api/client'
import type { Shortcut } from '@/types/shortcut'

const props = defineProps<{
  audioId: number
  audioName: string
  shortcutCount: number
  alreadyHasShortcut: boolean
}>()

const emit = defineEmits<{
  close: []
  created: []
}>()

const colors = ['#10B981', '#3B82F6', '#EF4444', '#F59E0B', '#8B5CF6', '#EC4899']

const name = ref(props.audioName.slice(0, 50))
const selectedColor = ref(colors[0])
const isCreating = ref(false)

async function handleCreate() {
  if (!name.value.trim()) return

  isCreating.value = true
  try {
    await apiClient.post<Shortcut>('/api/v1/settings/shortcuts', {
      audio_message_id: props.audioId,
      custom_name: name.value.trim(),
      custom_color: selectedColor.value,
    })
    emit('created')
  } catch (e: any) {
    console.error('Failed to create shortcut:', e)
    alert(e.message || 'Error al crear shortcut')
  } finally {
    isCreating.value = false
  }
}
</script>
