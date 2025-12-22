<template>
  <div class="ai-suggestions">
    <div class="card bg-base-200 shadow-xl">
      <div class="card-body">
        <!-- Header -->
        <h2 class="card-title text-2xl mb-4">
          ¿Que quieres anunciar hoy?
        </h2>

        <!-- Context Input -->
        <div class="form-control">
          <textarea
            v-model="context"
            class="textarea textarea-bordered h-56"
            placeholder=""
            :disabled="isGenerating"
            maxlength="1000"
          ></textarea>
        </div>

        <!-- Advanced Settings Toggle -->
        <button
          @click="showAdvancedSettings = !showAdvancedSettings"
          class="flex items-center gap-1 text-sm opacity-60 hover:opacity-100 transition-opacity mt-2"
          :disabled="isGenerating"
        >
          <svg
            class="h-3 w-3 transition-transform duration-200"
            :class="{ 'rotate-90': showAdvancedSettings }"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M6 6L14 10L6 14V6Z" />
          </svg>
          <span>Opciones</span>
        </button>

        <!-- Collapsible Settings Panel -->
        <div
          class="settings-panel overflow-hidden transition-all duration-300 ease-in-out"
          :class="showAdvancedSettings ? 'max-h-40 opacity-100 mt-3' : 'max-h-0 opacity-0'"
        >
          <div class="grid grid-cols-2 gap-6">
            <!-- Tone Slider -->
            <div class="form-control">
              <label class="label py-1">
                <span class="label-text text-sm">Tono</span>
                <span class="label-text-alt text-xs">{{ toneLabels[toneIndex] }}</span>
              </label>
              <input
                type="range"
                v-model.number="toneIndex"
                min="0"
                max="4"
                step="1"
                class="range range-primary range-sm"
                :disabled="isGenerating"
              />
              <div class="flex justify-between px-1 mt-1">
                <span
                  v-for="(label, idx) in toneLabels"
                  :key="label"
                  class="text-[10px] opacity-50"
                  :class="{ 'opacity-100 font-medium': idx === toneIndex }"
                >|</span>
              </div>
            </div>

            <!-- Duration Slider -->
            <div class="form-control">
              <label class="label py-1">
                <span class="label-text text-sm">Duracion</span>
                <span class="label-text-alt text-xs">{{ duration }}s</span>
              </label>
              <input
                type="range"
                v-model.number="duration"
                min="5"
                max="25"
                step="5"
                class="range range-primary range-sm"
                :disabled="isGenerating"
              />
              <div class="flex justify-between px-1 mt-1">
                <span
                  v-for="val in [5, 10, 15, 20, 25]"
                  :key="val"
                  class="text-[10px] opacity-50"
                  :class="{ 'opacity-100 font-medium': val === duration }"
                >|</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="alert alert-error mt-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ error }}</span>
          <button @click="clearError" class="btn btn-sm btn-ghost">Cerrar</button>
        </div>

        <!-- Generate Button -->
        <div class="card-actions justify-end mt-4">
          <button
            @click="generateSuggestions"
            class="btn btn-primary btn-block"
            :disabled="!canGenerate"
          >
            <span v-if="isGenerating" class="loading loading-spinner"></span>
            <span v-else class="flex items-center gap-2">
              <SparklesIcon class="h-5 w-5" />
              Generar Sugerencias
            </span>
          </button>
        </div>

        <!-- Progress Info -->
        <div v-if="isGenerating" class="mt-4">
          <progress class="progress progress-primary w-full"></progress>
          <p class="text-sm text-center mt-2 opacity-70">
