/**
 * AI Client Manager Composable
 * State management for AI Client settings UI
 */
import { ref, computed, onMounted } from 'vue'
import { apiClient } from '@/api/client'
import type { AIClient, AIClientListResponse } from '@/composables/useAIClients'

export function useAIClientManager() {
  // State
  const clients = ref<AIClient[]>([])
  const selectedClient = ref<AIClient | null>(null)
  const isLoading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)
  const successMessage = ref<string | null>(null)
  const activeClientId = ref<string | null>(null)

  // Computed
  const sortedClients = computed(() =>
    [...clients.value].sort((a, b) => a.order - b.order)
  )

  const activeClient = computed(() =>
    clients.value.find(c => c.id === activeClientId.value)
  )

  // Helper to clear messages after delay
  const clearMessages = () => {
    setTimeout(() => {
      error.value = null
      successMessage.value = null
    }, 3000)
  }

  // Load all clients
  async function loadClients() {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.get<AIClientListResponse>('/api/v1/settings/ai-clients')
      clients.value = response.clients
      activeClientId.value = response.active_client_id
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Error cargando clientes'
      clearMessages()
    } finally {
      isLoading.value = false
    }
  }

  // Select a client
  function selectClient(client: AIClient | null) {
    selectedClient.value = client ? { ...client } : null
  }

  // Create new client
  async function createClient(data: Partial<AIClient>): Promise<AIClient | null> {
    isSaving.value = true
    error.value = null

    try {
      const response = await apiClient.post<AIClient>('/api/v1/settings/ai-clients', data)
      clients.value.push(response)
      successMessage.value = `Cliente "${response.name}" creado exitosamente`
      clearMessages()
      return response
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Error creando cliente'
      clearMessages()
      throw e
    } finally {
      isSaving.value = false
    }
  }

  // Update existing client
  async function updateClient(clientId: string, data: Partial<AIClient>): Promise<AIClient | null> {
    isSaving.value = true
    error.value = null

    try {
      const response = await apiClient.patch<AIClient>(`/api/v1/settings/ai-clients/${clientId}`, data)
      const index = clients.value.findIndex(c => c.id === clientId)
      if (index !== -1) {
        clients.value[index] = response
      }
      // Update selected if it's the same
      if (selectedClient.value?.id === clientId) {
        selectedClient.value = response
      }
      successMessage.value = 'Cliente actualizado exitosamente'
      clearMessages()
      return response
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Error actualizando cliente'
      clearMessages()
      throw e
    } finally {
      isSaving.value = false
    }
  }

  // Delete client
  async function deleteClient(clientId: string): Promise<boolean> {
    isSaving.value = true
    error.value = null

    try {
      await apiClient.delete(`/api/v1/settings/ai-clients/${clientId}`)
      clients.value = clients.value.filter(c => c.id !== clientId)
      if (selectedClient.value?.id === clientId) {
        selectedClient.value = null
      }
      successMessage.value = 'Cliente eliminado exitosamente'
      clearMessages()
      return true
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Error eliminando cliente'
      clearMessages()
      return false
    } finally {
      isSaving.value = false
    }
  }

  // Set client as active/default
  async function setActiveClient(clientId: string): Promise<boolean> {
    isSaving.value = true
    error.value = null

    try {
      await apiClient.post(`/api/v1/settings/ai-clients/active/${clientId}`)
      activeClientId.value = clientId
      // Update local state
      clients.value = clients.value.map(c => ({
        ...c,
        is_default: c.id === clientId
      }))
      // Update selected if matches
      if (selectedClient.value?.id === clientId) {
        selectedClient.value = { ...selectedClient.value, is_default: true }
      }
      successMessage.value = 'Cliente activo actualizado'
      clearMessages()
      return true
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Error estableciendo cliente activo'
      clearMessages()
      return false
    } finally {
      isSaving.value = false
    }
  }

  // Reorder clients
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
      error.value = e.response?.data?.detail || 'Error reordenando clientes'
      clearMessages()
      return false
    }
  }

  return {
    // State
    clients,
    selectedClient,
    isLoading,
    isSaving,
    error,
    successMessage,
    activeClientId,

    // Computed
    sortedClients,
    activeClient,

    // Actions
    loadClients,
    selectClient,
    createClient,
    updateClient,
    deleteClient,
    setActiveClient,
    reorderClients
  }
}
