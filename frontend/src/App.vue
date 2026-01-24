<template>
  <PasswordGate />
  <div class="min-h-screen bg-base-100">
    <NavigationHeader v-if="!isLandingPage" />
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import NavigationHeader from '@/components/common/NavigationHeader.vue'
import PasswordGate from '@/components/PasswordGate.vue'
import { isMobileDevice } from '@/composables/useMobileDevice'

const route = useRoute()
const router = useRouter()
const isLandingPage = computed(() => route.path === '/landing')

onMounted(() => {
  console.log('🚀 MediaFlowDemo v2.1 Frontend Started')

  // Redirect mobile devices to landing page
  if (isMobileDevice() && route.path === '/') {
    router.replace('/landing')
  }
})
</script>

<style scoped>
/* App-specific styles */
</style>
