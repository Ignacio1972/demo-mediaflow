<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { CollapsiblePanel } from '@/components/shared/ui'

interface Props {
  campaignId: string
  initialInstructions: string | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  save: [instructions: string]
}>()

// State
const instructions = ref(props.initialInstructions || '')
const isSaving = ref(false)
const isDirty = computed(() =>
  instructions.value !== (props.initialInstructions || '')
)

// Sync with prop changes
watch(() => props.initialInstructions, (newVal) => {
  instructions.value = newVal || ''
})

// Preview text for collapsed state
const previewText = computed(() => {
  if (!props.initialInstructions) return 'Sin entrenamiento'
  const text = props.initialInstructions
  return text.length > 50 ? text.slice(0, 50) + '...' : text
})

// Save handler
async function handleSave() {
  if (!isDirty.value) return

  isSaving.value = true
  try {
    emit('save', instructions.value)
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <CollapsiblePanel
    title="Entrenamiento IA"
    icon="🧠"
    :preview="previewText"
    :default-expanded="!initialInstructions"
  >
    <div class="space-y-4">
      <p class="text-sm opacity-70">
        Instrucciones para la IA cuando genere sugerencias para esta campaña:
      </p>

      <textarea
        v-model="instructions"
        class="textarea textarea-bordered w-full h-32"
        placeholder="Ej: Usa un tono patriota y festivo. Menciona el 18 de septiembre. Incluye referencias a asados, empanadas y cueca..."
      />

      <div class="flex justify-end">
        <button
          class="btn btn-primary btn-sm"
          :class="{ 'btn-disabled': !isDirty }"
          :disabled="!isDirty || isSaving"
          @click="handleSave"
        >
          <span v-if="isSaving" class="loading loading-spinner loading-xs"></span>
          <template v-else>Guardar</template>
        </button>
      </div>
    </div>
  </CollapsiblePanel>
</template>
