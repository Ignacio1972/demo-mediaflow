<template>
  <div class="ai-suggestions">
    <div class="card bg-base-200 shadow-xl">
      <div class="card-body">
        <!-- Header -->
        <h2 class="card-title text-2xl mb-4">
          ¿Qué necesitas anunciar?
        </h2>

        <!-- Context Input -->
        <div class="form-control">
          <textarea
            v-model="context"
            class="textarea textarea-bordered h-24 font-mono"
            placeholder=""
            :disabled="isGenerating"
            maxlength="500"
          ></textarea>
        </div>

        <!-- Quick Configuration -->
        <div class="grid grid-cols-2 gap-4">
          <!-- Tone Selector -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Tono</span>
            </label>
            <select
              v-model="tone"
              class="select select-bordered"
              :disabled="isGenerating"
            >
              <option value="profesional">🎩 Profesional</option>
              <option value="entusiasta">🎉 Entusiasta</option>
              <option value="amigable">😊 Amigable</option>
              <option value="urgente">⚡ Urgente</option>
              <option value="informativo">📋 Informativo</option>
            </select>
          </div>

          <!-- Duration Selector -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Duración objetivo</span>
            </label>
            <select
              v-model="duration"
              class="select select-bordered"
              :disabled="isGenerating"
            >
              <option :value="5">5 segundos (~10 palabras)</option>
              <option :value="10">10 segundos (~20 palabras)</option>
              <option :value="15">15 segundos (~30 palabras)</option>
              <option :value="20">20 segundos (~40 palabras)</option>
              <option :value="25">25 segundos (~50 palabras)</option>
            </select>
          </div>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="alert alert-error mt-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ error }}</span>
          <button @click="clearError" class="btn btn-sm btn-ghost">✕</button>
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
              Generar Sugerencias con IA
            </span>
          </button>
        </div>

        <!-- Progress Info -->
        <div v-if="isGenerating" class="mt-4">
          <progress class="progress progress-primary w-full"></progress>
          <p class="text-sm text-center mt-2 opacity-70">
            Claude AI está generando sugerencias...
          </p>
        </div>

        <!-- Suggestions Panel -->
        <div v-if="suggestions.length > 0" class="mt-6">
          <div class="divider">Sugerencias Generadas</div>

          <div class="space-y-3">
            <div
              v-for="(suggestion, index) in suggestions"
              :key="index"
              class="card bg-base-300 hover:bg-base-100 transition-all cursor-pointer border-2"
              :class="selectedIndex === index ? 'border-primary' : 'border-transparent'"
              @click="selectSuggestion(index)"
            >
              <div class="card-body p-4">
                <!-- Suggestion Text -->
                <p class="text-base leading-relaxed">
                  {{ suggestion }}
                </p>

                <!-- Metadata -->
                <div class="flex items-center gap-4 text-xs opacity-70 mt-2">
                  <span class="flex items-center gap-1">
                    <DocumentTextIcon class="h-3 w-3" />
                    {{ countWords(suggestion) }} palabras
                  </span>
                  <span class="flex items-center gap-1">
                    <Bars3BottomLeftIcon class="h-3 w-3" />
                    {{ suggestion.length }} caracteres
                  </span>
                  <span class="flex items-center gap-1">
                    <ClockIcon class="h-3 w-3" />
                    ~{{ estimateDuration(suggestion) }}s
                  </span>
                </div>

                <!-- Actions -->
                <div class="card-actions justify-end mt-3">
                  <button
                    @click.stop="useSuggestion(suggestion)"
                    class="btn btn-primary btn-sm gap-2"
                  >
                    <CheckIcon class="h-4 w-4" />
                    Usar este texto
                  </button>
                  <button
                    @click.stop="copySuggestion(suggestion)"
                    class="btn btn-ghost btn-sm gap-2"
                  >
                    <ClipboardDocumentIcon class="h-4 w-4" />
                    Copiar
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Clear Button -->
          <div class="mt-4 text-center">
            <button
              @click="clearSuggestions"
              class="btn btn-ghost btn-sm gap-2"
            >
              <TrashIcon class="h-4 w-4" />
              Limpiar sugerencias
            </button>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="!isGenerating" class="mt-6 text-center opacity-50">
          <div class="text-6xl mb-2">💡</div>
          <p class="text-sm">Las sugerencias aparecerán aquí</p>
          <p class="text-xs mt-1">Completa el contexto y presiona "Generar"</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import audioApi from '@/api/audio'
