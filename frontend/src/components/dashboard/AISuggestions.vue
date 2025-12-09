<template>
  <div class="ai-suggestions">
    <div class="card bg-base-200 shadow-xl">
      <div class="card-body">
        <!-- Header with Active Client Badge -->
        <div class="flex items-center justify-between mb-4">
          <h2 class="card-title text-2xl">
            Generar Anuncios con IA
          </h2>
          <div
            v-if="activeClientName"
            class="badge badge-primary badge-outline gap-1"
            :title="'Usando contexto de: ' + activeClientName"
          >
            <CpuChipIcon class="h-3 w-3" />
            {{ activeClientName }}
          </div>
        </div>

        <!-- Context Input -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">Describe lo que quieres anunciar</span>
            <span class="label-text-alt">{{ context.length }} / 1000</span>
          </label>
          <textarea
            v-model="context"
            class="textarea textarea-bordered h-24"
            placeholder="Ej: Oferta de 2x1 en pizzas todos los martes, nuevo horario de atencion..."
            :disabled="isGenerating"
            maxlength="1000"
          ></textarea>
        </div>

        <!-- Quick Configuration -->
        <div class="grid grid-cols-2 gap-4 mt-2">
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
              <option value="profesional">Profesional</option>
              <option value="entusiasta">Entusiasta</option>
              <option value="amigable">Amigable</option>
              <option value="urgente">Urgente</option>
              <option value="informativo">Informativo</option>
            </select>
          </div>

          <!-- Duration Selector -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Duracion objetivo</span>
            </label>
            <select
              v-model="duration"
              class="select select-bordered"
              :disabled="isGenerating"
            >
              <option :value="5">5 segundos</option>
              <option :value="10">10 segundos</option>
              <option :value="15">15 segundos</option>
              <option :value="20">20 segundos</option>
              <option :value="25">25 segundos</option>
            </select>
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
            Claude AI esta generando sugerencias...
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

                <!-- Metadata -->
                <div class="flex items-center gap-4 text-xs opacity-70 mt-2">
                  <span class="flex items-center gap-1">
                    <DocumentTextIcon class="h-3 w-3" />
                    {{ suggestion.word_count }} palabras
                  </span>
                  <span class="flex items-center gap-1">
                    <Bars3BottomLeftIcon class="h-3 w-3" />
                    {{ suggestion.char_count }} caracteres
                  </span>
                  <span class="flex items-center gap-1">
                    <ClockIcon class="h-3 w-3" />
                    ~{{ estimateDuration(suggestion.word_count) }}s
                  </span>
                </div>

                <!-- Actions -->
                <div class="card-actions justify-end mt-3">
                  <button
                    @click.stop="useSuggestion(suggestion.text)"
                    class="btn btn-primary btn-sm gap-2"
                  >
                    <CheckIcon class="h-4 w-4" />
                    Usar este texto
                  </button>
                  <button
                    @click.stop="copySuggestion(suggestion.text)"
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
  DocumentTextIcon,
  Bars3BottomLeftIcon,
  ClockIcon,
  CheckIcon,
  ClipboardDocumentIcon,
  TrashIcon,
  CpuChipIcon
} from '@heroicons/vue/24/outline'

// Emits
const emit = defineEmits<{
  suggestionSelected: [text: string]
}>()

// State
const context = ref('')
const tone = ref<AIGenerateRequest['tone']>('profesional')
const duration = ref(15)
const suggestions = ref<AIAnnouncementSuggestion[]>([])
const selectedIndex = ref<number | null>(null)
const isGenerating = ref(false)
const error = ref<string | null>(null)
const activeClientName = ref<string | null>(null)

// Computed
const canGenerate = computed(() => {
  return context.value.trim().length >= 5 && !isGenerating.value
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

const copySuggestion = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    showToast('Copiado al portapapeles', 'info')
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

const estimateDuration = (wordCount: number): number => {
  // Aproximadamente 2 palabras por segundo
  return Math.ceil(wordCount / 2)
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
