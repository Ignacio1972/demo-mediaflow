<script setup lang="ts">
import { inject } from 'vue'
import type { CampaignWorkflow } from '../composables/useCampaignWorkflow'
import { toneLabels } from '../composables/useCampaignWorkflow'

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
        :disabled="workflow.isGeneratingSuggestions.value"
      />

      <!-- Advanced Options Toggle -->
      <div class="mt-4">
        <button
          @click="workflow.showAdvancedOptions.value = !workflow.showAdvancedOptions.value"
          class="inline-flex items-center gap-2 text-sm text-base-content/60 hover:text-base-content transition-colors"
          :disabled="workflow.isGeneratingSuggestions.value"
        >
          <svg
            class="h-4 w-4 transition-transform duration-200"
            :class="{ 'rotate-180': workflow.showAdvancedOptions.value }"
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
          :class="workflow.showAdvancedOptions.value ? 'max-h-48 opacity-100 mt-5' : 'max-h-0 opacity-0'"
        >
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 sm:gap-8">
            <!-- Tone Selector -->
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <label class="text-sm font-medium">Tono</label>
                <span class="text-xs font-medium text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                  {{ toneLabels[workflow.toneIndex.value] }}
                </span>
              </div>
              <input
                type="range"
                v-model.number="workflow.toneIndex.value"
                min="0"
                max="4"
                step="1"
                class="range range-primary range-sm"
                :disabled="workflow.isGeneratingSuggestions.value"
              />
              <div class="flex justify-between text-[10px] text-base-content/40 px-0.5">
                <span v-for="label in toneLabels" :key="label">·</span>
              </div>
            </div>

            <!-- Duration Selector -->
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <label class="text-sm font-medium">Duracion</label>
                <span class="text-xs font-medium text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                  {{ workflow.duration.value }}s
                </span>
              </div>
              <input
                type="range"
                v-model.number="workflow.duration.value"
                min="5"
                max="25"
                step="5"
                class="range range-primary range-sm"
                :disabled="workflow.isGeneratingSuggestions.value"
              />
              <div class="flex justify-between text-[10px] text-base-content/40 px-0.5">
                <span v-for="val in [5, 10, 15, 20, 25]" :key="val">·</span>
              </div>
            </div>
          </div>
        </div>
      </div>

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