import {
  SparklesIcon,
  DocumentTextIcon,
  Bars3BottomLeftIcon,
  ClockIcon,
  CheckIcon,
  ClipboardDocumentIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

// Emits
const emit = defineEmits<{
  suggestionSelected: [text: string]
}>()

// State
const context = ref('')
const tone = ref('profesional')
const duration = ref(15)
const suggestions = ref<string[]>([])
const selectedIndex = ref<number | null>(null)
const isGenerating = ref(false)
const error = ref<string | null>(null)

// Computed
const contextLength = computed(() => context.value.length)

const canGenerate = computed(() => {
  return context.value.trim().length > 0 && !isGenerating.value
})

// Tone mapping: Spanish UI -> English API
const toneMapping: Record<string, string> = {
  'profesional': 'professional',
  'entusiasta': 'friendly',
  'amigable': 'friendly',
  'urgente': 'urgent',
  'informativo': 'casual'
}

// Methods
const generateSuggestions = async () => {
  if (!canGenerate.value) return

  try {
    isGenerating.value = true
    error.value = null
    suggestions.value = []
    selectedIndex.value = null

    console.log('🤖 Generating AI suggestions...', {
      context: context.value,
      tone: tone.value,
      duration: duration.value
    })

    // Calculate max words based on duration
    // Aproximadamente 2 palabras por segundo
    const maxWords = Math.floor(duration.value * 2)

    // Map Spanish tone to English for API
    const apiTone = toneMapping[tone.value] || 'professional'

    const response = await audioApi.generateAISuggestions({
      prompt: context.value.trim(),    // Backend expects 'prompt', not 'context'
      context: context.value.trim(),   // Also send context for additional info
      tone: apiTone,                   // Use mapped English value
      max_words: maxWords
    })

    suggestions.value = response.suggestions || []

    console.log(`✅ Generated ${suggestions.value.length} suggestions`)

    // Auto-scroll to suggestions
    setTimeout(() => {
      const suggestionsPanel = document.querySelector('.ai-suggestions .space-y-3')
      if (suggestionsPanel) {
        suggestionsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
      }
    }, 100)

  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || 'Error generando sugerencias'
    console.error('❌ Error generating suggestions:', e)
  } finally {
    isGenerating.value = false
  }
}

const selectSuggestion = (index: number) => {
  selectedIndex.value = index
}

const useSuggestion = (text: string) => {
  emit('suggestionSelected', text)

  // Visual feedback
  const notification = document.createElement('div')
  notification.className = 'toast toast-top toast-end'
  notification.innerHTML = `
    <div class="alert alert-success">
      <span>✅ Texto copiado al generador</span>
    </div>
  `
  document.body.appendChild(notification)

  setTimeout(() => {
    notification.remove()
  }, 2000)
}

const copySuggestion = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)

    // Visual feedback
    const notification = document.createElement('div')
    notification.className = 'toast toast-top toast-end'
    notification.innerHTML = `
      <div class="alert alert-info">
        <span>📋 Copiado al portapapeles</span>
      </div>
    `
    document.body.appendChild(notification)

    setTimeout(() => {
      notification.remove()
    }, 2000)
  } catch (e) {
    console.error('Failed to copy:', e)
  }
}

const clearSuggestions = () => {
  suggestions.value = []
  selectedIndex.value = null
}

const clearError = () => {
  error.value = null
}

const countWords = (text: string): number => {
  return text.trim().split(/\s+/).length
}

const estimateDuration = (text: string): number => {
  // Aproximadamente 2 palabras por segundo
  const words = countWords(text)
  return Math.ceil(words / 2)
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
