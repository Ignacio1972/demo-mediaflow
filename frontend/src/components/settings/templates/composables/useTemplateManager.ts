/**
 * Template Manager Composable
 * Handles all template CRUD operations and state management
 */
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'

// Template interface
export interface MessageTemplate {
  id: string
  name: string
  description: string | null
  template_text: string
  variables: string[]
  module: string
  order: number
  active: boolean
  is_default: boolean
  use_announcement_sound: boolean
  default_voice_id: string | null
  created_at?: string
  updated_at?: string
}

export interface TemplateCreate {
  id: string
  name: string
  description?: string
  template_text: string
  variables?: string[]
  module: string
  active?: boolean
  is_default?: boolean
  use_announcement_sound?: boolean
  default_voice_id?: string | null
}

export interface TemplateUpdate {
  name?: string
  description?: string
  template_text?: string
  variables?: string[]
  module?: string
  active?: boolean
  is_default?: boolean
  use_announcement_sound?: boolean
  default_voice_id?: string | null
  order?: number
}

export interface ModuleInfo {
  id: string
  name: string
  icon: string
  variables: string[]
}

export function useTemplateManager() {
  // State
  const templates = ref<MessageTemplate[]>([])
  const selectedTemplate = ref<MessageTemplate | null>(null)
  const isLoading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)
  const successMessage = ref<string | null>(null)
  const availableModules = ref<ModuleInfo[]>([])
  const selectedModule = ref<string | null>(null)

  // Computed
  const activeTemplates = computed(() => templates.value.filter(t => t.active))

  const sortedTemplates = computed(() =>
    [...templates.value].sort((a, b) => {
      // Sort by module first, then by order
      if (a.module !== b.module) {
        return a.module.localeCompare(b.module)
      }
      return a.order - b.order
    })
  )

  const filteredTemplates = computed(() => {
    if (!selectedModule.value) {
      return sortedTemplates.value
    }
    return sortedTemplates.value.filter(t => t.module === selectedModule.value)
  })

  const templatesByModule = computed(() => {
    const grouped: Record<string, MessageTemplate[]> = {}
    for (const template of sortedTemplates.value) {
      if (!grouped[template.module]) {
        grouped[template.module] = []
      }
      grouped[template.module].push(template)
    }
    return grouped
  })

  // Clear messages after delay
  const clearMessages = () => {
    setTimeout(() => {
      error.value = null
      successMessage.value = null
    }, 3000)
  }

  // Load all templates
  const loadTemplates = async (module?: string) => {
    isLoading.value = true
    error.value = null

    try {
      let url = '/api/v1/settings/templates'
      if (module) {
        url += `?module=${module}`
      }
      const response = await apiClient.get<MessageTemplate[]>(url)
      templates.value = response
      console.log(`✅ Loaded ${templates.value.length} templates`)
    } catch (e: any) {
      error.value = e.message || 'Error al cargar plantillas'
      console.error('❌ Failed to load templates:', e)
    } finally {
      isLoading.value = false
    }
  }

  // Load available modules
  const loadModules = async () => {
    try {
      const response = await apiClient.get<{
        modules: ModuleInfo[]
        available_modules: ModuleInfo[]
      }>('/api/v1/settings/templates/modules/list')
      availableModules.value = response.available_modules
    } catch (e: any) {
      console.error('Failed to load modules:', e)
    }
  }

  // Select a template for editing
  const selectTemplate = (template: MessageTemplate | null) => {
    selectedTemplate.value = template ? { ...template } : null
  }

  // Create new template
  const createTemplate = async (templateData: TemplateCreate): Promise<MessageTemplate | null> => {
    isSaving.value = true
    error.value = null

    try {
      const response = await apiClient.post<MessageTemplate>('/api/v1/settings/templates', templateData)
      templates.value.push(response)
      // Re-sort
      templates.value.sort((a, b) => {
        if (a.module !== b.module) return a.module.localeCompare(b.module)
        return a.order - b.order
      })
      successMessage.value = `Plantilla "${response.name}" creada exitosamente`
      clearMessages()
      return response
    } catch (e: any) {
      error.value = e.message || 'Error al crear plantilla'
      clearMessages()
      throw e
    } finally {
      isSaving.value = false
    }
  }

  // Update existing template
  const updateTemplate = async (templateId: string, updates: TemplateUpdate): Promise<MessageTemplate | null> => {
    isSaving.value = true
    error.value = null

    try {
      const response = await apiClient.patch<MessageTemplate>(`/api/v1/settings/templates/${templateId}`, updates)

      // Update in local array
      const index = templates.value.findIndex(t => t.id === templateId)
      if (index !== -1) {
        templates.value[index] = response
      }

      // If is_default changed, update other templates in same module
      if (updates.is_default === true) {
        templates.value.forEach(t => {
          if (t.module === response.module && t.id !== templateId) {
            t.is_default = false
          }
        })
      }

      // Update selected if it's the one being edited
      if (selectedTemplate.value?.id === templateId) {
        selectedTemplate.value = response
      }

      successMessage.value = `Plantilla "${response.name}" actualizada`
      clearMessages()
      return response
    } catch (e: any) {
      error.value = e.message || 'Error al actualizar plantilla'
      clearMessages()
      throw e
    } finally {
      isSaving.value = false
    }
  }

  // Delete template
  const deleteTemplate = async (templateId: string): Promise<boolean> => {
    isSaving.value = true
    error.value = null

    try {
      await apiClient.delete(`/api/v1/settings/templates/${templateId}`)

      // Remove from local array
      const template = templates.value.find(t => t.id === templateId)
      templates.value = templates.value.filter(t => t.id !== templateId)

      // Clear selection if deleted
      if (selectedTemplate.value?.id === templateId) {
        selectedTemplate.value = null
      }

      successMessage.value = `Plantilla "${template?.name}" eliminada`
      clearMessages()
      return true
    } catch (e: any) {
      error.value = e.message || 'Error al eliminar plantilla'
      clearMessages()
      throw e
    } finally {
      isSaving.value = false
    }
  }

  // Reorder templates
  const reorderTemplates = async (newOrder: string[]): Promise<void> => {
    error.value = null

    try {
      await apiClient.put('/api/v1/settings/templates/reorder', { template_ids: newOrder })

      // Update local order
      newOrder.forEach((id, index) => {
        const template = templates.value.find(t => t.id === id)
        if (template) {
          template.order = index
        }
      })

      // Re-sort
      templates.value.sort((a, b) => {
        if (a.module !== b.module) return a.module.localeCompare(b.module)
        return a.order - b.order
      })
    } catch (e: any) {
      error.value = e.message || 'Error al reordenar plantillas'
      clearMessages()
      throw e
    }
  }

  // Toggle template active status
  const toggleTemplateActive = async (templateId: string): Promise<void> => {
    const template = templates.value.find(t => t.id === templateId)
    if (!template) return

    await updateTemplate(templateId, { active: !template.active })
  }

  // Set template as default for module
  const setAsDefault = async (templateId: string): Promise<void> => {
    await updateTemplate(templateId, { is_default: true })
  }

  // Preview template with variables
  const previewTemplate = async (templateText: string, variables: Record<string, string>): Promise<{
    original: string
    rendered: string
    missing_variables: string[]
  }> => {
    try {
      const response = await apiClient.post<{
        original: string
        rendered: string
        missing_variables: string[]
      }>('/api/v1/settings/templates/preview', {
        template_text: templateText,
        variables,
      })
      return response
    } catch (e: any) {
      console.error('Failed to preview template:', e)
      throw e
    }
  }

  // Generate ID from name
  const generateIdFromName = (name: string): string => {
    return name
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '') // Remove accents
      .replace(/[^a-z0-9]+/g, '_')      // Replace non-alphanumeric with underscore
      .replace(/^_+|_+$/g, '')          // Trim underscores
      .substring(0, 50)                  // Max 50 chars
  }

  // Check if ID is available
  const isIdAvailable = (id: string): boolean => {
    return !templates.value.some(t => t.id === id)
  }

  // Extract variables from template text
  const extractVariables = (templateText: string): string[] => {
    const pattern = /\{([a-zA-Z_][a-zA-Z0-9_]*)\}/g
    const matches: string[] = []
    let match
    while ((match = pattern.exec(templateText)) !== null) {
      if (!matches.includes(match[1])) {
        matches.push(match[1])
      }
    }
    return matches
  }

  // Filter by module
  const filterByModule = (module: string | null) => {
    selectedModule.value = module
  }

  return {
    // State
    templates,
    selectedTemplate,
    isLoading,
    isSaving,
    error,
    successMessage,
    availableModules,
    selectedModule,

    // Computed
    activeTemplates,
    sortedTemplates,
    filteredTemplates,
    templatesByModule,

    // Actions
    loadTemplates,
    loadModules,
    selectTemplate,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    reorderTemplates,
    toggleTemplateActive,
    setAsDefault,
    previewTemplate,
    filterByModule,

    // Helpers
    generateIdFromName,
    isIdAvailable,
    extractVariables,
  }
}
