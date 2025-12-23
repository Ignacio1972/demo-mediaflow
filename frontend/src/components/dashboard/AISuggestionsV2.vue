<template>
  <div class="ai-suggestions-v2">
    <div class="card bg-base-100 border-2 border-base-300 rounded-2xl shadow-sm">
      <div class="card-body p-8">
        <!-- Header with title and subtitle -->
        <div class="mb-6">
          <h2 class="text-2xl font-bold tracking-tight">
            ¿Qué quieres anunciar?
          </h2>
          <p class="text-sm text-base-content/50 mt-1">
            Describe tu mensaje y la IA generará opciones para ti
          </p>
        </div>

        <!-- Context Input -->
        <div class="space-y-2">
          <textarea
            v-model="context"
            class="textarea bg-base-200/50 border-2 border-base-300 focus:border-primary focus:bg-base-100 rounded-xl w-full h-40 text-base leading-relaxed resize-none transition-all"
            placeholder="Ej: Promoción de tacos al pastor 2x1 los martes..."
            :disabled="isGenerating"
            maxlength="1000"
          ></textarea>
          <div class="flex justify-end">
            <span class="text-xs text-base-content/40">{{ context.length }}/1000</span>
          </div>
        </div>

        <!-- Options Panel (collapsible) -->
        <div class="mt-4">
          <button
            @click="showAdvancedSettings = !showAdvancedSettings"
            class="inline-flex items-center gap-2 text-sm text-base-content/60 hover:text-base-content transition-colors"
            :disabled="isGenerating"
          >
            <svg
              class="h-4 w-4 transition-transform duration-200"
              :class="{ 'rotate-180': showAdvancedSettings }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
            <span>Opciones avanzadas</span>
          </button>

          <!-- Collapsible Content -->
          <div
            class="overflow-hidden transition-all duration-300 ease-out"
            :class="showAdvancedSettings ? 'max-h-48 opacity-100 mt-5' : 'max-h-0 opacity-0'"
          >
            <div class="grid grid-cols-2 gap-8">
              <!-- Tone Selector -->
              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <label class="text-sm font-medium">Tono</label>
                  <span class="text-xs font-medium text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                    {{ toneLabels[toneIndex] }}
                  </span>
                </div>
                <input
                  type="range"
                  v-model.number="toneIndex"
                  min="0"
                  max="4"
                  step="1"
                  class="range range-primary range-sm"
                  :disabled="isGenerating"
                />
                <div class="flex justify-between text-[10px] text-base-content/40 px-0.5">
                  <span v-for="label in toneLabels" :key="label">·</span>
                </div>
              </div>

              <!-- Duration Selector -->
              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <label class="text-sm font-medium">Duración</label>
                  <span class="text-xs font-medium text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                    {{ duration }}s
                  </span>
                </div>
                <input
                  type="range"
                  v-model.number="duration"
                  min="5"
                  max="25"
                  step="5"
                  class="range range-primary range-sm"
                  :disabled="isGenerating"
                />
                <div class="flex justify-between text-[10px] text-base-content/40 px-0.5">
                  <span v-for="val in [5, 10, 15, 20, 25]" :key="val">·</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="alert bg-error/10 text-error border-0 mt-6 rounded-xl">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span class="text-sm">{{ error }}</span>
          <button @click="clearError" class="btn btn-ghost btn-sm btn-circle">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Generate Button -->
        <div class="mt-6">
          <button
            @click="generateSuggestions"
            class="btn btn-primary w-full h-12 rounded-xl text-base font-semibold shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 transition-all"
            :disabled="!canGenerate"
          >
            <span v-if="isGenerating" class="loading loading-spinner"></span>
            <template v-else>
              <SparklesIcon class="h-5 w-5" />
              <span>Generar Sugerencias</span>
            </template>
          </button>
        </div>

        <!-- Progress State -->
        <div v-if="isGenerating" class="mt-6 text-center">
          <div class="flex items-center justify-center gap-2 text-sm text-base-content/60">
            <span class="inline-block w-2 h-2 bg-primary rounded-full animate-pulse"></span>
            <span>Generando ideas...</span>
          </div>
        </div>

        <!-- Suggestions Results -->
        <div v-if="suggestions.length > 0" class="mt-8">
          <!-- Divider with count -->
          <div class="flex items-center gap-4 mb-6">
            <div class="h-px flex-1 bg-base-300"></div>
            <span class="text-xs font-medium text-base-content/50 uppercase tracking-wider">
              {{ suggestions.length }} sugerencias
            </span>
            <div class="h-px flex-1 bg-base-300"></div>
          </div>

          <!-- Suggestion Cards -->
          <div class="space-y-4">
            <div
              v-for="(suggestion, index) in suggestions"
              :key="suggestion.id"
              class="group relative bg-base-200/50 hover:bg-base-200 border-2 rounded-xl p-5 cursor-pointer transition-all duration-200"
              :class="selectedIndex === index
                ? 'border-primary bg-primary/5'
                : 'border-transparent hover:border-base-300'"
              @click="selectSuggestion(index)"
            >
              <!-- Selection indicator -->
              <div
                v-if="selectedIndex === index"
                class="absolute -left-px top-1/2 -translate-y-1/2 w-1 h-8 bg-primary rounded-r-full"
              ></div>

              <!-- Suggestion Text -->
              <p class="text-base leading-relaxed pr-24">
                {{ suggestion.text }}
              </p>

              <!-- Use Button (appears on hover or when selected) -->
              <button
                @click.stop="useSuggestion(suggestion.text)"
                class="absolute right-4 top-1/2 -translate-y-1/2 btn btn-primary btn-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"
                :class="{ 'opacity-100': selectedIndex === index }"
              >
                <CheckIcon class="h-4 w-4" />
                <span>Usar</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="!isGenerating" class="mt-8 py-8 text-center">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-base-200 rounded-2xl mb-4">
            <SparklesIcon class="h-8 w-8 text-base-content/30" />
          </div>
          <p class="text-sm text-base-content/50">Las sugerencias aparecerán aquí</p>
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
import { SparklesIcon, CheckIcon } from '@heroicons/vue/24/outline'

