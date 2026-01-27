/**
 * Tenant Store - Pinia
 * Manages tenant configuration for multi-tenant branding
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'

export interface TenantConfig {
  tenant_id: string
  tenant_name: string
  tenant_logo: string
  tenant_primary_color: string
  tenant_secondary_color: string
  tenant_domain: string
  tenant_favicon: string
  app_version: string
}

const DEFAULT_CONFIG: TenantConfig = {
  tenant_id: 'demo',
  tenant_name: 'MediaFlow Demo',
  tenant_logo: '/images/mediaflow-logo.png',
  tenant_primary_color: '#4F46E5',
  tenant_secondary_color: '#7C3AED',
  tenant_domain: 'localhost',
  tenant_favicon: '/favicon.ico',
  app_version: '2.1.0'
}

export const useTenantStore = defineStore('tenant', () => {
  // State
  const config = ref<TenantConfig>(DEFAULT_CONFIG)
  const isLoaded = ref(false)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const tenantName = computed(() => config.value.tenant_name)
  const tenantLogo = computed(() => config.value.tenant_logo)
  const tenantId = computed(() => config.value.tenant_id)
  const primaryColor = computed(() => config.value.tenant_primary_color)
  const secondaryColor = computed(() => config.value.tenant_secondary_color)
  const appVersion = computed(() => config.value.app_version)

  // Actions

  /**
   * Load tenant configuration from API
   */
  async function loadConfig() {
    if (isLoaded.value) {
      console.log('Tenant config already loaded')
      return config.value
    }

    try {
      isLoading.value = true
      error.value = null

      console.log('Loading tenant configuration...')
      const response = await apiClient.get<TenantConfig>('/api/v1/config/tenant')

      config.value = response
      isLoaded.value = true

      // Apply branding
      applyBranding()

      console.log(`Tenant loaded: ${config.value.tenant_name}`)
      return config.value
    } catch (e: any) {
      error.value = `Failed to load tenant config: ${e.message}`
      console.error('Error loading tenant config:', e)
      // Use default config on error
      config.value = DEFAULT_CONFIG
      isLoaded.value = true
      return config.value
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Apply tenant branding to the page
   */
  function applyBranding() {
    // Update document title
    document.title = config.value.tenant_name

    // Update favicon
    const faviconLink = document.querySelector<HTMLLinkElement>('link[rel="icon"]')
    if (faviconLink) {
      faviconLink.href = config.value.tenant_favicon
    }

    // Apply CSS custom properties for colors
    const root = document.documentElement
    root.style.setProperty('--tenant-primary-color', config.value.tenant_primary_color)
    root.style.setProperty('--tenant-secondary-color', config.value.tenant_secondary_color)

    console.log('Branding applied:', {
      name: config.value.tenant_name,
      primaryColor: config.value.tenant_primary_color
    })
  }

  /**
   * Reset to default configuration
   */
  function resetConfig() {
    config.value = DEFAULT_CONFIG
    isLoaded.value = false
    error.value = null
  }

  return {
    // State
    config,
    isLoaded,
    isLoading,
    error,

    // Computed
    tenantName,
    tenantLogo,
    tenantId,
    primaryColor,
    secondaryColor,
    appVersion,

    // Actions
    loadConfig,
    applyBranding,
    resetConfig
  }
})
