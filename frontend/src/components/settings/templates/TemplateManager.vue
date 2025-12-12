<template>
  <div class="template-manager min-h-screen bg-base-100">
    <SettingsNav />
    <div class="p-6">
      <div class="container mx-auto max-w-7xl">
        <!-- Header -->
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h1 class="text-3xl font-bold text-primary flex items-center gap-3">
              <span class="text-4xl">📝</span>
              Plantillas
            </h1>
            <p class="text-sm text-base-content/60 mt-1">
              Gestiona las plantillas de mensajes para anuncios TTS
            </p>
          </div>
          <button
            @click="showAddModal = true"
            class="btn btn-primary"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Nueva Plantilla
          </button>
        </div>

        <!-- Toast Messages -->
        <div v-if="error" class="alert alert-error mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ error }}</span>
        </div>

        <div v-if="successMessage" class="alert alert-success mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ successMessage }}</span>
        </div>

        <!-- Main Content -->
        <div class="grid lg:grid-cols-3 gap-6">
          <!-- Left: Template List (1 column) -->
          <div class="lg:col-span-1">
            <TemplateList
              :templates="filteredTemplates"
              :selected-template="selectedTemplate"
              :is-loading="isLoading"
              :available-modules="availableModules"
              :selected-module="selectedModule"
              @select="handleSelectTemplate"
              @filter-module="filterByModule"
            />
          </div>

          <!-- Right: Template Form (2 columns) -->
          <div class="lg:col-span-2">
            <TemplateForm
              v-if="selectedTemplate"
              :template="selectedTemplate"
              :is-saving="isSaving"
              :available-modules="availableModules"
              @save="handleSaveTemplate"
              @cancel="handleCancelEdit"
              @delete="handleDeleteTemplate"
              @set-default="handleSetDefault"
            />

            <!-- Empty State -->
            <div v-else class="card bg-base-100 shadow-xl">
              <div class="card-body items-center text-center py-16">
                <div class="text-6xl mb-4">👈</div>
                <h3 class="text-xl font-semibold text-base-content/70">
                  Selecciona una plantilla
                </h3>
                <p class="text-base-content/50 mt-2">
                  Elige una plantilla de la lista para editarla o crea una nueva
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Add Template Modal -->
        <TemplateAddModal
          v-if="showAddModal"
          :existing-ids="existingIds"
          :available-modules="availableModules"
          @close="showAddModal = false"
          @create="handleCreateTemplate"
        />

        <!-- Delete Confirmation Modal -->
        <dialog v-if="templateToDelete" class="modal modal-open">
          <div class="modal-box">
            <h3 class="font-bold text-lg text-error">
              Confirmar Eliminacion
            </h3>
            <p class="py-4">
              Estas seguro de que quieres eliminar la plantilla
              <strong>"{{ templateToDelete.name }}"</strong>?
            </p>

            <div v-if="templateToDelete.is_default" class="alert alert-warning mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>
                Esta es la plantilla por defecto del modulo.
                Se asignara otra plantilla como predeterminada.
              </span>
            </div>

            <div class="modal-action">
              <button
                class="btn btn-ghost"
                @click="templateToDelete = null"
              >
                Cancelar
              </button>
              <button
                class="btn btn-error"
                @click="confirmDelete"
                :disabled="isSaving"
              >
                <span v-if="isSaving" class="loading loading-spinner loading-sm"></span>
                Eliminar
              </button>
            </div>
          </div>
          <form method="dialog" class="modal-backdrop">
            <button @click="templateToDelete = null">close</button>
          </form>
        </dialog>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTemplateManager, type MessageTemplate, type TemplateUpdate } from './composables/useTemplateManager'
import TemplateList from './components/TemplateList.vue'
import TemplateForm from './components/TemplateForm.vue'
import TemplateAddModal from './components/TemplateAddModal.vue'
import SettingsNav from '../SettingsNav.vue'

// Composable
const {
  templates,
  selectedTemplate,
  isLoading,
  isSaving,
  error,
  successMessage,
  availableModules,
  selectedModule,
  filteredTemplates,
  loadTemplates,
  loadModules,
  selectTemplate,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  setAsDefault,
  filterByModule,
} = useTemplateManager()

// Local state
const showAddModal = ref(false)
const templateToDelete = ref<MessageTemplate | null>(null)

// Computed
const existingIds = computed(() => templates.value.map(t => t.id))

// Handlers
const handleSelectTemplate = (template: MessageTemplate) => {
  selectTemplate(template)
}

const handleSaveTemplate = async (updates: TemplateUpdate) => {
  if (!selectedTemplate.value) return

  try {
    await updateTemplate(selectedTemplate.value.id, updates)
  } catch (e) {
    console.error('Failed to save template:', e)
  }
}

const handleCancelEdit = () => {
  if (selectedTemplate.value) {
    const template = templates.value.find(t => t.id === selectedTemplate.value?.id)
    if (template) {
      selectTemplate(template)
    }
  }
}

const handleDeleteTemplate = (templateId: string) => {
  const template = templates.value.find(t => t.id === templateId)
  if (template) {
    templateToDelete.value = template
  }
}

const confirmDelete = async () => {
  if (!templateToDelete.value) return

  try {
    await deleteTemplate(templateToDelete.value.id)
    templateToDelete.value = null
  } catch (e) {
    console.error('Failed to delete template:', e)
  }
}

const handleSetDefault = async (templateId: string) => {
  try {
    await setAsDefault(templateId)
  } catch (e) {
    console.error('Failed to set default:', e)
  }
}

const handleCreateTemplate = async (templateData: any) => {
  try {
    const newTemplate = await createTemplate(templateData)
    showAddModal.value = false
    if (newTemplate) {
      selectTemplate(newTemplate)
    }
  } catch (e) {
    console.error('Failed to create template:', e)
  }
}

// Load data on mount
onMounted(async () => {
  await Promise.all([
    loadTemplates(),
    loadModules(),
  ])
})
</script>
