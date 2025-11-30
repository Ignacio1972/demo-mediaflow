<template>
  <div class="flex flex-col items-center justify-center py-16 px-4">
    <div class="text-6xl mb-4">{{ icon }}</div>
    <h3 class="text-xl font-semibold text-base-content mb-2">{{ title }}</h3>
    <p class="text-base-content/60 text-center max-w-md mb-6">{{ description }}</p>

    <div v-if="showActions" class="flex gap-3">
      <button
        v-if="showUpload"
        class="btn btn-primary"
        @click="emit('upload')"
      >
        <ArrowUpTrayIcon class="h-5 w-5 mr-2" />
        Subir Audio
      </button>
      <button
        v-if="showGenerate"
        class="btn btn-secondary"
        @click="emit('generate')"
      >
        <SparklesIcon class="h-5 w-5 mr-2" />
        Generar con IA
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowUpTrayIcon, SparklesIcon } from '@heroicons/vue/24/outline'

withDefaults(defineProps<{
  icon?: string
  title?: string
  description?: string
  showActions?: boolean
  showUpload?: boolean
  showGenerate?: boolean
}>(), {
  icon: '📚',
  title: 'Biblioteca vacia',
  description: 'No hay mensajes guardados. Genera tu primer mensaje o sube un archivo de audio.',
  showActions: true,
  showUpload: true,
  showGenerate: true
})

const emit = defineEmits<{
  upload: []
  generate: []
}>()
</script>
