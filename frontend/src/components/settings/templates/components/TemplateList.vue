<template>
  <div class="template-list">
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-lg mb-4">
          Plantillas
          <span class="badge badge-ghost">{{ templates.length }}</span>
        </h2>

        <!-- Module Filter -->
        <div class="mb-4">
          <select
            :value="selectedModule || ''"
            @change="$emit('filter-module', ($event.target as HTMLSelectElement).value || null)"
            class="select select-bordered select-sm w-full"
          >
            <option value="">Todos los modulos</option>
            <option
              v-for="mod in availableModules"
              :key="mod.id"
              :value="mod.id"
            >
              {{ mod.icon }} {{ mod.name }}
            </option>
          </select>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="space-y-3">
          <div v-for="i in 3" :key="i" class="skeleton h-16 w-full"></div>
        </div>

        <!-- Empty State -->
        <div v-else-if="templates.length === 0" class="text-center py-8">
          <div class="text-4xl mb-2">📭</div>
          <p class="text-base-content/60">
            No hay plantillas
          </p>
          <p class="text-sm text-base-content/40 mt-1">
            Crea una nueva plantilla para comenzar
          </p>
        </div>

        <!-- Template List -->
        <div v-else class="space-y-2">
          <div
            v-for="template in templates"
            :key="template.id"
            @click="$emit('select', template)"
            class="template-item p-3 rounded-lg cursor-pointer transition-all"
            :class="{
              'bg-primary/10 border-2 border-primary': selectedTemplate?.id === template.id,
              'bg-base-200 hover:bg-base-300 border-2 border-transparent': selectedTemplate?.id !== template.id,
              'opacity-50': !template.active
            }"
          >
            <div class="flex items-start gap-3">
              <!-- Module Icon -->
              <div class="text-2xl">
                {{ getModuleIcon(template.module) }}
              </div>

              <!-- Template Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="font-medium truncate">{{ template.name }}</span>
                  <span
                    v-if="template.is_default"
                    class="badge badge-primary badge-xs"
                  >
                    Default
                  </span>
                  <span
                    v-if="template.use_announcement_sound"
                    class="badge badge-warning badge-xs"
                    title="Sonido de anuncio activado"
                  >
                    Anuncio
                  </span>
                  <span
                    v-if="!template.active"
                    class="badge badge-ghost badge-xs"
                  >
                    Inactiva
                  </span>
                </div>
                <div class="text-xs text-base-content/60 mt-1">
                  {{ template.description || 'Sin descripcion' }}
                </div>
                <div class="flex flex-wrap gap-1 mt-2">
                  <span
                    v-for="variable in template.variables.slice(0, 3)"
                    :key="variable"
                    class="badge badge-outline badge-xs"
                  >
                    {{ variable }}
                  </span>
                  <span
                    v-if="template.variables.length > 3"
                    class="badge badge-ghost badge-xs"
                  >
                    +{{ template.variables.length - 3 }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { MessageTemplate, ModuleInfo } from '../composables/useTemplateManager'

interface Props {
  templates: MessageTemplate[]
  selectedTemplate: MessageTemplate | null
  isLoading: boolean
  availableModules: ModuleInfo[]
  selectedModule: string | null
}

const props = defineProps<Props>()

defineEmits<{
  (e: 'select', template: MessageTemplate): void
  (e: 'filter-module', module: string | null): void
}>()

// Get icon for module
const getModuleIcon = (moduleId: string): string => {
  const mod = props.availableModules.find(m => m.id === moduleId)
  return mod?.icon || '📝'
}
</script>

<style scoped>
.template-item {
  border-style: solid;
}
</style>
