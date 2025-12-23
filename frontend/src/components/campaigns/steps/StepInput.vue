<script setup lang="ts">
import { inject } from 'vue'
import type { CampaignWorkflow } from '../composables/useCampaignWorkflow'

// Inject workflow from CampaignDetail
const workflow = inject<CampaignWorkflow>('workflow')!
</script>

<template>
  <div class="card bg-base-200">
    <div class="card-body">
      <h2 class="card-title">Crear Nuevo Anuncio</h2>

      <p class="text-sm opacity-70 mb-4">
        Describe brevemente que quieres anunciar y la IA generara sugerencias de texto profesional.
      </p>

      <textarea
        v-model="workflow.inputText.value"
        class="textarea textarea-bordered w-full h-28"
        placeholder="Ej: ofertas de carne para asado
Ej: promocion 2x1 en bebidas
Ej: llegaron productos nuevos

(Opcional: deja vacio para sugerencia general)"
      />

      <!-- Error message -->
      <div v-if="workflow.suggestionsError.value" class="alert alert-error mt-4">
        {{ workflow.suggestionsError.value }}
      </div>

      <!-- Actions -->
      <div class="flex justify-between items-center mt-4">
        <div class="text-sm opacity-50">
          <template v-if="workflow.hasInputText.value">
            Se generaran sugerencias basadas en tu descripcion
          </template>
          <template v-else-if="workflow.campaignName.value">
            Se generara una sugerencia general para "{{ workflow.campaignName.value }}"
          </template>
          <template v-else>
            Escribe algo o espera a que cargue la campana
          </template>
        </div>

        <button
          class="btn btn-primary"
          :disabled="!workflow.canRequestSuggestions.value"
          @click="workflow.requestSuggestions"
        >
          <span
            v-if="workflow.isGeneratingSuggestions.value"
            class="loading loading-spinner loading-sm"
          ></span>
          Pedir Sugerencia
        </button>
      </div>
    </div>
  </div>
</template>
