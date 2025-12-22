import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Campaign, CampaignCreate, CampaignListResponse } from '@/types/campaign'
import { apiClient } from '@/api/client'

export const useCampaignStore = defineStore('campaigns', () => {
  // State
  const campaigns = ref<Campaign[]>([])
  const currentCampaign = ref<Campaign | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const activeCampaigns = computed(() =>
    campaigns.value.filter(c => c.active)
  )

  const campaignsWithTraining = computed(() =>
    campaigns.value.filter(c => c.has_ai_training)
  )

  const totalAudios = computed(() =>
    campaigns.value.reduce((sum, c) => sum + c.audio_count, 0)
  )

  // Actions
  async function fetchCampaigns() {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiClient.get<CampaignListResponse>('/api/v1/campaigns')
      campaigns.value = response.campaigns
    } catch (err) {
      error.value = 'Error al cargar campañas'
      console.error('fetchCampaigns error:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCampaign(id: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiClient.get<Campaign>(`/api/v1/campaigns/${id}`)
      currentCampaign.value = response
      return response
    } catch (err) {
      error.value = 'Campaña no encontrada'
      console.error('fetchCampaign error:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function createCampaign(data: CampaignCreate) {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiClient.post<Campaign>('/api/v1/campaigns', data)
      await fetchCampaigns() // Refresh list
      return response
    } catch (err) {
      error.value = 'Error al crear campaña'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateAITraining(id: string, instructions: string) {
    try {
      const response = await apiClient.patch<Campaign>(
        `/api/v1/campaigns/${id}`,
        { ai_instructions: instructions }
      )
      // Update local state
      if (currentCampaign.value?.id === id) {
        currentCampaign.value = response
      }
      const index = campaigns.value.findIndex(c => c.id === id)
      if (index !== -1) {
        campaigns.value[index] = response
      }
      return response
    } catch (err) {
      error.value = 'Error al guardar entrenamiento'
      throw err
    }
  }

  function clearCurrent() {
    currentCampaign.value = null
  }

  return {
    // State
    campaigns,
    currentCampaign,
    isLoading,
    error,
    // Getters
    activeCampaigns,
    campaignsWithTraining,
    totalAudios,
    // Actions
    fetchCampaigns,
    fetchCampaign,
    createCampaign,
    updateAITraining,
    clearCurrent
  }
})
