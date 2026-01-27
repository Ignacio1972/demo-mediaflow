<template>
  <PasswordGate />
  <div class="min-h-screen bg-base-100 flex flex-col">
    <NavigationHeader v-if="!isLandingPage" />
    <router-view class="flex-1" />
    <!-- Global Footer -->
    <footer class="mt-auto py-4 text-center">
      <span class="text-xs text-base-content/50">
        Powered by <a href="https://mediaflow.cl/" target="_blank" class="hover:underline"><span style="color: #00adef">Media</span><span class="text-base-content/70">Flow</span></a>. Copyright 2026.
      </span>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import NavigationHeader from '@/components/common/NavigationHeader.vue'
import PasswordGate from '@/components/PasswordGate.vue'
import { isMobileDevice } from '@/composables/useMobileDevice'
import { useTenantStore } from '@/stores/tenant'

const route = useRoute()
const router = useRouter()
const tenantStore = useTenantStore()
const isLandingPage = computed(() => route.path === '/landing')

onMounted(async () => {
  // Load tenant configuration first
  await tenantStore.loadConfig()

  console.log(`MediaFlow v${tenantStore.appVersion} - ${tenantStore.tenantName}`)

  // Redirect mobile devices to landing page
  if (isMobileDevice() && route.path === '/') {
    router.replace('/landing')
  }
})
</script>

<style scoped>
/* App-specific styles */
</style>
