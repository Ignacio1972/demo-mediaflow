<template>
  <PasswordGate />
  <div class="min-h-screen bg-base-100">
    <NavigationHeader v-if="!isLandingPage" />
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import NavigationHeader from '@/components/common/NavigationHeader.vue'

const route = useRoute()
const isLandingPage = computed(() => route.path === '/landing')
import PasswordGate from '@/components/PasswordGate.vue'

onMounted(() => {
  console.log('🚀 MediaFlowDemo v2.1 Frontend Started')
})
</script>

<style scoped>
/* App-specific styles */
</style>
