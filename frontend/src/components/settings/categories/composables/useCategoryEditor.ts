/**
 * Category Editor Composable
 * Handles all category CRUD operations and state management
 */
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'

// Category interface
export interface Category {
  id: string
  name: string
  icon: string | null
  color: string | null
  order: number
  active: boolean
  created_at?: string
  updated_at?: string
  message_count?: number
}

export interface CategoryCreate {
  id: string
  name: string
  icon?: string
  color?: string
  active?: boolean
}

export interface CategoryUpdate {
  name?: string
  icon?: string
  color?: string
  active?: boolean
  order?: number
}

export function useCategoryEditor() {
  // State
  const categories = ref<Category[]>([])
  const selectedCategory = ref<Category | null>(null)
  const isLoading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)
  const successMessage = ref<string | null>(null)

  // Computed
  const activeCategories = computed(() => categories.value.filter(c => c.active))
  const sortedCategories = computed(() => [...categories.value].sort((a, b) => a.order - b.order))

  // Clear messages after delay
  const clearMessages = () => {
    setTimeout(() => {
      error.value = null
      successMessage.value = null
    }, 3000)
  }

  // Load all categories
  const loadCategories = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.get<Category[]>('/api/v1/settings/categories')
      categories.value = response
      console.log(`✅ Loaded ${categories.value.length} categories`)
    } catch (e: any) {
      error.value = e.message || 'Error al cargar categorías'
      console.error('❌ Failed to load categories:', e)
    } finally {
      isLoading.value = false
    }
  }

  // Select a category for editing
  const selectCategory = (category: Category | null) => {
    selectedCategory.value = category ? { ...category } : null
  }

  // Create new category
  const createCategory = async (categoryData: CategoryCreate): Promise<Category | null> => {
    isSaving.value = true
    error.value = null

    try {
      const response = await apiClient.post<Category>('/api/v1/settings/categories', categoryData)
      categories.value.push(response)
      // Re-sort by order
      categories.value.sort((a, b) => a.order - b.order)
      successMessage.value = `Categoría "${response.name}" creada exitosamente`
      clearMessages()
      return response
    } catch (e: any) {
      error.value = e.message || 'Error al crear categoría'
      clearMessages()
      throw e
    } finally {
      isSaving.value = false
    }
  }

  // Update existing category
  const updateCategory = async (categoryId: string, updates: CategoryUpdate): Promise<Category | null> => {
    isSaving.value = true
    error.value = null

    try {
      const response = await apiClient.patch<Category>(`/api/v1/settings/categories/${categoryId}`, updates)

      // Update in local array
      const index = categories.value.findIndex(c => c.id === categoryId)
      if (index !== -1) {
        categories.value[index] = response
      }

      // Update selected if it's the one being edited
      if (selectedCategory.value?.id === categoryId) {
        selectedCategory.value = response
      }

      successMessage.value = `Categoría "${response.name}" actualizada`
      clearMessages()
      return response
    } catch (e: any) {
      error.value = e.message || 'Error al actualizar categoría'
      clearMessages()
      throw e
    } finally {
      isSaving.value = false
    }
  }

  // Delete category
  const deleteCategory = async (categoryId: string, force: boolean = false): Promise<boolean> => {
    isSaving.value = true
    error.value = null

    try {
      const url = force
        ? `/api/v1/settings/categories/${categoryId}?force=true`
        : `/api/v1/settings/categories/${categoryId}`

      await apiClient.delete(url)

      // Remove from local array
      const category = categories.value.find(c => c.id === categoryId)
      categories.value = categories.value.filter(c => c.id !== categoryId)

      // Clear selection if deleted
      if (selectedCategory.value?.id === categoryId) {
        selectedCategory.value = null
      }

      successMessage.value = `Categoría "${category?.name}" eliminada`
      clearMessages()
      return true
    } catch (e: any) {
      error.value = e.message || 'Error al eliminar categoría'
      clearMessages()
      throw e
    } finally {
      isSaving.value = false
    }
  }

  // Reorder categories
  const reorderCategories = async (newOrder: string[]): Promise<void> => {
    error.value = null

    try {
      await apiClient.put('/api/v1/settings/categories/reorder', { category_ids: newOrder })

      // Update local order
      newOrder.forEach((id, index) => {
        const category = categories.value.find(c => c.id === id)
        if (category) {
          category.order = index
        }
      })

      // Resort the array
      categories.value.sort((a, b) => a.order - b.order)
    } catch (e: any) {
      error.value = e.message || 'Error al reordenar categorías'
      clearMessages()
      throw e
    }
  }

  // Toggle category active status
  const toggleCategoryActive = async (categoryId: string): Promise<void> => {
    const category = categories.value.find(c => c.id === categoryId)
    if (!category) return

    await updateCategory(categoryId, { active: !category.active })
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
    return !categories.value.some(c => c.id === id)
  }

  return {
    // State
    categories,
    selectedCategory,
    isLoading,
    isSaving,
    error,
    successMessage,

    // Computed
    activeCategories,
    sortedCategories,

    // Actions
    loadCategories,
    selectCategory,
    createCategory,
    updateCategory,
    deleteCategory,
    reorderCategories,
    toggleCategoryActive,

    // Helpers
    generateIdFromName,
    isIdAvailable,
  }
}
