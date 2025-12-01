<template>
  <dialog class="modal modal-open">
    <div class="modal-box max-w-lg">
      <h3 class="font-bold text-lg mb-4">
        🎙️ Agregar Nueva Voz
      </h3>

      <form @submit.prevent="handleSubmit">
        <div class="space-y-4">
          <!-- Voice ID -->
          <div class="form-control">
            <label class="label">
              <span class="label-text">ID de Voz *</span>
              <span class="label-text-alt text-base-content/50">Único, sin espacios</span>
            </label>
            <input
              v-model="formData.id"
              type="text"
              class="input input-bordered"
              placeholder="ej: juan_carlos"
              pattern="[a-z0-9_]+"
              required
              @input="sanitizeId"
            />
            <label class="label">
              <span class="label-text-alt text-base-content/50">
                Solo letras minúsculas, números y guiones bajos
              </span>
            </label>
          </div>

          <!-- Name -->
          <div class="form-control">
            <label class="label">
              <span class="label-text">Nombre *</span>
            </label>
            <input
              v-model="formData.name"
              type="text"
              class="input input-bordered"
              placeholder="ej: Juan Carlos"
              required
            />
          </div>

          <!-- ElevenLabs ID -->
          <div class="form-control">
            <label class="label">
              <span class="label-text">ElevenLabs Voice ID *</span>
            </label>
            <input
              v-model="formData.elevenlabs_id"
              type="text"
              class="input input-bordered font-mono text-sm"
              placeholder="ej: G4IAP30yc6c1gK0csDfu"
              required
            />
            <label class="label">
              <span class="label-text-alt text-base-content/50">
                Encuéntralo en tu cuenta de ElevenLabs
              </span>
            </label>
          </div>

          <!-- Gender -->
          <div class="form-control">
            <label class="label">
              <span class="label-text">Género</span>
            </label>
            <select v-model="formData.gender" class="select select-bordered">
              <option value="">Sin especificar</option>
              <option value="M">Masculino</option>
              <option value="F">Femenino</option>
            </select>
          </div>

          <!-- Description -->
          <div class="form-control">
            <label class="label">
              <span class="label-text">Descripción (opcional)</span>
            </label>
            <textarea
              v-model="formData.description"
              class="textarea textarea-bordered h-20"
              placeholder="Descripción de la voz..."
            ></textarea>
          </div>

          <!-- Default Settings Info -->
          <div class="alert alert-info">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div>
              <div class="font-semibold">Settings por defecto</div>
              <div class="text-sm">
                La voz se creará con settings estándar. Podrás ajustarlos después en el editor.
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="modal-action">
          <button
            type="button"
            class="btn btn-ghost"
            @click="$emit('close')"
            :disabled="isSubmitting"
          >
            Cancelar
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="isSubmitting || !isFormValid"
          >
            <span v-if="isSubmitting" class="loading loading-spinner loading-sm"></span>
            {{ isSubmitting ? 'Creando...' : 'Crear Voz' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Backdrop -->
    <form method="dialog" class="modal-backdrop">
      <button @click="$emit('close')">close</button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import type { VoiceSettings } from '../composables/useVoiceManager'

const emit = defineEmits<{
  close: []
  create: [voice: Partial<VoiceSettings>]
}>()

const isSubmitting = ref(false)

const formData = reactive({
  id: '',
  name: '',
  elevenlabs_id: '',
  gender: '' as '' | 'M' | 'F',
  description: '',
})

// Computed
const isFormValid = computed(() => {
  return (
    formData.id.trim() !== '' &&
    formData.name.trim() !== '' &&
    formData.elevenlabs_id.trim() !== '' &&
    /^[a-z0-9_]+$/.test(formData.id)
  )
})

// Sanitize ID to only allow lowercase, numbers, and underscores
const sanitizeId = () => {
  formData.id = formData.id
    .toLowerCase()
    .replace(/[^a-z0-9_]/g, '_')
    .replace(/_+/g, '_')
}

// Submit handler
const handleSubmit = async () => {
  if (!isFormValid.value) return

  isSubmitting.value = true

  try {
    const voiceData: Partial<VoiceSettings> = {
      id: formData.id.trim(),
      name: formData.name.trim(),
      elevenlabs_id: formData.elevenlabs_id.trim(),
      gender: formData.gender || undefined,
      description: formData.description.trim() || undefined,
      // Default settings
      active: true,
      is_default: false,
      style: 50,
      stability: 55,
      similarity_boost: 80,
      use_speaker_boost: true,
      volume_adjustment: 0,
    }

    emit('create', voiceData)
  } finally {
    isSubmitting.value = false
  }
}
</script>
