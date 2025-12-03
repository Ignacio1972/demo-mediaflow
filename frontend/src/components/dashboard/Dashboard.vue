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
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAudioStore } from '@/stores/audio'
import { storeToRefs } from 'pinia'
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
