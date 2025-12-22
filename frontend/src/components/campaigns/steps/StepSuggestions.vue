<script setup lang="ts">
import { inject } from 'vue'
import type { CampaignWorkflow, Suggestion } from '../composables/useCampaignWorkflow'

// Inject workflow from CampaignDetail
const workflow = inject<CampaignWorkflow>('workflow')!

function handleUse(suggestion: Suggestion) {
  workflow.useSuggestion(suggestion)
}

function handleBack() {
  workflow.goToStep('input')
}
</script>

<template>
  <div class="space-y-4">
    <!-- Header with context -->
    <div class="card bg-base-200">
      <div class="card-body py-3">
        <div class="flex items-center justify-between">
          <div>
            <span class="text-sm opacity-50">Contexto:</span>
            <span class="ml-2 font-medium">{{ workflow.inputText.value }}</span>
          </div>
          <button class="btn btn-ghost btn-sm" @click="handleBack">
            Cambiar
          </button>
        </div>
      </div>
    </div>

    <!-- Suggestions divider -->
    <div class="divider">
      {{ workflow.suggestions.value.length }} sugerencias
    </div>

    <!-- Suggestion cards -->
    <div
      v-for="suggestion in workflow.suggestions.value"
      :key="suggestion.id"
      class="card bg-base-200 hover:bg-base-300 transition-colors"
    >
      <div class="card-body">
        <p class="text-lg leading-relaxed">
          "{{ suggestion.text }}"
        </p>

        <div class="card-actions justify-between items-center mt-4">
          <div class="text-sm opacity-50">
            {{ suggestion.char_count }} caracteres &middot; {{ suggestion.word_count }} palabras
          </div>

          <button
            class="btn btn-primary btn-sm"
            @click="handleUse(suggestion)"
          >
            Usar
          </button>
        </div>
      </div>
    </div>

    <!-- Request more -->
    <div class="text-center">
      <button
        class="btn btn-ghost btn-sm"
        :disabled="workflow.isGeneratingSuggestions.value"
        @click="workflow.requestSuggestions"
      >
        <span
          v-if="workflow.isGeneratingSuggestions.value"
          class="loading loading-spinner loading-xs"
        ></span>
        Generar mas sugerencias
      </button>
    </div>
  </div>
</template>
