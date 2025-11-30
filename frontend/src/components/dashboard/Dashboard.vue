<template>
  <div class="min-h-screen bg-base-100">
    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8 max-w-[1600px]">
      <div class="grid lg:grid-cols-5 gap-6">
        <!-- Left Column: AI + Message Generator (3/5) -->
        <div class="lg:col-span-3 space-y-6">
          <!-- Step 1: AI Suggestions -->
          <AISuggestions @suggestion-selected="handleSuggestionSelected" />

          <!-- Step 2 & 3: Message Generator + Audio Preview -->
          <MessageGenerator
            ref="messageGeneratorRef"
            @audio-generated="handleAudioGenerated"
          />

          <!-- Audio Preview (appears after generation) -->
          <AudioPreview :audio="currentAudio" />
        </div>

        <!-- Right Column: Recent Messages (2/5) -->
        <div class="lg:col-span-2">
          <RecentMessages />
        </div>
      </div>

      <!-- Features Info (Bottom) -->
      <div class="card bg-base-200 shadow-xl mt-6">
        <div class="card-body">
          <h3 class="card-title text-xl mb-4 flex items-center gap-2">
            <SparklesIcon class="h-6 w-6" />
            Workflow de Generación
          </h3>
          <div class="space-y-2">
            <div class="flex items-start gap-3">
              <span class="badge badge-primary badge-lg">1</span>
              <span class="text-sm"><strong>Sugerencias IA:</strong> Describe qué anunciar → Claude genera 2 opciones</span>
            </div>
            <div class="flex items-start gap-3">
              <span class="badge badge-secondary badge-lg">2</span>
              <span class="text-sm"><strong>Edición:</strong> Selecciona una sugerencia → Edita y mejora el texto</span>
            </div>
            <div class="flex items-start gap-3">
              <span class="badge badge-accent badge-lg">3</span>
              <span class="text-sm"><strong>Generación:</strong> Cuando estés listo → Genera audio TTS profesional</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAudioStore } from '@/stores/audio'
import { storeToRefs } from 'pinia'
import { SparklesIcon } from '@heroicons/vue/24/outline'
import AISuggestions from './AISuggestions.vue'
import MessageGenerator from './MessageGenerator.vue'
import AudioPreview from './AudioPreview.vue'
import RecentMessages from './RecentMessages.vue'

// Store
const audioStore = useAudioStore()
const { currentAudio } = storeToRefs(audioStore)

// Refs
const messageGeneratorRef = ref<InstanceType<typeof MessageGenerator> | null>(null)

// Event handlers
const handleSuggestionSelected = (text: string) => {
  console.log('📝 Suggestion selected, setting text in MessageGenerator:', text)

  // Set text in MessageGenerator
  if (messageGeneratorRef.value) {
    messageGeneratorRef.value.setMessageText(text)

    // Scroll to MessageGenerator
    setTimeout(() => {
      const messageGenElement = document.querySelector('.message-generator')
      if (messageGenElement) {
        messageGenElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }, 100)
  }
}

const handleAudioGenerated = (response: any) => {
  console.log('✅ Audio generated in Dashboard:', response)
  // Audio is already in store.currentAudio
}

onMounted(() => {
  console.log('📊 Dashboard Component Mounted')
})
</script>

<style scoped>
/* Dashboard specific styles */
</style>