// Emits
const emit = defineEmits<{
  suggestionSelected: [text: string]
}>()

// Tone configuration
const toneLabels = ['Amigable', 'Entusiasta', 'Profesional', 'Urgente', 'Informativo']
const toneValues: AIGenerateRequest['tone'][] = ['amigable', 'entusiasta', 'profesional', 'urgente', 'informativo']

// State
const context = ref('')
const toneIndex = ref(2) // Default: profesional
const duration = ref(10)
const suggestions = ref<AIAnnouncementSuggestion[]>([])
const selectedIndex = ref<number | null>(null)
const isGenerating = ref(false)
const error = ref<string | null>(null)
const showAdvancedSettings = ref(false)

// Computed
const tone = computed(() => toneValues[toneIndex.value])
const canGenerate = computed(() => !isGenerating.value)

// Methods
const generateSuggestions = async () => {
  if (!canGenerate.value) return

  try {
    isGenerating.value = true
    error.value = null
    suggestions.value = []
    selectedIndex.value = null

    const response = await audioApi.generateAnnouncements({
      context: context.value.trim(),
      tone: tone.value,
      duration: duration.value,
      mode: 'normal'
    })

    if (response.success) {
      suggestions.value = response.suggestions
    } else {
      throw new Error('Error en la generación')
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || 'Error generando sugerencias'
  } finally {
    isGenerating.value = false
  }
}

const selectSuggestion = (index: number) => {
  selectedIndex.value = index
}

const useSuggestion = (text: string) => {
  emit('suggestionSelected', text)
  showToast('Texto enviado al generador')
}

const clearError = () => {
  error.value = null
}

const showToast = (message: string) => {
  const notification = document.createElement('div')
  notification.className = 'toast toast-top toast-end z-50'
  notification.innerHTML = `
    <div class="alert bg-success text-success-content shadow-lg">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
      <span class="text-sm font-medium">${message}</span>
    </div>
  `
  document.body.appendChild(notification)
  setTimeout(() => notification.remove(), 2500)
}
</script>

<style scoped>
.ai-suggestions-v2 {
  width: 100%;
}

/* Smooth animations for suggestion cards */
.space-y-4 > div {
  animation: fadeInUp 0.3s ease-out backwards;
}

.space-y-4 > div:nth-child(1) { animation-delay: 0ms; }
.space-y-4 > div:nth-child(2) { animation-delay: 75ms; }
.space-y-4 > div:nth-child(3) { animation-delay: 150ms; }
.space-y-4 > div:nth-child(4) { animation-delay: 225ms; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
