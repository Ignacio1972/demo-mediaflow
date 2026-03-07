<template>
  <PasswordGate />
  <div v-if="isLandingPage" class="min-h-screen bg-base-100 flex flex-col">
    <router-view class="flex-1" />
  </div>
  <div v-else class="min-h-screen bg-base-200">
    <AppHeader />
    <AppSidebar />
    <div class="lg:ml-64 pt-24 flex flex-col min-h-screen">
      <main class="flex-1 px-4 pb-4">
        <router-view />
      </main>
      <footer class="py-4 text-center">
        <span class="text-xs text-base-content/40">
          Powered by <a href="https://mediaflow.cl/" target="_blank" class="hover:underline"><span style="color: #00adef">Media</span><span class="text-base-content/60">Flow</span></a>
        </span>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import PasswordGate from '@/components/PasswordGate.vue'
import { isMobileDevice } from '@/composables/useMobileDevice'
import { useTenantStore } from '@/stores/tenant'

const route = useRoute()
const router = useRouter()
const tenantStore = useTenantStore()
const isLandingPage = computed(() => route.path === '/landing')

onMounted(async () => {
  await tenantStore.loadConfig()
  console.log(`MediaFlow v${tenantStore.appVersion} - ${tenantStore.tenantName}`)

  if (isMobileDevice() && route.path === '/') {
    router.replace('/campaigns')
  }
})
</script>

<style scoped>
/* App-specific styles */
</style>
