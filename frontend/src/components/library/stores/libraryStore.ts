import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AudioMessage, Category } from '@/types/audio'
import type { LibraryFilters, ViewMode } from '../types/library.types'
import { libraryApi } from '../services/libraryApi'

export const useLibraryStore = defineStore('library', () => {
  // State
  const messages = ref<AudioMessage[]>([])
  const categories = ref<Category[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const currentPage = ref(1)
  const perPage = ref(20)
  const viewMode = ref<ViewMode>('grid')

  const filters = ref<LibraryFilters>({
    search: '',
    category_id: null,
    is_favorite: null,
    sort_by: 'created_at',
    sort_order: 'desc',
    page: 1,
    per_page: 20
  })

  // Computed
  const totalPages = computed(() => Math.ceil(total.value / perPage.value))
  const hasNextPage = computed(() => currentPage.value < totalPages.value)
  const hasPrevPage = computed(() => currentPage.value > 1)
  const isEmpty = computed(() => messages.value.length === 0 && !isLoading.value)

  // Actions
  async function fetchMessages() {
    isLoading.value = true
    error.value = null

    try {
      const response = await libraryApi.getMessages(filters.value)
      messages.value = response.messages
      total.value = response.total
      currentPage.value = response.page
    } catch (err: any) {
      error.value = err.message || 'Error loading messages'
      console.error('[LibraryStore] fetchMessages error:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCategories() {
    try {
      categories.value = await libraryApi.getCategories()
    } catch (err: any) {
      console.error('[LibraryStore] fetchCategories error:', err)
    }
  }

  async function updateMessage(id: number, data: Partial<AudioMessage>) {
    try {
      const updated = await libraryApi.updateMessage(id, data)
      const index = messages.value.findIndex(m => m.id === id)
      if (index !== -1) {
        messages.value[index] = updated
      }
      return updated
    } catch (err: any) {
      error.value = err.message || 'Error updating message'
      throw err
    }
  }

  async function deleteMessage(id: number) {
    try {
      await libraryApi.deleteMessage(id)
      messages.value = messages.value.filter(m => m.id !== id)
      total.value = Math.max(0, total.value - 1)
    } catch (err: any) {
      error.value = err.message || 'Error deleting message'
      throw err
    }
  }

  async function deleteMessages(ids: number[]) {
    try {
      const result = await libraryApi.deleteMessages(ids)
      messages.value = messages.value.filter(m => !ids.includes(m.id))
      total.value = Math.max(0, total.value - result.deleted_count)
      return result
    } catch (err: any) {
      error.value = err.message || 'Error deleting messages'
      throw err
    }
  }

  async function toggleFavorite(id: number) {
    const message = messages.value.find(m => m.id === id)
    if (message) {
      return updateMessage(id, { is_favorite: !message.is_favorite })
    }
  }

  async function updateCategory(id: number, categoryId: string | null) {
    return updateMessage(id, { category_id: categoryId || undefined })
  }

  async function uploadAudio(file: File, displayName?: string) {
    isLoading.value = true
    try {
      const newMessage = await libraryApi.uploadAudio(file, displayName)
      messages.value.unshift(newMessage)
      total.value++
      return newMessage
    } catch (err: any) {
      error.value = err.message || 'Error uploading audio'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function sendToRadio(id: number) {
    try {
      return await libraryApi.sendToRadio(id)
    } catch (err: any) {
      error.value = err.message || 'Error sending to radio'
      throw err
    }
  }

  function setFilter<K extends keyof LibraryFilters>(key: K, value: LibraryFilters[K]) {
    filters.value[key] = value
    filters.value.page = 1 // Reset page on filter change
    fetchMessages()
  }

  function setFilters(newFilters: Partial<LibraryFilters>) {
    Object.assign(filters.value, newFilters)
    filters.value.page = 1
    fetchMessages()
  }

  function resetFilters() {
    filters.value = {
      search: '',
      category_id: null,
      is_favorite: null,
      sort_by: 'created_at',
      sort_order: 'desc',
      page: 1,
      per_page: 20
    }
    fetchMessages()
  }

  function nextPage() {
    if (hasNextPage.value) {
      filters.value.page++
      fetchMessages()
    }
  }

  function prevPage() {
    if (hasPrevPage.value) {
      filters.value.page--
      fetchMessages()
    }
  }

  function goToPage(page: number) {
    if (page >= 1 && page <= totalPages.value) {
      filters.value.page = page
      fetchMessages()
    }
  }

  function setViewMode(mode: ViewMode) {
    viewMode.value = mode
  }

  function clearError() {
    error.value = null
  }

  // Get category by ID
  function getCategoryById(id: string | null | undefined): Category | undefined {
    if (!id) return undefined
    return categories.value.find(c => c.id === id)
  }

  return {
    // State
    messages,
    categories,
    isLoading,
    error,
    total,
    currentPage,
    perPage,
    filters,
    viewMode,

    // Computed
    totalPages,
    hasNextPage,
    hasPrevPage,
    isEmpty,

    // Actions
    fetchMessages,
    fetchCategories,
    updateMessage,
    deleteMessage,
    deleteMessages,
    toggleFavorite,
    updateCategory,
    uploadAudio,
    sendToRadio,
    setFilter,
    setFilters,
    resetFilters,
    nextPage,
    prevPage,
    goToPage,
    setViewMode,
    clearError,
    getCategoryById
  }
})
