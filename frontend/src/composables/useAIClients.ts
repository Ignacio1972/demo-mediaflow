/**
 * AI Clients Composable
 * Manages AI client/context state and operations
 */
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'

export interface AIClient {
  id: string
  name: string
  context: string
  category: string
  active: boolean
  is_default: boolean
  order: number
  settings?: Record<string, any>
  custom_prompts?: Record<string, string>
  created_at?: string
  updated_at?: string
}

export interface AIClientListResponse {
  clients: AIClient[]
  active_client_id: string | null
  total: number
}

export function useAIClients() {
  const clients = ref<AIClient[]>([])
  const activeClientId = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const activeClient = computed(() =>
    clients.value.find(c => c.id === activeClientId.value)
  )

  const sortedClients = computed(() =>
    [...clients.value].sort((a, b) => a.order - b.order)
  )

  async function loadClients() {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.get<AIClientListResponse>('/api/v1/settings/ai-clients')
      clients.value = response.clients
      activeClientId.value = response.active_client_id
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message || 'Error loading clients'
      console.error('[useAIClients] Error:', e)
    } finally {
      isLoading.value = false
    }
  }

  async function setActiveClient(clientId: string): Promise<boolean> {
    try {
      await apiClient.post(`/api/v1/settings/ai-clients/active/${clientId}`)
      activeClientId.value = clientId
      // Update local state
      clients.value = clients.value.map(c => ({
        ...c,
        is_default: c.id === clientId
      }))
      return true
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message || 'Error setting active client'
      return false
    }
  }

  async function createClient(data: Partial<AIClient>): Promise<AIClient | null> {
    try {
      const response = await apiClient.post<AIClient>('/api/v1/settings/ai-clients', data)
      clients.value.push(response)
      return response
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message || 'Error creating client'
      throw e
    }
  }

  async function updateClient(clientId: string, data: Partial<AIClient>): Promise<AIClient | null> {
    try {
      const response = await apiClient.patch<AIClient>(`/api/v1/settings/ai-clients/${clientId}`, data)
      const index = clients.value.findIndex(c => c.id === clientId)
      if (index !== -1) {
        clients.value[index] = response
      }
      return response
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message || 'Error updating client'
      throw e
    }
  }

  async function deleteClient(clientId: string): Promise<boolean> {
    try {
      await apiClient.delete(`/api/v1/settings/ai-clients/${clientId}`)
      clients.value = clients.value.filter(c => c.id !== clientId)
      return true
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message || 'Error deleting client'
      return false
    }
  }

  async function reorderClients(clientIds: string[]): Promise<boolean> {
    try {
      await apiClient.put('/api/v1/settings/ai-clients/reorder', { client_ids: clientIds })
      // Update local order
      clientIds.forEach((id, index) => {
        const client = clients.value.find(c => c.id === id)
        if (client) client.order = index
      })
      return true
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message || 'Error reordering clients'
      return false
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    clients,
    activeClientId,
    activeClient,
    sortedClients,
    isLoading,
    error,

    // Actions
    loadClients,
    setActiveClient,
    createClient,
    updateClient,
    deleteClient,
    reorderClients,
    clearError
  }
}