...haciendo la magia
          </p>
        </div>

        <!-- Suggestions Panel -->
        <div v-if="suggestions.length > 0" class="mt-6">
          <div class="divider">
            <span class="text-sm opacity-70">{{ suggestions.length }} sugerencias generadas</span>
          </div>

          <div class="space-y-3">
            <div
              v-for="(suggestion, index) in suggestions"
              :key="suggestion.id"
              class="card bg-base-300 hover:bg-base-100 transition-all cursor-pointer border-2"
              :class="selectedIndex === index ? 'border-primary' : 'border-transparent'"
              @click="selectSuggestion(index)"
            >
              <div class="card-body p-4">
                <!-- Suggestion Text -->
                <p class="text-base leading-relaxed">
                  {{ suggestion.text }}
                </p>

                <!-- Actions -->
                <div class="card-actions justify-end mt-3">
                  <button
                    @click.stop="useSuggestion(suggestion.text)"
                    class="btn btn-primary btn-sm gap-2"
                  >
                    <CheckIcon class="h-4 w-4" />
                    Usar este texto
                  </button>
                </div>
              </div>
            </div>
          </div>

        </div>

        <!-- Empty State -->
        <div v-else-if="!isGenerating" class="mt-6 text-center opacity-50">
          <div class="text-5xl mb-2">
            <SparklesIcon class="h-12 w-12 mx-auto" />
          </div>
          <p class="text-sm">Las sugerencias apareceran aqui</p>
          <p class="text-xs mt-1">Describe lo que quieres anunciar y presiona "Generar"</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import audioApi from '@/api/audio'
import { apiClient } from '@/api/client'
import type { AIAnnouncementSuggestion, AIGenerateRequest } from '@/types/audio'
import {
  SparklesIcon,
  CheckIcon
} from '@heroicons/vue/24/outline'

// Emits
const emit = defineEmits<{
  suggestionSelected: [text: string]
}>()

// Tone configuration (profesional in the middle at index 2)
const toneLabels = ['Amigable', 'Entusiasta', 'Profesional', 'Urgente', 'Informativo']
const toneValues: AIGenerateRequest['tone'][] = ['amigable', 'entusiasta', 'profesional', 'urgente', 'informativo']

// State
const context = ref('')
const toneIndex = ref(2) // Default: profesional (middle)
const duration = ref(10)
const suggestions = ref<AIAnnouncementSuggestion[]>([])
const selectedIndex = ref<number | null>(null)
const isGenerating = ref(false)
const error = ref<string | null>(null)
const activeClientName = ref<string | null>(null)
const showAdvancedSettings = ref(false)

// Computed tone value from index
const tone = computed(() => toneValues[toneIndex.value])

// Computed
const canGenerate = computed(() => {
  return !isGenerating.value
})

// Load active client info on mount
onMounted(async () => {
  try {
    const response = await apiClient.get<{ name: string; id: string }>('/api/v1/settings/ai-clients/active')
    activeClientName.value = response.name
  } catch (e) {
    // No active client or error - use default
    activeClientName.value = null
  }
})

// Methods
const generateSuggestions = async () => {
  if (!canGenerate.value) return

  try {
    isGenerating.value = true
    error.value = null
    suggestions.value = []
    selectedIndex.value = null

    console.log('Generating AI announcements...', {
      context: context.value,
      tone: tone.value,
      duration: duration.value
    })

    const response = await audioApi.generateAnnouncements({
      context: context.value.trim(),
      tone: tone.value,
      duration: duration.value,
      mode: 'normal'
    })

    if (response.success) {
      suggestions.value = response.suggestions
      // Update active client name if returned
      if (response.active_client_id) {
        // Client name should be fetched separately or cached
      }
      console.log(`Generated ${suggestions.value.length} suggestions`)
    } else {
      throw new Error('Error en la generacion')
    }

    // Auto-scroll to suggestions
    setTimeout(() => {
      const suggestionsPanel = document.querySelector('.ai-suggestions .space-y-3')
      if (suggestionsPanel) {
        suggestionsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
      }
    }, 100)

  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || 'Error generando sugerencias'
    console.error('Error generating suggestions:', e)
  } finally {
    isGenerating.value = false
  }
}

const selectSuggestion = (index: number) => {
  selectedIndex.value = index
}

const useSuggestion = (text: string) => {
  emit('suggestionSelected', text)
  showToast('Texto enviado al generador', 'success')
}

const clearError = () => {
  error.value = null
}

const showToast = (message: string, type: 'success' | 'info' | 'error') => {
  const notification = document.createElement('div')
  notification.className = 'toast toast-top toast-end'
  notification.innerHTML = `
    <div class="alert alert-${type}">
      <span>${message}</span>
    </div>
  `
  document.body.appendChild(notification)

  setTimeout(() => {
    notification.remove()
  }, 2000)
}
</script>

<style scoped>
.ai-suggestions {
  width: 100%;
}

/* Animation for suggestion cards */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.space-y-3 > div {
  animation: fadeInUp 0.3s ease-out;
}
</style>
