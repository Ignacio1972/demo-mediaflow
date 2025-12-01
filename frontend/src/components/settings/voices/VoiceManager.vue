<template>
  <div class="voice-manager min-h-screen bg-base-100 p-6">
    <div class="container mx-auto max-w-7xl">
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 class="text-3xl font-bold text-primary flex items-center gap-3">
            <span class="text-4xl">🎙️</span>
            Voice Manager
          </h1>
          <p class="text-sm text-base-content/60 mt-1">
            Gestiona voces y sus configuraciones individuales para TTS
          </p>
        </div>
        <button
          @click="showAddModal = true"
          class="btn btn-primary"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Agregar Voz
        </button>
      </div>

      <!-- Toast Messages -->
      <div v-if="error" class="alert alert-error mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ error }}</span>
      </div>

      <div v-if="successMessage" class="alert alert-success mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ successMessage }}</span>
      </div>

      <!-- Main Content -->
      <div class="grid lg:grid-cols-3 gap-6">
        <!-- Left: Voice List (1 column) -->
        <div class="lg:col-span-1">
          <VoiceList
            :voices="voices"
            :selected-voice="selectedVoice"
            :is-loading="isLoading"
            @select="handleSelectVoice"
            @reorder="handleReorder"
          />
        </div>

        <!-- Right: Voice Editor (2 columns) -->
        <div class="lg:col-span-2">
          <VoiceEditor
            v-if="selectedVoice"
            ref="voiceEditorRef"
            :voice="selectedVoice"
            :is-saving="isSaving"
            :is-testing="isTesting"
            @save="handleSaveVoice"
            @cancel="handleCancelEdit"
            @delete="handleDeleteVoice"
            @set-default="handleSetDefault"
            @test="handleTestVoice"
          />

          <!-- Empty State -->
          <div v-else class="card bg-base-100 shadow-xl">
            <div class="card-body items-center text-center py-16">
              <div class="text-6xl mb-4">👈</div>
              <h3 class="text-xl font-semibold text-base-content/70">
                Selecciona una voz
              </h3>
              <p class="text-base-content/50 mt-2">
                Elige una voz de la lista para ver y editar su configuración
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Add Voice Modal -->
      <VoiceAddModal
        v-if="showAddModal"
        @close="showAddModal = false"
        @create="handleCreateVoice"
      />

      <!-- Delete Confirmation Modal -->
      <dialog v-if="voiceToDelete" class="modal modal-open">
        <div class="modal-box">
          <h3 class="font-bold text-lg text-error">
            ⚠️ Confirmar Eliminación
          </h3>
          <p class="py-4">
            ¿Estás seguro de que quieres eliminar la voz
            <strong>"{{ voiceToDelete.name }}"</strong>?
          </p>
          <p class="text-sm text-base-content/60">
            Esta acción no se puede deshacer.
          </p>
          <div class="modal-action">
            <button
              class="btn btn-ghost"
              @click="voiceToDelete = null"
            >
              Cancelar
            </button>
            <button
              class="btn btn-error"
              @click="confirmDelete"
              :disabled="isSaving"
            >
              <span v-if="isSaving" class="loading loading-spinner loading-sm"></span>
              Eliminar
            </button>
          </div>
        </div>
        <form method="dialog" class="modal-backdrop">
          <button @click="voiceToDelete = null">close</button>
        </form>
      </dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useVoiceManager, type VoiceSettings } from './composables/useVoiceManager'
import VoiceList from './components/VoiceList.vue'
import VoiceEditor from './components/VoiceEditor.vue'
import VoiceAddModal from './components/VoiceAddModal.vue'

// Composable
const {
  voices,
  selectedVoice,
  isLoading,
  isSaving,
  isTesting,
  error,
  successMessage,
  loadVoices,
  selectVoice,
  createVoice,
  updateVoice,
  deleteVoice,
  setDefaultVoice,
  reorderVoices,
  testVoice,
} = useVoiceManager()

// Local state
const showAddModal = ref(false)
const voiceToDelete = ref<VoiceSettings | null>(null)
const voiceEditorRef = ref<InstanceType<typeof VoiceEditor> | null>(null)

// Handlers
const handleSelectVoice = (voice: VoiceSettings) => {
  selectVoice(voice)
}

const handleSaveVoice = async (updates: Partial<VoiceSettings>) => {
  if (!selectedVoice.value) return

  try {
    await updateVoice(selectedVoice.value.id, updates)
  } catch (e) {
    console.error('Failed to save voice:', e)
  }
}

const handleCancelEdit = () => {
  // Just reset the selection to trigger editor reset
  if (selectedVoice.value) {
    const voice = voices.value.find(v => v.id === selectedVoice.value?.id)
    if (voice) {
      selectVoice(voice)
    }
  }
}

const handleDeleteVoice = (voiceId: string) => {
  const voice = voices.value.find(v => v.id === voiceId)
  if (voice) {
    voiceToDelete.value = voice
  }
}

const confirmDelete = async () => {
  if (!voiceToDelete.value) return

  try {
    await deleteVoice(voiceToDelete.value.id)
    voiceToDelete.value = null
  } catch (e) {
    console.error('Failed to delete voice:', e)
  }
}

const handleSetDefault = async (voiceId: string) => {
  try {
    await setDefaultVoice(voiceId)
  } catch (e) {
    console.error('Failed to set default voice:', e)
  }
}

const handleReorder = async (newOrder: string[]) => {
  try {
    await reorderVoices(newOrder)
  } catch (e) {
    console.error('Failed to reorder voices:', e)
  }
}

const handleCreateVoice = async (voiceData: Partial<VoiceSettings>) => {
  try {
    const newVoice = await createVoice(voiceData)
    showAddModal.value = false
    if (newVoice) {
      selectVoice(newVoice)
    }
  } catch (e) {
    console.error('Failed to create voice:', e)
  }
}

const handleTestVoice = async (text: string) => {
  if (!selectedVoice.value) return

  try {
    const result = await testVoice(selectedVoice.value.id, text)
    if (result && voiceEditorRef.value) {
      voiceEditorRef.value.setTestAudioUrl(result.audio_url)
    }
  } catch (e) {
    console.error('Failed to test voice:', e)
  }
}

// Load voices on mount
onMounted(() => {
  loadVoices()
})
</script>
